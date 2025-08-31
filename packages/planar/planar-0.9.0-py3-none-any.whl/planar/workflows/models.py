from datetime import datetime
from enum import Enum
from typing import Any, Dict, cast
from uuid import UUID, uuid4

from sqlalchemy import types
from sqlmodel import (
    JSON,
    Column,
    Field,
    Integer,
    col,
    func,
    literal,
)

from planar.db import PlanarInternalBase
from planar.modeling.mixins import TimestampMixin, timestamp_column


class StepStatus(str, Enum):
    SUCCEEDED = "succeeded"  # has finished execution
    RUNNING = "running"  # step currently running
    FAILED = "failed"  # Has encountered an error


class StepType(str, Enum):
    COMPUTE = "compute"
    AGENT = "agent"
    RULE = "rule"
    HUMAN_IN_THE_LOOP = "human_in_the_loop"
    TOOL_CALL = "tool_call"


class WorkflowStatus(str, Enum):
    # Persisted statuses (stored in database)
    PENDING = "pending"  # waiting to be executed
    SUCCEEDED = "succeeded"  # has finished execution
    FAILED = "failed"  # Has encountered an error

    # Virtual statuses (computed from other fields, never persisted)
    RUNNING = "running"  # currently running (computed from lock_until field)
    SUSPENDED = "suspended"  # waiting for event or wakeup time (computed from wakeup_at or waiting_for_event fields)


class Workflow(PlanarInternalBase, TimestampMixin, table=True):
    """
    Represents a workflow instance with its execution state.
    """

    function_name: str
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    parent_id: UUID | None = Field(
        default=None, index=True, foreign_key="planar.workflow.id"
    )
    status: WorkflowStatus = Field(default=WorkflowStatus.PENDING, index=True)
    args: list[Any] | None = Field(sa_column=Column(JSON))
    kwargs: Dict[str, Any] | None = Field(sa_column=Column(JSON))
    result: Any | None = Field(sa_column=Column(JSON), default=None)
    error: Dict[str, Any] | None = Field(sa_column=Column(JSON), default=None)
    wakeup_at: datetime | None = Field(default=None, nullable=True, index=True)
    # Event key this workflow is waiting for, if any
    waiting_for_event: str | None = Field(default=None, index=True)


class WorkflowStep(PlanarInternalBase, TimestampMixin, table=True):
    """
    Represents a single step within a workflow execution.
    """

    step_id: int = Field(primary_key=True)
    workflow_id: UUID = Field(primary_key=True, foreign_key="planar.workflow.id")
    parent_step_id: int | None = Field(default=None, index=True)
    function_name: str
    display_name: str | None = Field(
        default=None,
        description="Custom display name, for scenarios where we don't want to use the simplified function name as the display name",
    )
    status: StepStatus = Field(default=StepStatus.RUNNING)
    step_type: StepType
    args: list[Any] | None = Field(sa_column=Column(JSON))
    kwargs: Dict[str, Any] | None = Field(sa_column=Column(JSON))
    result: Any | None = Field(sa_column=Column(JSON), default=None)
    sub_step_count: int = Field(default=0)
    error: Dict[str, Any] | None = Field(sa_column=Column(JSON), default=None)
    retry_count: int = Field(default=0)


class WorkflowEvent(PlanarInternalBase, table=True):
    """
    Immutable record of events that workflows might be waiting for.
    Events form an append-only log that the workflow orchestrator can use
    to identify and wake up workflows that are waiting for specific events.
    """

    # Unique identifier for this event occurrence
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Event type identifier (e.g., "order_approved", "payment_received")
    event_key: str = Field(index=True)

    # Optional association with a specific workflow
    workflow_id: UUID | None = Field(
        default=None, index=True, foreign_key="planar.workflow.id"
    )

    # Optional payload data associated with the event
    payload: Dict[str, Any] | None = Field(sa_column=Column(JSON), default=None)

    # When the event was created
    timestamp: datetime = timestamp_column(index=True)


class LockedResource(PlanarInternalBase, table=True):
    """
    Represents a locked resource with expiration.
    Used for workflow execution locks and other concurrency control mechanisms.
    """

    lock_key: str = Field(primary_key=True)

    # lock_until field is used to ensure that workflows are not stuck if a worker crashes
    # after setting the status to RUNNING, but before setting the status to SUCCESS or FAILED
    lock_until: datetime | None = Field(default=None, nullable=True, index=True)

    # Enable SQLAlchemy row version tracking to detect concurrency conflicts
    version_id: int = Field(default=1, sa_column=Column(Integer, nullable=False))
    __mapper_args__ = {"version_id_col": cast(Any, version_id).sa_column}


__WORKFLOW_EXEC_LOCK_PREFIX = "workflow-execution:"


def workflow_exec_lock_key(workflow_id: UUID) -> str:
    return __WORKFLOW_EXEC_LOCK_PREFIX + str(workflow_id).replace("-", "").lower()


def workflow_lock_join_cond():
    # Join condition for getting locked workflows in a query.

    return col(LockedResource.lock_key) == (
        literal(__WORKFLOW_EXEC_LOCK_PREFIX)
        # SQLite uses strings for UUID columns, but it removes all "-"
        # characters It is possible that some dbs with native UUID support will
        # have "-" after converting to string, so we remove them here to make
        # the comparison consistent
        + func.lower(
            func.replace(
                func.cast(col(Workflow.id), types.Text),
                "-",
                "",
            )
        )
    )
