"""
Tests for agent serialization functionality.

This module tests the serialization of agents including configuration
management and schema validation warnings.
"""

import pytest
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from planar.ai.agent import Agent
from planar.ai.agent_utils import AgentConfig, agent_configuration
from planar.ai.models import AgentSerializeable
from planar.ai.utils import serialize_agent
from planar.object_config.object_config import ObjectConfigurationBase


class InputModelForTest(BaseModel):
    """Test input model for agents."""

    text: str
    value: int


class OutputModelForTest(BaseModel):
    """Test output model for agents."""

    result: str
    score: float


@pytest.fixture
def test_agent():
    """Create a test agent with various configurations."""
    return Agent(
        name="test_serialization_agent",
        system_prompt="Test system prompt",
        user_prompt="Test user prompt: {input}",
        model="openai:gpt-4o",
        max_turns=3,
        input_type=InputModelForTest,
        output_type=OutputModelForTest,
    )


@pytest.fixture
def test_agent_with_tools():
    """Create a test agent with tools."""

    async def test_tool(param: str) -> str:
        """A test tool."""
        return f"Processed: {param}"

    return Agent(
        name="test_agent_with_tools",
        system_prompt="System with tools",
        user_prompt="User: {input}",
        model="anthropic:claude-3-5-sonnet-latest",
        max_turns=5,
        tools=[test_tool],
    )


async def test_serialize_agent_basic(session: AsyncSession, test_agent):
    """Test basic agent serialization without any configurations."""

    # Serialize the agent
    serialized = await serialize_agent(test_agent)

    # Verify basic fields
    assert isinstance(serialized, AgentSerializeable)
    assert serialized.name == "test_serialization_agent"
    assert serialized.input_schema is not None
    assert serialized.output_schema is not None
    assert serialized.tool_definitions == []

    # Verify configs field exists and contains the default config (at least one config always present)
    assert hasattr(serialized, "configs")
    assert len(serialized.configs) == 1

    # Verify the default config is present and correct
    default_config = serialized.configs[-1]
    assert isinstance(default_config, ObjectConfigurationBase)
    assert default_config.version == 0
    assert default_config.data.system_prompt == test_agent.system_prompt
    assert default_config.data.user_prompt == test_agent.user_prompt
    assert default_config.data.model == str(test_agent.model)
    assert default_config.data.max_turns == test_agent.max_turns
    assert default_config.data.model_parameters == test_agent.model_parameters

    # Verify overwrites field is removed
    assert not hasattr(serialized, "overwrites")


async def test_serialize_agent_with_configs(session: AsyncSession, test_agent):
    """Test agent serialization with multiple configurations."""

    # Create multiple configurations
    config1 = AgentConfig(
        system_prompt="Override system 1",
        user_prompt="Override user 1: {input}",
        model="openai:gpt-4o",
        max_turns=2,
        model_parameters={"temperature": 0.7},
    )

    config2 = AgentConfig(
        system_prompt="Override system 2",
        user_prompt="Override user 2: {input}",
        model="anthropic:claude-3-opus",
        max_turns=4,
        model_parameters={"temperature": 0.9},
    )

    # Write configurations
    await agent_configuration.write_config(test_agent.name, config1)
    await agent_configuration.write_config(test_agent.name, config2)

    # Serialize the agent
    serialized = await serialize_agent(test_agent)

    # Verify configs are included
    assert len(serialized.configs) == 3

    # Verify default config is included
    default_config = serialized.configs[-1]
    assert isinstance(default_config, ObjectConfigurationBase)
    assert default_config.version == 0
    assert default_config.data.system_prompt == test_agent.system_prompt
    assert default_config.data.user_prompt == test_agent.user_prompt
    assert default_config.data.model == str(test_agent.model)
    assert default_config.data.max_turns == test_agent.max_turns
    assert default_config.data.model_parameters == test_agent.model_parameters

    # Verify configs are ordered by version (descending)
    assert all(
        isinstance(config, ObjectConfigurationBase) for config in serialized.configs
    )
    assert serialized.configs[0].version == 2  # Latest version first
    assert serialized.configs[1].version == 1

    # Verify config data
    latest_config = serialized.configs[0]
    assert latest_config.data.system_prompt == "Override system 2"
    assert latest_config.data.user_prompt == "Override user 2: {input}"
    assert latest_config.data.model == "anthropic:claude-3-opus"
    assert latest_config.data.max_turns == 4

    older_config = serialized.configs[1]
    assert older_config.data.system_prompt == "Override system 1"
    assert older_config.data.user_prompt == "Override user 1: {input}"


async def test_serialize_agent_with_tools(session: AsyncSession, test_agent_with_tools):
    """Test serialization of agent with tools."""

    # Serialize the agent
    serialized = await serialize_agent(test_agent_with_tools)

    # Verify tool definitions are included
    assert len(serialized.tool_definitions) == 1
    tool_def = serialized.tool_definitions[0]
    assert tool_def["name"] == "test_tool"
    assert tool_def["description"] == "A test tool."
    assert "parameters" in tool_def


async def test_serialize_agent_no_duplicate_fields(session: AsyncSession, test_agent):
    """Test that AgentSerializeable doesn't duplicate fields from AgentConfig."""

    # Create a configuration
    config = AgentConfig(
        system_prompt="Config system",
        user_prompt="Config user: {input}",
        model="openai:gpt-3.5-turbo",
        max_turns=1,
        model_parameters={},
    )

    await agent_configuration.write_config(test_agent.name, config)

    # Serialize the agent
    serialized = await serialize_agent(test_agent)

    # Verify that system_prompt, user_prompt, model, max_turns are NOT in the serialized object
    # They should only be in the configs
    assert not hasattr(serialized, "system_prompt")
    assert not hasattr(serialized, "user_prompt")
    assert not hasattr(serialized, "model")
    assert not hasattr(serialized, "max_turns")

    # These fields should only be accessible through configs
    assert serialized.configs[0].data.system_prompt == "Config system"
    assert serialized.configs[0].data.user_prompt == "Config user: {input}"
    assert serialized.configs[0].data.model == "openai:gpt-3.5-turbo"
    assert serialized.configs[0].data.max_turns == 1


async def test_agent_serializable_structure():
    """Test the structure of AgentSerializeable model."""
    # Verify the model has the expected fields
    fields = AgentSerializeable.model_fields.keys()

    # Should have these fields
    assert "name" in fields
    assert "input_schema" in fields
    assert "output_schema" in fields
    assert "tool_definitions" in fields
    assert "configs" in fields
    assert "built_in_vars" in fields

    # Should NOT have these fields (moved to configs)
    assert "system_prompt" not in fields
    assert "user_prompt" not in fields
    assert "model" not in fields
    assert "max_turns" not in fields
    assert "overwrites" not in fields


async def test_configs_field_type():
    """Test that configs field has the correct type annotation."""
    # Get the type annotation for configs field
    configs_field = AgentSerializeable.model_fields["configs"]

    # The annotation should be list[ObjectConfigurationBase[AgentConfig]]
    # This is a complex type, so we'll check the string representation
    assert "ObjectConfigurationBase" in str(configs_field.annotation)
    assert "AgentConfig" in str(configs_field.annotation)
