"""
Utility functions for working with AI models and agents.

This module contains helper functions for working with AI models
and agents, particularly around serialization and representation.
"""

from typing import Optional

from planar.ai.agent import Agent
from planar.ai.agent_utils import agent_configuration, create_tool_definition
from planar.ai.models import AgentSerializeable
from planar.logging import get_logger
from planar.object_registry import ObjectRegistry

logger = get_logger(__name__)


async def serialize_agent(
    agent_obj: Agent,
) -> AgentSerializeable:
    """
    Serialize an agent object into AgentSerializeable with schema validation warnings.

    Creates a serializable representation of an Agent, including all database
    configurations and schema validation status.

    Args:
        agent_obj: The agent object to serialize

    Returns:
        AgentSerializeable representation of the agent
    """
    logger.debug("serializing agent", agent_name=agent_obj.name)
    # Process tools if present
    tool_definitions = []
    if agent_obj.tools:
        tool_definitions = [
            create_tool_definition(t).model_dump() for t in agent_obj.tools
        ]
    logger.debug(
        "tool definitions for agent",
        agent_name=agent_obj.name,
        num_tools=len(tool_definitions),
    )

    input_schema = agent_obj.input_schema()
    result_schema = agent_obj.output_schema()
    logger.debug(
        "agent schema presence",
        input_schema_present=input_schema is not None,
        output_schema_present=result_schema is not None,
    )

    configs_list = await agent_configuration.read_configs_with_default(
        agent_obj.name, agent_obj.to_config()
    )
    logger.debug(
        "retrieved configurations for agent",
        num_configs=len(configs_list),
        agent_name=agent_obj.name,
    )

    serializable = AgentSerializeable(
        name=agent_obj.name,
        tool_definitions=tool_definitions,
        input_schema=input_schema,
        output_schema=result_schema,
        configs=configs_list,
    )
    logger.debug("agent serialized successfully", agent_name=agent_obj.name)
    return serializable


async def get_agent_serializable(
    agent_name: str,
    registry: ObjectRegistry,
) -> Optional[AgentSerializeable]:
    """
    Look up an agent by name in the registry and serialize it.

    Args:
        agent_name: The name of the agent to look up
        registry: ObjectRegistry to look up the agent

    Returns:
        AgentSerializeable representation of the agent, or None if not found
    """
    logger.debug("looking up agent by name", agent_name=agent_name)
    # Find the first agent with matching name, or None if none found
    reg_agent = next(
        (agent for agent in registry.get_agents() if agent.name == agent_name), None
    )
    if not reg_agent:
        logger.debug("agent not found in registry", agent_name=agent_name)
        return None

    logger.debug(
        "found agent in registry, serializing",
        agent_name=agent_name,
    )
    return await serialize_agent(reg_agent)
