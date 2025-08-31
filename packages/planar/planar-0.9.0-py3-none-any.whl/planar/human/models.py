from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import JSON, Column, Field

from planar.db import PlanarInternalBase
from planar.modeling.field_helpers import JsonSchema
from planar.modeling.mixins import TimestampMixin
from planar.modeling.mixins.auditable import AuditableMixin
from planar.modeling.mixins.uuid_primary_key import UUIDPrimaryKeyMixin


class HumanTaskStatus(str, Enum):
    """Status values for human tasks."""

    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class HumanTask(
    UUIDPrimaryKeyMixin, AuditableMixin, PlanarInternalBase, TimestampMixin, table=True
):
    """
    Database model for human tasks that require input from a human operator.

    Extends UUIDPrimaryKeyMixin which provides:
    - id: Primary key

    Extends AuditableMixin which provides:
    - created_by, updated_by: Audit fields

    And TimeStampMixin which provides:
    - created_at, updated_at: Timestamp fields
    """

    # Task identifying information
    name: str = Field(index=True)
    title: str
    description: Optional[str] = None

    # Workflow association
    workflow_id: UUID = Field(index=True)
    workflow_name: str

    # Input data for context
    input_schema: Optional[JsonSchema] = Field(default=None, sa_column=Column(JSON))
    input_data: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    message: Optional[str] = Field(default=None)

    # Schema for expected output
    output_schema: JsonSchema = Field(sa_column=Column(JSON))
    output_data: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    # Suggested data for the form (optional)
    suggested_data: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )

    # Task status
    status: HumanTaskStatus = Field(default=HumanTaskStatus.PENDING)

    # Completion tracking
    completed_by: Optional[str] = None
    completed_at: Optional[datetime] = None

    # Time constraints
    deadline: Optional[datetime] = None


class HumanTaskResult[TOutput: BaseModel](BaseModel):
    """Result of a completed human task."""

    task_id: UUID
    output: TOutput
    completed_at: datetime
