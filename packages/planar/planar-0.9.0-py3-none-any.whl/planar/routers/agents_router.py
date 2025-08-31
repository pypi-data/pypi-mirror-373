import asyncio
import json
from typing import Any, AsyncGenerator

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from planar.ai.agent_utils import agent_configuration
from planar.ai.models import AgentConfig, AgentEventEmitter, AgentEventType
from planar.ai.utils import AgentSerializeable, serialize_agent
from planar.logging import get_logger
from planar.object_config.object_config import ConfigValidationError
from planar.object_registry import ObjectRegistry
from planar.security.authorization import (
    AgentAction,
    AgentResource,
    validate_authorization_for,
)
from planar.session import get_engine, session_context
from planar.utils import utc_now

logger = get_logger(__name__)


class AgentSimulationRequestBody(BaseModel):
    input_value: str | dict[str, Any]


class AgentSimulationData[T](BaseModel):
    input_value: str | T


class SimulationAgentEvent:
    def __init__(
        self,
        event_type: AgentEventType,
        data: BaseModel | str | None,
    ):
        self.event_type = event_type
        self.data = data
        self.timestamp = utc_now().isoformat()


class SimulationAgentEventEmitter(AgentEventEmitter):
    def __init__(self):
        self.queue: asyncio.Queue[SimulationAgentEvent] = asyncio.Queue()

    def emit(self, event_type: AgentEventType, data: BaseModel | str | None):
        event = SimulationAgentEvent(event_type, data)
        self.queue.put_nowait(event)

    async def get_events(self) -> AsyncGenerator[str, None]:
        while True:
            event = await self.queue.get()

            if isinstance(event.data, BaseModel):
                data = {
                    "data": event.data.model_dump(),
                    "event_type": event.event_type,
                }
            else:
                data = {
                    "data": event.data,
                    "event_type": event.event_type,
                }

            yield f"data: {json.dumps(data)}\n\n"

            self.queue.task_done()

            if event.event_type in (AgentEventType.COMPLETED, AgentEventType.ERROR):
                break

    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return self.queue.empty()


class AgentEvent(BaseModel):
    """Model representing a single event emitted by the agent."""

    event: str
    data: dict


class AgentErrorData(BaseModel):
    detail: str


class AgentUpdateRequest(BaseModel):
    """Model for updating agent information."""

    system_prompt: str | None = None
    user_prompt: str | None = None


def create_agent_router(object_registry: ObjectRegistry) -> APIRouter:
    router = APIRouter(tags=["Agents"])

    @router.get("/", response_model=list[AgentSerializeable])
    async def get_agents():
        """Get all agents."""
        validate_authorization_for(AgentResource(), AgentAction.AGENT_LIST)
        registered_agents = object_registry.get_agents()
        serialized_agents: list[AgentSerializeable] = []

        for reg_agent in registered_agents:
            agent_serializable = await serialize_agent(
                agent_obj=reg_agent,
            )

            if agent_serializable:
                serialized_agents.append(agent_serializable)

        return serialized_agents

    @router.patch("/{agent_name}", response_model=AgentSerializeable)
    async def update_agent(agent_name: str, request: AgentUpdateRequest):
        """Update agent information (system prompt and user prompt)."""
        validate_authorization_for(
            AgentResource(id=agent_name), AgentAction.AGENT_UPDATE
        )
        agents = object_registry.get_agents()
        agent = next((a for a in agents if a.name == agent_name), None)
        if not agent:
            logger.warning("agent not found for update", agent_name=agent_name)
            raise HTTPException(status_code=404, detail="Agent not found")

        update = AgentConfig(
            model=str(agent.model),
            max_turns=agent.max_turns,
            model_parameters=agent.model_parameters,
            # At the moment, these are the only two fields that can be overridden
            system_prompt=request.system_prompt or agent.system_prompt,
            user_prompt=request.user_prompt or agent.user_prompt,
        )

        try:
            await agent_configuration.write_config(agent.name, update)
        except ConfigValidationError as e:
            raise HTTPException(
                status_code=400,
                detail=e.to_api_response().model_dump(mode="json", by_alias=True),
            )

        logger.info(
            "configuration updated for agent",
            agent_name=agent.name,
        )

        agent_serializable = await serialize_agent(
            agent_obj=agent,
        )

        if not agent_serializable:
            logger.warning(
                "failed to create serializable representation for agent after update",
                agent_name=agent.name,
            )
            raise HTTPException(
                status_code=500, detail="Failed to create agent representation"
            )

        return agent_serializable

    @router.post(
        "/{agent_name}/simulate",
        response_model=None,  # No standard response model for SSE
        responses={
            200: {
                "description": "Stream of agent events",
                "content": {
                    "text/event-stream": {
                        "schema": {
                            "type": "object",
                        }
                    }
                },
            }
        },
    )
    async def simulate_agent(
        agent_name: str,
        request: AgentSimulationRequestBody,
        background_tasks: BackgroundTasks,
    ):
        """Simulate an agent."""
        validate_authorization_for(
            AgentResource(id=agent_name), AgentAction.AGENT_SIMULATE
        )
        agents = object_registry.get_agents()
        agent = next((a for a in agents if a.name == agent_name), None)
        if not agent:
            logger.warning("agent not found for simulation", agent_name=agent_name)
            raise HTTPException(status_code=404, detail="Agent not found")

        emitter = SimulationAgentEventEmitter()

        # Create a copy of the request data to avoid sharing data between tasks
        request_copy = request.model_copy()

        # Create the background task with its own session context
        async def run_agent_with_session():
            logger.debug(
                "background task started for agent simulation", agent_name=agent_name
            )
            try:
                async with session_context(get_engine()):
                    data_model = (
                        AgentSimulationData[agent.input_type]
                        if agent.input_type
                        else AgentSimulationData
                    )
                    parsed_data = data_model.model_validate(request_copy.model_dump())
                    agent.event_emitter = emitter
                    await agent(parsed_data.input_value)
                    agent.event_emitter = None
                logger.debug(
                    "background task finished for agent simulation",
                    agent_name=agent_name,
                )
            except Exception as e:
                logger.error(
                    "background task failed for agent simulation",
                    agent_name=agent_name,
                    error=e,
                )
                emitter.emit(AgentEventType.ERROR, AgentErrorData(detail=str(e)))

        # Cancel the agent task when the response is closed
        agent_task = asyncio.create_task(run_agent_with_session())

        async def cancel_agent_task():
            if not agent_task.done():
                agent_task.cancel()
                logger.debug("agent task cancelled", agent_name=agent_name)

        background_tasks.add_task(cancel_agent_task)

        return StreamingResponse(
            emitter.get_events(),
            media_type="text/event-stream",
            background=background_tasks,
        )

    return router
