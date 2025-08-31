"""
Human-in-the-loop step implementation for Planar workflows.

This module provides the Human class for creating human task instances,
along with supporting entities and functions for managing human tasks.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Type, overload
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import col, select

from planar.human.models import HumanTask, HumanTaskResult, HumanTaskStatus
from planar.logging import get_logger
from planar.session import get_session
from planar.utils import utc_now
from planar.workflows import as_step
from planar.workflows.context import get_context
from planar.workflows.contrib import wait_for_event
from planar.workflows.events import emit_event
from planar.workflows.models import StepType

logger = get_logger(__name__)


class Timeout:
    """Helper class for defining timeout periods for human tasks."""

    def __init__(self, duration: timedelta):
        """
        Initialize timeout with a duration.

        Args:
            duration: The timeout duration as a timedelta
        """
        self.duration = duration

    def get_seconds(self) -> float:
        """
        Get the timeout duration in seconds.

        Returns:
            Timeout duration in seconds
        """
        return self.duration.total_seconds()

    def get_timedelta(self) -> timedelta:
        """
        Get the timeout duration as a timedelta.

        Returns:
            Timeout duration as a timedelta
        """
        return self.duration


class Human[TInput: BaseModel, TOutput: BaseModel]:
    """
    Human-in-the-loop task for workflows.

    Creates a callable task object that:
    1. Creates a HumanTask record
    2. Suspends workflow using event system
    3. Returns structured data when human completes the task
    """

    def __init__(
        self,
        name: str,
        title: str,
        output_type: Type[TOutput],
        description: Optional[str] = None,
        input_type: Type[TInput] | None = None,
        timeout: Optional[Timeout] = None,
    ):
        """
        Initialize a human task definition.

        Args:
            name: Unique identifier for this task
            title: Human-readable title
            output_type: Pydantic model for expected output (required)
            description: Detailed task description (optional)
            input_type: Pydantic model for input data (optional)
            timeout: Maximum time to wait for human input (optional)
        """
        self.name = name
        self.title = title
        self.description = description
        self.input_type = input_type
        self.output_type = output_type
        self.timeout = timeout

        if self.input_type and not issubclass(self.input_type, BaseModel):
            raise ValueError("input_type must be a Pydantic model or None")
        if not issubclass(self.output_type, BaseModel):
            raise ValueError("output_type must be a Pydantic model")

    @overload
    async def __call__(
        self,
        input_data: TInput,
        message: str | None = None,
        suggested_data: TOutput | None = None,
    ) -> HumanTaskResult[TOutput]: ...

    @overload
    async def __call__(
        self, *, message: str, suggested_data: TOutput | None = None
    ) -> HumanTaskResult[TOutput]: ...

    async def __call__(
        self,
        input_data: TInput | None = None,
        message: str | None = None,
        suggested_data: TOutput | None = None,
    ) -> HumanTaskResult[TOutput]:
        logger.debug(
            "human task called",
            task_name=self.name,
            has_input=input_data is not None,
            has_message=message is not None,
            has_suggestion=suggested_data is not None,
        )
        if self.output_type is None:
            raise ValueError("output_type must be provided")
        run_step = as_step(
            self.run_step,
            step_type=StepType.HUMAN_IN_THE_LOOP,
            display_name=self.name,
            return_type=HumanTaskResult[self.output_type],
        )
        return await run_step(input_data, message, suggested_data)

    async def run_step(
        self,
        input_data: TInput | None = None,
        message: str | None = None,
        suggested_data: TOutput | None = None,
    ) -> HumanTaskResult[TOutput]:
        """
        Create a human task and wait for completion.

        Can be called with either (or both of):
        1. A Pydantic model instance of input_type
        2. A context message string for display to the human

        Args:
            input_data: Context data for the human task
            message: Optional message to display to the human
            suggested_data: Optional pre-filled data conforming to output_type

        Returns:
            HumanTaskResult containing the human's response
        """
        logger.debug("human task run_step executing", task_name=self.name)
        if input_data is None and message is None:
            logger.warning(
                "human task called without input_data or message", task_name=self.name
            )
            raise ValueError("Either input_data or message must be provided")

        # Create task in database
        logger.debug("creating human task record", task_name=self.name)
        task_id = await as_step(
            self._create_task,
            step_type=StepType.HUMAN_IN_THE_LOOP,
            display_name="Create Human Task",
        )(input_data, message, suggested_data)
        logger.info("human task record created", task_name=self.name, task_id=task_id)

        # Wait for task completion event
        event_key = f"human_task_completed:{task_id}"
        max_wait_seconds = self.timeout.get_seconds() if self.timeout else -1
        logger.debug(
            "waiting for event",
            event_key=event_key,
            task_name=self.name,
            timeout_seconds=max_wait_seconds,
        )
        # TODO: Catch timeout exception on event, expire human task and raise timeout error
        event_data = await wait_for_event(
            event_key=event_key, max_wait_time=max_wait_seconds
        )
        logger.info("event received for task", event_key=event_key, task_name=self.name)

        # Return structured result
        return HumanTaskResult(
            task_id=task_id,
            output=self.output_type.model_validate(event_data["output_data"]),
            completed_at=datetime.fromisoformat(event_data["completed_at"]),
        )

    async def _create_task(
        self,
        input_data: TInput | None = None,
        message: str | None = None,
        suggested_data: TOutput | None = None,
    ) -> UUID:
        """
        Create the human task record in the database.
        This is a separate step for replay safety.

        Args:
            input_data: Context data for the human task
            message: Optional message to display to the human
            suggested_data: Optional pre-filled data conforming to output_type

        Returns:
            UUID of the created human task
        """
        logger.debug("human task _create_task executing", task_name=self.name)
        # Get workflow context
        ctx = get_context()
        session = get_session()

        if input_data is not None:
            if isinstance(input_data, BaseModel):
                if self.input_type and not isinstance(input_data, self.input_type):
                    logger.warning(
                        "input type mismatch for human task",
                        task_name=self.name,
                        expected_type=self.input_type,
                        got_type=type(input_data),
                    )
                    raise ValueError(
                        f"Input must be of type {self.input_type}, but got {type(input_data)}"
                    )

        # Create HumanTask record
        task = HumanTask(
            name=self.name,
            title=self.title,
            description=self.description,
            workflow_id=ctx.workflow.id,
            workflow_name=ctx.workflow.function_name,
            input_schema=self.input_type.model_json_schema()
            if self.input_type
            else None,
            input_data=input_data.model_dump(mode="json") if input_data else None,
            message=message,
            output_schema=self.output_type.model_json_schema(),
            suggested_data=suggested_data.model_dump(mode="json")
            if suggested_data
            else None,
            deadline=self._calculate_deadline(),
            status=HumanTaskStatus.PENDING,
        )

        # Persist to database
        session.add(task)
        await session.commit()
        logger.info(
            "human task persisted to database", task_name=self.name, task_id=task.id
        )

        return task.id

    def _calculate_deadline(self) -> Optional[datetime]:
        """
        Calculate the task deadline based on timeout.

        Returns:
            Deadline as a UTC datetime or None if no timeout
        """
        if not self.timeout:
            return None

        return utc_now() + self.timeout.get_timedelta()


async def complete_human_task(
    task_id: UUID, output_data: Dict[str, Any], completed_by: Optional[str] = None
) -> None:
    """
    Complete a human task and trigger workflow resumption.

    Args:
        task_id: The task to complete
        output_data: The human's response
        completed_by: Optional identifier for who completed the task

    Raises:
        ValueError: If task not found or not in pending status
    """
    logger.debug("completing human task", task_id=task_id, completed_by=completed_by)
    # Find the task
    session = get_session()
    task = await session.get(HumanTask, task_id)
    if not task:
        logger.warning("human task not found for completion", task_id=task_id)
        raise ValueError(f"Task {task_id} not found")

    # Validate task can be completed
    if task.status != HumanTaskStatus.PENDING:
        logger.warning(
            "attempt to complete human task not in pending status",
            task_id=task_id,
            status=task.status,
        )
        raise ValueError(f"Task {task_id} is not pending (status: {task.status})")

    # TODO: Validate output against schema
    # This would validate output_data against task.output_schema

    # Update task
    completed_at = utc_now()
    task.status = HumanTaskStatus.COMPLETED
    task.output_data = output_data
    task.completed_at = completed_at
    task.completed_by = completed_by or "anonymous"
    session.add(task)
    await session.commit()
    logger.info("human task marked as completed", task_id=task_id)

    # Emit completion event to resume workflow
    event_key = f"human_task_completed:{task_id}"
    logger.debug(
        "emitting completion event for task", event_key=event_key, task_id=task_id
    )
    await emit_event(
        event_key=event_key,
        payload={
            "task_id": str(task_id),
            "output_data": output_data,
            "completed_at": completed_at.isoformat(),
        },
        workflow_id=task.workflow_id,
    )


async def cancel_human_task(
    task_id: UUID, reason: str = "cancelled", cancelled_by: Optional[str] = None
) -> None:
    """
    Cancel a pending human task.

    Args:
        task_id: The task to cancel
        reason: Reason for cancellation
        cancelled_by: Optional identifier for who cancelled the task

    Raises:
        ValueError: If task not found or not in pending status
    """
    logger.debug(
        "cancelling human task",
        task_id=task_id,
        reason=reason,
        cancelled_by=cancelled_by,
    )
    # Find the task
    session = get_session()
    task = await session.get(HumanTask, task_id)
    if not task:
        logger.warning("human task not found for cancellation", task_id=task_id)
        raise ValueError(f"Task {task_id} not found")

    # Validate task can be cancelled
    if task.status != HumanTaskStatus.PENDING:
        logger.warning(
            "attempt to cancel human task not in pending status",
            task_id=task_id,
            status=task.status,
        )
        raise ValueError(f"Task {task_id} is not pending (status: {task.status})")

    # Update task
    cancelled_at = utc_now()
    task.status = HumanTaskStatus.CANCELLED
    task.completed_at = cancelled_at
    task.completed_by = cancelled_by or "system"
    # Store cancellation reason in output_data
    task.output_data = {"cancelled": True, "reason": reason}
    session.add(task)
    await session.commit()
    logger.info("human task marked as cancelled", task_id=task_id)

    # Emit cancellation event to resume workflow
    event_key = (
        f"human_task_completed:{task_id}"  # Note: Uses same event key as completion
    )
    logger.debug(
        "emitting cancellation event for task", event_key=event_key, task_id=task_id
    )
    await emit_event(
        event_key=event_key,
        payload={
            "task_id": str(task_id),
            "output_data": {"cancelled": True, "reason": reason},
            "completed_at": cancelled_at.isoformat(),
        },
        workflow_id=task.workflow_id,
    )


async def get_human_tasks(
    status: Optional[HumanTaskStatus] = None,
    workflow_id: Optional[UUID] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[HumanTask]:
    """
    Get human tasks matching the given filters.

    Args:
        status: Filter by task status
        workflow_id: Filter by workflow ID
        limit: Maximum number of tasks to return
        offset: Offset for pagination

    Returns:
        List of human tasks
    """
    logger.debug(
        "getting human tasks",
        status=status,
        limit=limit,
        offset=offset,
    )
    session = get_session()
    query = select(HumanTask)

    if status:
        query = query.where(col(HumanTask.status) == status)

    if workflow_id:
        query = query.where(col(HumanTask.workflow_id) == workflow_id)

    # Order by creation time, newest first
    query = query.order_by(col(HumanTask.created_at).desc())
    query = query.offset(offset).limit(limit)

    tasks = list((await session.exec(query)).all())
    logger.debug("found human tasks matching criteria", count=len(tasks))
    return tasks


async def get_human_task(task_id: UUID) -> HumanTask | None:
    """
    Get a human task by ID.

    Args:
        task_id: The task ID

    Returns:
        The human task or None if not found
    """
    logger.debug("getting human task by id", task_id=task_id)
    session = get_session()
    task = await session.get(HumanTask, task_id)
    if task:
        logger.debug("found human task", task_id=task_id)
    else:
        logger.debug("human task not found", task_id=task_id)
    return task
