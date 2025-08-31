"""
Tests for object configuration schema validation functionality.

Also Tests for the object configuration promotion logic.

This module consolidates tests for the promote_config functionality
used by the object_config_router, covering both agent and rule configurations.
"""

from uuid import uuid4

import pytest
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from planar.ai.agent import Agent
from planar.ai.agent_utils import agent_configuration
from planar.ai.models import AgentConfig
from planar.object_config import (
    DEFAULT_UUID,
    ConfigNotFoundError,
    ConfigurableObjectType,
    ObjectConfiguration,
    ObjectConfigurationIO,
)
from planar.object_registry import ObjectRegistry
from planar.rules.models import Rule, RuleEngineConfig, create_jdm_graph
from planar.rules.rule_configuration import rule_configuration


@pytest.fixture
def rule_definition():
    class RuleInputOutput(BaseModel):
        test: str

    return Rule(
        name="test_rule_promote_success",
        description="Test rule for promoting configuration",
        input=RuleInputOutput,
        output=RuleInputOutput,
    )


@pytest.fixture
def agent_definition():
    class AgentInputOutput(BaseModel):
        test: str

    return Agent(
        name="test_agent_promote_success",
        system_prompt="Test agent for promoting configuration",
        user_prompt="Test agent for promoting configuration",
        model="gpt-4",
        max_turns=1,
    )


class ConfigV1(BaseModel):
    """Version 1 of a test configuration schema."""

    name: str
    value: int


@pytest.fixture
def config_io_v1():
    """Configuration IO for version 1 schema."""
    return ObjectConfigurationIO(ConfigV1, ConfigurableObjectType.RULE)


async def test_schema_validation_success(session: AsyncSession, config_io_v1):
    """Test that valid configurations are loaded"""
    # Write a valid V1 configuration
    config_v1 = ConfigV1(name="test", value=42)
    await config_io_v1.write_config("test_object", config_v1)

    # Read it back with validation
    result = await config_io_v1._read_configs("test_object")

    assert len(result) == 1
    assert result[0].data.name == "test"
    assert result[0].data.value == 42


async def test_no_config_returns_empty_list(session: AsyncSession, config_io_v1):
    """Test that non-existent configurations return empty list"""
    result = await config_io_v1._read_configs("nonexistent_object")

    assert len(result) == 0


async def test_multiple_versions_ordered_by_version_desc(
    session: AsyncSession, config_io_v1
):
    """Test that multiple configurations are returned ordered by version descending."""
    # Write multiple configurations
    config_v1_1 = ConfigV1(name="test1", value=1)
    config_v1_2 = ConfigV1(name="test2", value=2)
    config_v1_3 = ConfigV1(name="test3", value=3)

    await config_io_v1.write_config("test_object", config_v1_1)
    await config_io_v1.write_config("test_object", config_v1_2)
    await config_io_v1.write_config("test_object", config_v1_3)

    # Read all configurations
    result = await config_io_v1._read_configs("test_object")

    # Should have 3 configurations, ordered by version descending
    assert len(result) == 3
    assert result[0].version == 3  # Latest version first
    assert result[0].data.name == "test3"
    assert result[1].version == 2
    assert result[1].data.name == "test2"
    assert result[2].version == 1  # Oldest version last
    assert result[2].data.name == "test1"


@pytest.mark.asyncio
class TestPromoteConfigurationLogic:
    """Test the promote configuration logic for agents and rules."""

    async def test_promote_rule_config_success(
        self, session: AsyncSession, rule_definition: Rule
    ):
        """Test promoting a rule configuration successfully."""
        ObjectRegistry.get_instance().register(rule_definition)

        rule_config = RuleEngineConfig(jdm=create_jdm_graph(rule_definition))
        config = await rule_configuration.write_config(
            rule_definition.name, rule_config
        )

        await rule_configuration.promote_config(config.id)

        configs = await rule_configuration.read_configs_with_default(
            rule_definition.name, rule_definition.to_config()
        )

        assert len(configs) == 2
        assert configs[0].active is True
        assert configs[0].version == 1

        # last config is default
        assert configs[1].active is False
        assert configs[1].version == 0

        db_config = (
            await session.exec(
                select(ObjectConfiguration).where(ObjectConfiguration.id == config.id)
            )
        ).first()
        assert db_config is not None
        assert db_config.active is True

    async def test_promote_agent_config_success(
        self, session: AsyncSession, agent_definition: Agent
    ):
        """Test promoting an agent configuration successfully."""
        object_name = f"test_agent_promote_success_{uuid4().hex}"
        agent_config = AgentConfig(
            system_prompt="Sys", user_prompt="User", model="gpt-4", max_turns=1
        )
        config = await agent_configuration.write_config(object_name, agent_config)

        await agent_configuration.promote_config(config.id)

        configs = await agent_configuration.read_configs_with_default(
            object_name, agent_definition.to_config()
        )

        assert len(configs) == 2
        assert configs[0].active is True
        assert configs[0].id == config.id

        db_config = (
            await session.exec(
                select(ObjectConfiguration).where(ObjectConfiguration.id == config.id)
            )
        ).first()
        assert db_config is not None
        assert db_config.active is True

    async def test_promote_switches_active_rule_configs(
        self, session: AsyncSession, rule_definition: Rule
    ):
        """Test that promoting a rule config switches active status correctly."""
        ObjectRegistry.get_instance().register(rule_definition)

        jdm_graph = create_jdm_graph(rule_definition)

        config1_payload = RuleEngineConfig(jdm=jdm_graph)
        config2_payload = RuleEngineConfig(jdm=jdm_graph)

        config1 = await rule_configuration.write_config(
            rule_definition.name, config1_payload
        )
        config2 = await rule_configuration.write_config(
            rule_definition.name, config2_payload
        )

        await rule_configuration.promote_config(config1.id)
        await rule_configuration.promote_config(config2.id)

        configs = await rule_configuration.read_configs_with_default(
            rule_definition.name, rule_definition.to_config()
        )

        assert len(configs) == 3
        active_configs = [c for c in configs if c.active]
        inactive_configs = [c for c in configs if not c.active]

        assert len(active_configs) == 1
        assert active_configs[0].id == config2.id
        assert len(inactive_configs) == 2
        assert inactive_configs[0].id == config1.id
        assert inactive_configs[1].id == DEFAULT_UUID

        db_config1 = (
            await session.exec(
                select(ObjectConfiguration).where(ObjectConfiguration.id == config1.id)
            )
        ).first()
        db_config2 = (
            await session.exec(
                select(ObjectConfiguration).where(ObjectConfiguration.id == config2.id)
            )
        ).first()
        assert db_config1 is not None and db_config1.active is False
        assert db_config2 is not None and db_config2.active is True

    async def test_promote_switches_active_agent_configs(
        self, session: AsyncSession, agent_definition: Agent
    ):
        """Test that promoting an agent config switches active status correctly."""
        object_name = f"test_agent_switches_active_{uuid4().hex}"
        config1_payload = AgentConfig(
            system_prompt="S1", user_prompt="U1", model="m1", max_turns=1
        )
        config2_payload = AgentConfig(
            system_prompt="S2", user_prompt="U2", model="m2", max_turns=2
        )

        config1 = await agent_configuration.write_config(object_name, config1_payload)
        config2 = await agent_configuration.write_config(object_name, config2_payload)

        await agent_configuration.promote_config(config1.id)
        await agent_configuration.promote_config(config2.id)

        configs = await agent_configuration.read_configs_with_default(
            object_name, agent_definition.to_config()
        )

        assert len(configs) == 3
        active_configs = [c for c in configs if c.active]
        inactive_configs = [c for c in configs if not c.active]

        assert len(active_configs) == 1
        assert active_configs[0].id == config2.id
        assert len(inactive_configs) == 2

        db_config1 = (
            await session.exec(
                select(ObjectConfiguration).where(ObjectConfiguration.id == config1.id)
            )
        ).first()
        db_config2 = (
            await session.exec(
                select(ObjectConfiguration).where(ObjectConfiguration.id == config2.id)
            )
        ).first()
        assert db_config1 is not None and db_config1.active is False
        assert db_config2 is not None and db_config2.active is True

    async def test_promote_default_rule_config_reverts(
        self, session: AsyncSession, rule_definition: Rule
    ):
        """Test promoting default rule config (UUID all zeros) reverts to original."""
        ObjectRegistry.get_instance().register(rule_definition)
        rule_config = RuleEngineConfig(jdm=create_jdm_graph(rule_definition))
        config = await rule_configuration.write_config(
            rule_definition.name, rule_config
        )

        await rule_configuration.promote_config(config.id)
        db_config_promoted = (
            await session.exec(
                select(ObjectConfiguration).where(ObjectConfiguration.id == config.id)
            )
        ).first()
        assert db_config_promoted is not None and db_config_promoted.active is True

        await session.commit()

        await rule_configuration.promote_config(
            DEFAULT_UUID, object_name=rule_definition.name
        )

        configs = await rule_configuration.read_configs_with_default(
            rule_definition.name, rule_definition.to_config()
        )

        assert len(configs) == 2
        assert configs[0].version == 1
        assert configs[1].version == 0

        assert configs[0].active is False
        assert configs[1].active is True

        db_config_reverted = (
            await session.exec(
                select(ObjectConfiguration).where(ObjectConfiguration.id == config.id)
            )
        ).first()
        assert db_config_reverted is not None and db_config_reverted.active is False

    async def test_promote_default_agent_config_reverts(
        self, session: AsyncSession, agent_definition: Agent
    ):
        """Test promoting default agent config (UUID all zeros) reverts."""
        object_name = f"test_agent_revert_default_{uuid4().hex}"
        agent_config = AgentConfig(
            system_prompt="S", user_prompt="U", model="m", max_turns=1
        )
        config = await agent_configuration.write_config(object_name, agent_config)

        await agent_configuration.promote_config(config.id)
        db_config_promoted = (
            await session.exec(
                select(ObjectConfiguration).where(ObjectConfiguration.id == config.id)
            )
        ).first()
        assert db_config_promoted is not None and db_config_promoted.active is True

        await session.commit()

        await agent_configuration.promote_config(DEFAULT_UUID, object_name=object_name)

        configs = await agent_configuration.read_configs_with_default(
            object_name, agent_definition.to_config()
        )

        assert len(configs) == 2

        assert configs[0].version == 1
        assert configs[1].version == 0

        assert configs[0].active is False
        assert configs[1].active is True

        db_config_reverted = (
            await session.exec(
                select(ObjectConfiguration).where(ObjectConfiguration.id == config.id)
            )
        ).first()
        assert db_config_reverted is not None and db_config_reverted.active is False

    async def test_promote_nonexistent_config_raises_error(self, session: AsyncSession):
        """Test promoting a non-existent config ID raises ConfigNotFoundError."""
        nonexistent_id = uuid4()
        with pytest.raises(ConfigNotFoundError) as excinfo_rule:
            await rule_configuration.promote_config(nonexistent_id)
        assert excinfo_rule.value.invalid_id == nonexistent_id
        assert excinfo_rule.value.object_type == ConfigurableObjectType.RULE

        with pytest.raises(ConfigNotFoundError) as excinfo_agent:
            await agent_configuration.promote_config(nonexistent_id)
        assert excinfo_agent.value.invalid_id == nonexistent_id
        assert excinfo_agent.value.object_type == ConfigurableObjectType.AGENT

    async def test_promote_default_config_requires_object_name(
        self, session: AsyncSession
    ):
        """Test promoting default UUID requires object_name parameter."""
        with pytest.raises(
            ValueError,
            match="object_name is required when reverting to default configuration",
        ):
            await rule_configuration.promote_config(DEFAULT_UUID)
        with pytest.raises(
            ValueError,
            match="object_name is required when reverting to default configuration",
        ):
            await agent_configuration.promote_config(DEFAULT_UUID)

    async def test_default_config_is_active_when_no_other_configs_present(
        self, session: AsyncSession, rule_definition: Rule, agent_definition: Agent
    ):
        """Test default config is active when no custom configs exist for the object_name."""
        object_name_rule = f"nonexistent_rule_for_default_{uuid4().hex}"
        object_name_agent = f"nonexistent_agent_for_default_{uuid4().hex}"

        configs = await rule_configuration.read_configs_with_default(
            object_name_rule, rule_definition.to_config()
        )
        assert len(configs) == 1
        assert configs[0].version == 0
        assert configs[0].active is True

        await agent_configuration.promote_config(
            DEFAULT_UUID, object_name=object_name_agent
        )
        configs = await agent_configuration.read_configs_with_default(
            object_name_agent, agent_definition.to_config()
        )
        assert len(configs) == 1
        assert configs[0].version == 0
        assert configs[0].active is True

    async def test_promote_returns_all_configs_ordered(
        self, session: AsyncSession, agent_definition: Agent
    ):
        """Test that promote_config returns all configurations for the object_name, ordered by version."""
        object_name = f"test_agent_promote_all_ordered_{uuid4().hex}"
        created_configs = []
        for i in range(3):
            config = AgentConfig(
                system_prompt=f"Config {i}",
                user_prompt=f"UP {i}",
                model="m",
                max_turns=i + 1,
            )
            cfg = await agent_configuration.write_config(object_name, config)
            created_configs.append(cfg)

        # Promote the middle config (chronologically, so it's version 2, index 1 if created_configs is in creation order)
        # Assuming versions are 1, 2, 3. Created_configs[1] is version 2.
        # The versions will be 3, 2, 1 in the database after 3 writes.
        # So created_configs[0] (first written) would be version 1.
        # created_configs[1] (second written) would be version 2.
        # created_configs[2] (third written) would be version 3.

        # Let's fetch all configs to be sure about IDs and versions before promoting
        all_configs_before_promote = (
            await agent_configuration.read_configs_with_default(
                object_name, agent_definition.to_config()
            )
        )
        ids_by_version_desc = [
            c.id for c in all_configs_before_promote
        ]  # Should be [id_v3, id_v2, id_v1, id_default]

        # Verify that the default config is active by default
        default_config = all_configs_before_promote[-1]
        assert default_config.active is True, (
            "Default config should be active by default"
        )

        # Promote the one that corresponds to original version 2 (second created)
        # This ID would be ids_by_version_desc[1]
        config_to_promote_id = ids_by_version_desc[1]

        await agent_configuration.promote_config(config_to_promote_id)

        all_configs_after_promote = await agent_configuration.read_configs_with_default(
            object_name, agent_definition.to_config()
        )

        assert len(all_configs_after_promote) == 4

        versions = [config.version for config in all_configs_after_promote]
        assert versions == sorted(versions, reverse=True), (
            "Configs should be sorted by version descending"
        )

        active_configs = [
            config for config in all_configs_after_promote if config.active
        ]
        assert len(active_configs) == 1
        assert active_configs[0].id == config_to_promote_id

    async def test_promote_multiple_configs_only_one_active_rule(
        self, session: AsyncSession, rule_definition: Rule
    ):
        """Test that when multiple rule configs exist, only the promoted one is active."""
        ObjectRegistry.get_instance().register(rule_definition)

        config_ids = []
        for i in range(3):
            rule_config = RuleEngineConfig(jdm=create_jdm_graph(rule_definition))
            cfg = await rule_configuration.write_config(
                rule_definition.name, rule_config
            )
            config_ids.append(cfg.id)

        # Config_ids are in order of creation: [id_v1, id_v2, id_v3]
        # After all writes, read_configs would return them ordered [v3, v2, v1]
        # Let's promote the middle one created (which would be version 2)
        # To get its ID robustly, let's re-fetch and pick based on version or order.
        all_cfgs = await rule_configuration._read_configs(rule_definition.name)

        # all_cfgs.configs is sorted by version desc (e.g. [v3, v2, v1])
        # We want to promote the one with original version 2. This is all_cfgs.configs[1]
        id_to_promote = all_cfgs[1].id

        await rule_configuration.promote_config(id_to_promote)

        configs = await rule_configuration.read_configs_with_default(
            rule_definition.name, rule_definition.to_config()
        )

        assert len(configs) == 4
        active_found = [c for c in configs if c.active]
        assert len(active_found) == 1
        assert active_found[0].id == id_to_promote

        # Verify in database: iterate through all initially created config IDs
        # and check their active status. Only id_to_promote should be active.
        # config_ids was populated in order of creation: [id_for_v1, id_for_v2, id_for_v3]
        # id_to_promote corresponds to the one with version 2 (the second one created).
        for created_id in config_ids:
            db_config = (
                await session.exec(
                    select(ObjectConfiguration).where(
                        ObjectConfiguration.id == created_id
                    )
                )
            ).first()
            assert db_config is not None, f"Config with ID {created_id} not found in DB"
            if created_id == id_to_promote:
                assert db_config.active is True, (
                    f"Promoted config {created_id} should be active"
                )
            else:
                assert db_config.active is False, (
                    f"Non-promoted config {created_id} should be inactive"
                )
