"""
Tests for object configuration router endpoints.

This module tests the object configuration router endpoints to ensure they work correctly
for both agent and rule configurations.
"""

from typing import AsyncGenerator
from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from planar.ai.agent import Agent
from planar.ai.agent_utils import agent_configuration
from planar.ai.models import AgentConfig
from planar.app import PlanarApp
from planar.config import sqlite_config
from planar.object_config import DEFAULT_UUID, ObjectConfiguration
from planar.object_config.object_config import ConfigurableObjectType
from planar.object_registry import ObjectRegistry
from planar.rules.decorator import rule
from planar.rules.models import Rule, RuleEngineConfig, create_jdm_graph
from planar.rules.rule_configuration import rule_configuration
from planar.testing.planar_test_client import PlanarTestClient


class InputForTestRule(BaseModel):
    """Input for test rule."""

    value: int = Field(description="Test value")
    category: str = Field(description="Test category")


class OutputFromTestRule(BaseModel):
    """Output from test rule."""

    result: int = Field(description="Result value")
    message: str = Field(description="Result message")


@pytest.fixture(name="app")
def app_fixture():
    """Create a test app with agents and rules."""
    app = PlanarApp(
        config=sqlite_config(":memory:"),
        title="Test app for object config router",
        description="Testing object configuration endpoints",
    )

    # Register a simple agent
    simple_agent = Agent(
        name="test_agent",
        system_prompt="Test system prompt",
        user_prompt="Test user prompt: {input}",
        model="openai:gpt-4o",
        max_turns=2,
    )
    app.register_agent(simple_agent)

    # Create and register a rule
    @rule(description="Test rule for configuration")
    def test_rule(input: InputForTestRule) -> OutputFromTestRule:
        # Default implementation
        return OutputFromTestRule(
            result=input.value * 2, message=f"Processed {input.category}"
        )

    app.register_rule(test_rule)

    return app


@pytest.fixture
async def agent_with_configs(app: PlanarApp, session: AsyncSession):
    """Create an agent with multiple configurations."""
    # First config
    agent_config_1 = AgentConfig(
        system_prompt="Config 1 system",
        user_prompt="Config 1 user: {input}",
        model="openai:gpt-4o",
        max_turns=3,
    )
    await agent_configuration.write_config("test_agent", agent_config_1)

    # Second config
    agent_config_2 = AgentConfig(
        system_prompt="Config 2 system",
        user_prompt="Config 2 user: {input}",
        model="anthropic:claude-3-sonnet",
        max_turns=5,
    )
    config_2 = await agent_configuration.write_config("test_agent", agent_config_2)

    # Make the second config active
    await agent_configuration.promote_config(config_2.id)

    return config_2.id


@pytest.fixture
async def rule_with_configs(
    session: AsyncSession,
) -> AsyncGenerator[tuple[Rule, list[ObjectConfiguration]], None]:
    class RuleInputOutput(BaseModel):
        test: str

    rule = Rule(
        name=f"test_rule_promote_{uuid4().hex}",
        description="Test rule for promoting configuration",
        input=RuleInputOutput,
        output=RuleInputOutput,
    )
    ObjectRegistry.get_instance().register(rule)

    # Create some configs
    jdm_config_1 = create_jdm_graph(rule)
    jdm_config_2 = create_jdm_graph(rule)

    rule_config_1 = RuleEngineConfig(jdm=jdm_config_1)
    rule_config_2 = RuleEngineConfig(jdm=jdm_config_2)

    config1 = await rule_configuration.write_config(rule.name, rule_config_1)
    config2 = await rule_configuration.write_config(rule.name, rule_config_2)

    yield rule, [config1, config2]


async def test_promote_agent_config(
    client: PlanarTestClient,
    app: PlanarApp,
    session: AsyncSession,
    agent_with_configs: UUID,
):
    """Test promoting an agent configuration."""
    # Get the configurations first to find a non-active one
    agent = app._object_registry.get_agents()[0]
    configs = await agent_configuration.read_configs_with_default(
        "test_agent", agent.to_config()
    )

    # Find the first (inactive) config
    inactive_config = next(c for c in configs if not c.active)

    # Promote the inactive config
    request_data = {
        "object_type": ConfigurableObjectType.AGENT,
        "config_id": str(inactive_config.id),
        "object_name": "test_agent",
    }

    response = await client.post(
        "/planar/v1/object-configurations/promote", json=request_data
    )
    assert response.status_code == 200

    result = response.json()
    assert "configs" in result
    assert len(result["configs"]) >= 3  # At least 2 configs + default

    # Verify the promoted config is now active
    promoted_config = next(
        c for c in result["configs"] if c["id"] == str(inactive_config.id)
    )
    assert promoted_config["active"] is True

    # Verify other configs are inactive
    for config in result["configs"]:
        if config["id"] != str(inactive_config.id):
            assert config["active"] is False


async def test_promote_rule_config(
    client: PlanarTestClient,
    app: PlanarApp,
    session: AsyncSession,
):
    """Test promoting a rule configuration."""
    # Get the configurations first to find a non-active one
    rule = ObjectRegistry.get_instance().get_rules()[0]

    await rule_configuration.write_config(
        rule.name, RuleEngineConfig(jdm=create_jdm_graph(rule))
    )

    configs = await rule_configuration.read_configs_with_default(
        rule.name, rule.to_config()
    )

    assert len(configs) == 2

    # Find the first (inactive) config
    inactive_config = next(c for c in configs if not c.active)

    # Promote the inactive config
    request_data = {
        "object_type": ConfigurableObjectType.RULE,
        "config_id": str(inactive_config.id),
        "object_name": rule.name,
    }

    response = await client.post(
        "/planar/v1/object-configurations/promote", json=request_data
    )
    assert response.status_code == 200

    result = response.json()
    assert "configs" in result
    assert len(result["configs"]) == 2

    # Verify the promoted config is now active
    promoted_config = next(
        c for c in result["configs"] if c["id"] == str(inactive_config.id)
    )
    assert promoted_config["active"] is True

    # Verify the config data is correct
    assert promoted_config["object_type"] == "rule"
    assert promoted_config["object_name"] == rule.name
    assert "jdm" in promoted_config["data"]


async def test_promote_to_default_agent(
    client: PlanarTestClient,
    app: PlanarApp,
    session: AsyncSession,
    agent_with_configs: UUID,
):
    """Test promoting to default (revert to original implementation) for agent."""
    # Promote to default using the special UUID
    request_data = {
        "object_type": ConfigurableObjectType.AGENT,
        "config_id": str(DEFAULT_UUID),
        "object_name": "test_agent",
    }

    response = await client.post(
        "/planar/v1/object-configurations/promote", json=request_data
    )
    assert response.status_code == 200

    result = response.json()
    assert "configs" in result

    # Verify all non-default configs are inactive
    for config in result["configs"]:
        if config["version"] == 0:  # Default config
            assert config["active"] is True
        else:
            assert config["active"] is False


async def test_promote_to_default_rule(
    client: PlanarTestClient,
    app: PlanarApp,
    session: AsyncSession,
    rule_with_configs: UUID,
):
    """Test promoting to default (revert to original implementation) for rule."""
    # Promote to default using the special UUID
    request_data = {
        "object_type": ConfigurableObjectType.RULE,
        "config_id": str(DEFAULT_UUID),
        "object_name": "test_rule",
    }

    response = await client.post(
        "/planar/v1/object-configurations/promote", json=request_data
    )
    assert response.status_code == 200

    result = response.json()
    assert "configs" in result

    # Verify all non-default configs are inactive
    for config in result["configs"]:
        if config["version"] == 0:  # Default config
            assert config["active"] is True
        else:
            assert config["active"] is False


async def test_promote_nonexistent_agent(
    client: PlanarTestClient, app: PlanarApp, session: AsyncSession
):
    """Test promoting config for non-existent agent."""
    request_data = {
        "object_type": ConfigurableObjectType.AGENT,
        "config_id": str(UUID("12345678-1234-5678-1234-567812345678")),
        "object_name": "nonexistent_agent",
    }

    response = await client.post(
        "/planar/v1/object-configurations/promote", json=request_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Agent not found"


async def test_promote_nonexistent_rule(
    client: PlanarTestClient, app: PlanarApp, session: AsyncSession
):
    """Test promoting config for non-existent rule."""
    request_data = {
        "object_type": ConfigurableObjectType.RULE,
        "config_id": str(UUID("12345678-1234-5678-1234-567812345678")),
        "object_name": "nonexistent_rule",
    }

    response = await client.post(
        "/planar/v1/object-configurations/promote", json=request_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Rule not found"


async def test_promote_nonexistent_config(
    client: PlanarTestClient,
    app: PlanarApp,
    session: AsyncSession,
    agent_with_configs: UUID,
):
    """Test promoting a non-existent configuration."""
    # Try to promote a config that doesn't exist
    request_data = {
        "object_type": ConfigurableObjectType.AGENT,
        "config_id": str(UUID("99999999-9999-9999-9999-999999999999")),
        "object_name": "test_agent",
    }

    # This should fail with an error from the promote_config method
    response = await client.post(
        "/planar/v1/object-configurations/promote", json=request_data
    )
    assert response.status_code == 404


async def test_config_versions_ordering(
    client: PlanarTestClient,
    app: PlanarApp,
    session: AsyncSession,
    agent_with_configs: UUID,
):
    """Test that configurations are returned in correct version order."""
    # Promote to ensure we have a known state
    request_data = {
        "object_type": ConfigurableObjectType.AGENT,
        "config_id": str(agent_with_configs),
        "object_name": "test_agent",
    }

    response = await client.post(
        "/planar/v1/object-configurations/promote", json=request_data
    )
    assert response.status_code == 200

    result = response.json()
    configs = result["configs"]

    # Verify configs are ordered by version descending (except default which is always last)
    non_default_configs = [c for c in configs if c["version"] != 0]
    versions = [c["version"] for c in non_default_configs]
    assert versions == sorted(versions, reverse=True)

    # Verify default config is last
    assert configs[-1]["version"] == 0
