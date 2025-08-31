from datetime import datetime
from enum import Enum
from typing import Any, Dict, List
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from planar.modeling.field_helpers import JsonSchema
from planar.workflows import Workflow
from planar.workflows.models import (
    StepStatus,
    StepType,
    WorkflowStatus,
)
from planar.workflows.step_metadata import StepMetadata


class EntityMetadata(BaseModel):
    name: str
    description: str | None = None
    json_schema: JsonSchema
    instance_count: int = 0


class EntityInstance(BaseModel):
    id: str
    entity_name: str
    data: dict[str, Any]


class EntityInstanceList(BaseModel):
    items: List[EntityInstance]
    total: int
    offset: int
    limit: int


class SortDirection(str, Enum):
    """Enum for sort direction options."""

    ASC = "asc"
    DESC = "desc"


# Models related to the workflow management REST API
class WorkflowStartResponse(BaseModel):
    id: UUID


class WorkflowStatusResponse(BaseModel):
    workflow: Workflow


class DurationStats(BaseModel):
    min_seconds: int | None = None
    avg_seconds: int | None = None
    max_seconds: int | None = None


class WorkflowRunStatusCounts(BaseModel):
    """Type-safe representation of workflow run status counts."""

    # Virtual statuses (computed, never persisted)
    running: int = 0
    suspended: int = 0

    # Persisted statuses (stored in database)
    pending: int = 0
    succeeded: int = 0
    failed: int = 0


class WorkflowDefinition(BaseModel):
    fully_qualified_name: str
    name: str
    description: str | None = None
    input_schema: JsonSchema | None = None
    output_schema: JsonSchema | None = None
    total_runs: int
    run_statuses: WorkflowRunStatusCounts
    durations: DurationStats | None = None


class StepStats(BaseModel):
    completed: int = 0
    failed: int = 0
    running: int = 0


class WorkflowRun(BaseModel):
    id: UUID
    status: WorkflowStatus
    args: List[Any] | None = None
    kwargs: Dict[str, Any] | None = None
    result: Any | None = None
    error: Dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
    step_stats: StepStats


class StepRunError(BaseModel):
    type: str
    message: str
    traceback: str | None = None


class WorkflowStepInfo(BaseModel):
    step_id: int
    is_internal_step: bool = Field(
        default=False,
        description="Whether the step is an internal Planar step, or a user-defined step",
    )
    parent_step_id: int | None = None
    workflow_id: UUID
    function_name: str
    display_name: str
    description: str | None = None
    step_type: StepType
    status: StepStatus
    args: List[Any] | None = None
    kwargs: Dict[str, Any] | None = None
    result: Any | None = None
    error: StepRunError | None = None
    retry_count: int
    created_at: datetime
    updated_at: datetime
    meta: StepMetadata | None = Field(
        default=None,
        description="Step type-specific rich data (e.g., human task details for human_in_the_loop steps)",
    )

    def model_post_init(self, __context: Any) -> None:
        if self.function_name.startswith("planar."):
            self.is_internal_step = True

    @staticmethod
    def get_display_name(custom_name: str | None, function_name: str) -> str:
        """
        If provided, use custom name, otherwise extract function name from a "fully qualified" function name.

        For example, 'module.directory.fn_name' becomes 'fn_name'.
        If there are no periods in the string, returns the original string.
        """
        return custom_name or function_name.split(".")[-1]

    @model_validator(mode="after")
    def validate_meta_step_type(self):
        """
        Make sure the outer step_type agrees with whatever subtype was
        chosen for `meta`. This runs *after* normal field validation,
        so `self.meta` is already an instantiated metadata object.
        """
        if self.meta is None:
            return self  # nothing to compare

        if self.step_type != self.meta.step_type:
            raise ValueError(
                f"meta.step_type={self.meta.step_type!r} does not match "
                f"outer step_type={self.step_type!r}"
            )
        return self


class WorkflowRunList(BaseModel):
    items: List[WorkflowRun]
    total: int
    offset: int | None
    limit: int | None


class WorkflowStepList(BaseModel):
    items: List[WorkflowStepInfo]
    total: int
    offset: int | None
    limit: int | None


class WorkflowList(BaseModel):
    items: List[WorkflowDefinition]
    total: int
    offset: int | None
    limit: int | None
