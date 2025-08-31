"""
Event API router for Planar workflows.

This module provides API routes for emitting events that workflows might be waiting for.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from sqlmodel import col, select

from planar.logging import get_logger
from planar.session import get_session
from planar.workflows.events import emit_event as emit_workflow_event
from planar.workflows.models import WorkflowEvent

logger = get_logger(__name__)


class EventEmitRequest(BaseModel):
    event_key: str
    payload: Optional[Dict[str, Any]] = None
    workflow_id: Optional[UUID] = None


class EventResponse(BaseModel):
    id: UUID
    event_key: str
    timestamp: str
    payload: Optional[Dict[str, Any]] = None
    workflow_id: Optional[UUID] = None


def create_workflow_event_routes(router: APIRouter):
    @router.post("/events/emit", response_model=EventResponse)
    async def emit_event(request: EventEmitRequest = Body(...)):
        """
        Emit an event that workflows might be waiting for.

        This endpoint allows external systems or APIs to emit events that will
        wake up workflows waiting for those events.
        """
        try:
            event, woken_workflows_count = await emit_workflow_event(
                event_key=request.event_key,
                payload=request.payload,
                workflow_id=request.workflow_id,
            )
            logger.info(
                "event emitted",
                event_key=request.event_key,
                event_id=event.id,
                woken_workflows_count=woken_workflows_count,
            )
            return EventResponse(
                id=event.id,
                event_key=event.event_key,
                timestamp=event.timestamp.isoformat(),
                payload=event.payload,
                workflow_id=event.workflow_id,
            )
        except Exception as e:
            logger.exception("error emitting event", event_key=request.event_key)
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/events/list", response_model=List[EventResponse])
    async def list_events(limit: int = 50, event_key: Optional[str] = None):
        """
        List recent events, optionally filtered by event key.
        """
        session = get_session()

        query = select(WorkflowEvent).order_by(col(WorkflowEvent.timestamp).desc())

        if event_key:
            query = query.where(WorkflowEvent.event_key == event_key)

        events = (await session.exec(query.limit(limit))).all()

        return [
            EventResponse(
                id=event.id,
                event_key=event.event_key,
                timestamp=event.timestamp.isoformat(),
                payload=event.payload,
                workflow_id=event.workflow_id,
            )
            for event in events
        ]
