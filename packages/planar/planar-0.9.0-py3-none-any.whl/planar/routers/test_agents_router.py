"""
Tests for agent router endpoints.

This module tests the agent router endpoints to ensure they work correctly
with the new serialization changes.
"""

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from planar.ai.agent import Agent
from planar.app import PlanarApp
from planar.config import sqlite_config
from planar.testing.planar_test_client import PlanarTestClient


@pytest.fixture(name="app")
def app_fixture():
    """Create a test app with agents."""
    app = PlanarApp(
        config=sqlite_config(":memory:"),
        title="Test app for agent router",
        description="Testing agent endpoints",
    )

    # Register a simple agent
    simple_agent = Agent(
        name="simple_test_agent",
        system_prompt="Simple system prompt",
        user_prompt="Simple user prompt: {input}",
        model="openai:gpt-4o",
        max_turns=2,
    )
    app.register_agent(simple_agent)

    # Register an agent with tools
    async def test_tool(param: str) -> str:
        """A test tool."""
        return f"Processed: {param}"

    agent_with_tools = Agent(
        name="agent_with_tools",
        system_prompt="System with tools",
        user_prompt="User: {input}",
        model="anthropic:claude-3-5-sonnet-latest",
        max_turns=5,
        tools=[test_tool],
    )
    app.register_agent(agent_with_tools)

    return app


async def test_get_agents_endpoint(
    client: PlanarTestClient, app: PlanarApp, session: AsyncSession
):
    """Test the GET /agents endpoint returns agents with configs field."""
    response = await client.get("/planar/v1/agents/")
    assert response.status_code == 200

    agents = response.json()
    assert len(agents) == 2

    # Check first agent
    simple_agent = next(a for a in agents if a["name"] == "simple_test_agent")
    assert simple_agent["name"] == "simple_test_agent"
    assert "configs" in simple_agent
    assert isinstance(simple_agent["configs"], list)
    assert len(simple_agent["configs"]) == 1  # Default config always present

    # Verify the default config is present and correct
    default_config = simple_agent["configs"][-1]
    assert default_config["version"] == 0
    assert default_config["data"]["system_prompt"] == "Simple system prompt"
    assert default_config["data"]["user_prompt"] == "Simple user prompt: {input}"
    assert default_config["data"]["model"] == "openai:gpt-4o"
    assert default_config["data"]["max_turns"] == 2

    # Verify removed fields are not present
    assert "system_prompt" not in simple_agent
    assert "user_prompt" not in simple_agent
    assert "model" not in simple_agent
    assert "max_turns" not in simple_agent
    assert "overwrites" not in simple_agent

    # Check agent with tools
    tools_agent = next(a for a in agents if a["name"] == "agent_with_tools")
    assert len(tools_agent["tool_definitions"]) == 1
    assert tools_agent["tool_definitions"][0]["name"] == "test_tool"


async def test_update_agent_endpoint(
    client: PlanarTestClient, app: PlanarApp, session: AsyncSession
):
    """Test the PATCH /agents/{agent_name} endpoint creates configs."""
    # Get agents first
    response = await client.get("/planar/v1/agents/")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) == 2

    # Update the agent
    update_data = {
        "system_prompt": "Updated system prompt",
        "user_prompt": "Updated user prompt: {input}",
    }
    response = await client.patch(
        "/planar/v1/agents/simple_test_agent", json=update_data
    )
    assert response.status_code == 200

    updated_agent = response.json()
    assert "configs" in updated_agent
    assert len(updated_agent["configs"]) == 2

    # Check the config data
    config = updated_agent["configs"][0]
    assert config["data"]["system_prompt"] == "Updated system prompt"
    assert config["data"]["user_prompt"] == "Updated user prompt: {input}"
    assert config["version"] == 1
    assert config["object_type"] == "agent"
    assert config["object_name"] == "simple_test_agent"


async def test_agent_with_multiple_configs(
    client: PlanarTestClient, app: PlanarApp, session: AsyncSession
):
    """Test that agents return all configs when multiple exist."""
    # Get the agent ID first
    response = await client.get("/planar/v1/agents/")
    agents = response.json()
    simple_agent = next(a for a in agents if a["name"] == "simple_test_agent")

    # Create first config via PATCH endpoint
    config1_data = {
        "system_prompt": "Config 1 system",
        "user_prompt": "Config 1 user: {input}",
        "model": "openai:gpt-4o",
        "max_turns": 2,
        "model_parameters": {"temperature": 0.7},
    }
    response = await client.patch(
        f"/planar/v1/agents/{simple_agent['name']}", json=config1_data
    )
    assert response.status_code == 200

    # Create second config via PATCH endpoint
    config2_data = {
        "system_prompt": "Config 2 system",
        "user_prompt": "Config 2 user: {input}",
        "model": "anthropic:claude-3-opus",
        "max_turns": 4,
        "model_parameters": {"temperature": 0.9},
    }
    response = await client.patch(
        f"/planar/v1/agents/{simple_agent['name']}", json=config2_data
    )
    assert response.status_code == 200

    # Get agents
    response = await client.get("/planar/v1/agents/")
    agents = response.json()
    simple_agent = next(a for a in agents if a["name"] == "simple_test_agent")

    # Verify all configs are returned (including default config)
    assert len(simple_agent["configs"]) == 3
    assert simple_agent["configs"][0]["version"] == 2  # Latest first
    assert simple_agent["configs"][1]["version"] == 1
    assert simple_agent["configs"][2]["version"] == 0  # Default config

    # Verify config data
    assert simple_agent["configs"][0]["data"]["system_prompt"] == "Config 2 system"
    assert simple_agent["configs"][1]["data"]["system_prompt"] == "Config 1 system"
    assert simple_agent["configs"][2]["data"]["system_prompt"] == "Simple system prompt"
