"""
Event system for workflow engine.

This module provides functions for emitting and checking events that workflows
might be waiting for.
"""

from datetime import datetime
from typing import Any, Dict, Optional, cast
from uuid import UUID, uuid4

from sqlmodel import col, select, update

from planar.logging import get_logger
from planar.session import get_session
from planar.workflows.models import Workflow, WorkflowEvent
from planar.workflows.orchestrator import WorkflowOrchestrator
from planar.workflows.tracing import trace

logger = get_logger(__name__)


async def emit_event(
    event_key: str,
    payload: Optional[Dict[str, Any]] = None,
    workflow_id: Optional[UUID] = None,
) -> tuple[WorkflowEvent, int]:
    """
    Emit a new event that workflows might be waiting for.

    Args:
        event_key: The event identifier
        payload: Optional data to include with the event
        workflow_id: Optional workflow ID if the event is targeted at a specific workflow

    Returns:
        The created event record
    """
    logger.debug(
        "emitting event",
        event_key=event_key,
        workflow_id=str(workflow_id),
        payload_keys=list(payload.keys()) if payload else None,
    )
    await trace("enter", event_key=event_key)
    session = get_session()

    select_condition = col(Workflow.waiting_for_event) == event_key
    if workflow_id:
        select_condition &= col(Workflow.id) == workflow_id
    update_query = (
        update(Workflow)
        .where(select_condition)
        .values(waiting_for_event=None, wakeup_at=None)
        .returning(col(Workflow.id))
    )

    async def transaction():
        # Update affected events
        workflow_ids = (await session.exec(cast(Any, update_query))).all()
        logger.info(
            "event woke up workflows", event_key=event_key, count=len(workflow_ids)
        )
        await trace(
            "wake-affected-workflows", event_key=event_key, count=len(workflow_ids)
        )
        # Create the event record
        event = WorkflowEvent(
            id=uuid4(),
            event_key=event_key,
            workflow_id=workflow_id,
            payload=payload or {},
        )
        session.add(event)
        logger.debug("event record created", event_key=event_key, event_id=event.id)
        await trace("add-event-record", event_key=event_key)

        return event, workflow_ids

    event, workflow_ids = await session.run_transaction(transaction)
    await trace("commit", event_key=event_key)
    logger.info("event committed to database", event_key=event_key, event_id=event.id)

    if workflow_ids and WorkflowOrchestrator.is_set():
        logger.debug("requesting orchestrator poll due to event", event_key=event_key)
        WorkflowOrchestrator.get().poll_soon()

    await trace("return", event_key=event_key)
    return event, len(workflow_ids)


async def check_event_exists(
    event_key: str, since: Optional[datetime] = None, workflow_id: Optional[UUID] = None
) -> bool:
    """
    Check if an event with the given key exists, optionally after a specific time.

    Args:
        event_key: The event identifier
        since: Only consider events after this time
        workflow_id: Optional workflow ID to check for workflow-specific events

    Returns:
        True if a matching event exists, False otherwise
    """
    logger.debug(
        "checking if event exists",
        event_key=event_key,
        since=since,
    )
    session = get_session()

    # Start building the query
    query = select(WorkflowEvent).where(WorkflowEvent.event_key == event_key)

    # If a timestamp is provided, only check for events after that time
    if since:
        query = query.where(WorkflowEvent.timestamp > since)

    # If a workflow ID is provided, check for events specific to that workflow
    # or global events (no workflow ID)
    if workflow_id:
        query = query.where(
            (col(WorkflowEvent.workflow_id) == workflow_id)
            | (col(WorkflowEvent.workflow_id).is_(None))
        )

    # Execute the query and check if any result exists
    event = (await session.exec(query)).first()
    exists = event is not None
    logger.debug("event exists check result", event_key=event_key, exists=exists)
    return exists


async def get_latest_event(
    event_key: str, since: Optional[datetime] = None, workflow_id: Optional[UUID] = None
) -> Optional[WorkflowEvent]:
    """
    Get the most recent event with the given key.

    Args:
        event_key: The event identifier
        since: Only consider events after this time
        workflow_id: Optional workflow ID to check for workflow-specific events

    Returns:
        The most recent matching event, or None if no match found
    """
    logger.debug(
        "getting latest event",
        event_key=event_key,
        since=since,
    )
    session = get_session()

    # Start building the query
    query = select(WorkflowEvent).where(WorkflowEvent.event_key == event_key)

    # If a timestamp is provided, only check for events after that time
    if since:
        query = query.where(WorkflowEvent.timestamp > since)

    # If a workflow ID is provided, check for events specific to that workflow
    # or global events (no workflow ID)
    if workflow_id:
        query = query.where(
            (col(WorkflowEvent.workflow_id) == workflow_id)
            | (col(WorkflowEvent.workflow_id).is_(None))
        )

    # Order by timestamp descending and get the first (most recent) result
    query = query.order_by(col(WorkflowEvent.timestamp).desc())

    # Execute the query and return the first result (or None)
    event = (await session.exec(query)).first()
    if event:
        logger.debug(
            "latest event found",
            event_key=event_key,
            event_id=event.id,
            timestamp=event.timestamp,
        )
    else:
        logger.debug("no event found with given criteria", event_key=event_key)
    return event
