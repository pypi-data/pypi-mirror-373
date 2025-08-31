from dataclasses import dataclass, field
from uuid import UUID

from planar.task_local import TaskLocal
from planar.workflows.models import Workflow, WorkflowStep


@dataclass(kw_only=True)
class ExecutionContext:
    workflow: Workflow
    # This might seem redundant, but it is actually necessary to prevent
    # implicit DB calls when accessing ctx.workflow.id which causes greenlet
    # I/O errors with async SQLAlchemy. This can happen for example when a
    # rollback is issued, which causes SQLAlchemy to expire the objects managed
    # by the session.
    workflow_id: UUID
    current_step_id: int = 0
    step_stack: list[WorkflowStep] = field(default_factory=list)
    # The start_workflow helper (decorators.py) has
    # the same parameters as the original function,
    # so we can't pass this as an argument. Instead
    # we use a context variable to signal that the
    # started workflow should set this one as the
    # parent.
    bind_parent_workflow: bool = False


data: TaskLocal[ExecutionContext] = TaskLocal()


def in_context() -> bool:
    return data.is_set()


def get_context() -> ExecutionContext:
    return data.get()


def set_context(ctx: ExecutionContext):
    return data.set(ctx)


def delete_context():
    return data.clear()
