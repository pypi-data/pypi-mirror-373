from sqlmodel import col, select

from planar.session import get_session
from planar.workflows.models import WorkflowStep


async def get_step_parent(step: WorkflowStep) -> WorkflowStep | None:
    """Get the parent step of the given step.

    Args:
        step: The step to get the parent of

    Returns:
        The parent step, or None if the step has no parent
    """
    if step.parent_step_id is None:
        return None

    session = get_session()
    return (
        await session.exec(
            select(WorkflowStep)
            .where(col(WorkflowStep.workflow_id) == step.workflow_id)
            .where(col(WorkflowStep.step_id) == step.parent_step_id)
        )
    ).first()


async def get_step_children(step: WorkflowStep) -> list[WorkflowStep]:
    """Get all direct child steps of the given step.

    Args:
        step: The step to get the children of

    Returns:
        A list of child steps
    """
    session = get_session()
    result = await session.exec(
        select(WorkflowStep)
        .where(col(WorkflowStep.workflow_id) == step.workflow_id)
        .where(col(WorkflowStep.parent_step_id) == step.step_id)
    )
    return list(result.all())


async def get_step_descendants(step: WorkflowStep) -> list[WorkflowStep]:
    """Get all descendant steps (children, grandchildren, etc.) of the given step.

    Args:
        step: The step to get the descendants of

    Returns:
        A list of all descendant steps
    """
    descendants = await get_step_children(step)
    result_descendants = descendants.copy()

    # For each child, recursively get their descendants
    for child in descendants:
        child_descendants = await get_step_descendants(child)
        result_descendants.extend(child_descendants)

    return result_descendants


async def get_step_ancestors(step: WorkflowStep) -> list[WorkflowStep]:
    """Get all ancestor steps (parent, grandparent, etc.) of the given step.

    Args:
        step: The step to get the ancestors of

    Returns:
        A list of all ancestor steps, ordered from parent to oldest ancestor
    """
    ancestors = []
    current = step

    while current.parent_step_id is not None:
        parent = await get_step_parent(current)
        if parent is None:
            break
        ancestors.append(parent)
        current = parent

    return ancestors
