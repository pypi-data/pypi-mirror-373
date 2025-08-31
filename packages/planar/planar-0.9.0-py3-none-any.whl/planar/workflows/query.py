from typing import Any

from sqlalchemy import types
from sqlmodel import case, cast, col, literal, select
from sqlmodel import func as sql_func
from sqlmodel.ext.asyncio.session import AsyncSession

from planar.logging import get_logger
from planar.modeling.orm.query_filter_builder import build_paginated_query
from planar.routers.models import DurationStats
from planar.utils import utc_now
from planar.workflows import LockedResource, Workflow
from planar.workflows.models import WorkflowStatus, workflow_lock_join_cond


def build_effective_status_case():
    """Build SQL case expression for calculating effective workflow status."""
    now = utc_now()
    return case(
        # When lock_until is not null and in the future, it's RUNNING
        (
            (col(LockedResource.lock_until).isnot(None))
            & (col(LockedResource.lock_until) > now),
            literal("running"),
        ),
        # When wakeup_at is set or waiting_for_event is set, it's SUSPENDED
        (
            (col(Workflow.wakeup_at).isnot(None))
            | (col(Workflow.waiting_for_event).isnot(None)),
            literal("suspended"),
        ),
        else_=sql_func.lower(cast(Workflow.status, types.Text)),
    )


logger = get_logger(__name__)


async def get_bulk_workflow_run_statuses(
    workflow_names: list[str],
    session: AsyncSession,
    filters: list[tuple[Any, str, Any]] = [],
) -> dict[str, dict[WorkflowStatus, int]]:
    """
    Get the status counts for multiple workflows in a single query.
    """
    logger.debug(
        "getting bulk workflow run statuses",
        workflow_names=workflow_names,
        filters=filters,
    )
    if not workflow_names:
        return {}

    status_query = (
        select(
            col(Workflow.function_name).label("workflow_name"),
            build_effective_status_case().label("effective_status"),
            sql_func.count().label("count"),
        )
        .select_from(Workflow)
        .outerjoin(LockedResource, workflow_lock_join_cond())
        .where(col(Workflow.function_name).in_(workflow_names))
        .group_by(col(Workflow.function_name), "effective_status")
    )

    status_counts = (
        await session.exec(
            build_paginated_query(
                status_query,
                filters=filters,
            )[0]
        )
    ).all()
    logger.debug("raw status counts from db", status_counts=status_counts)

    # Group results by workflow name
    bulk_statuses: dict[str, dict[WorkflowStatus, int]] = {}
    for workflow_name, status_str, count in status_counts:
        if workflow_name not in bulk_statuses:
            bulk_statuses[workflow_name] = {}

        # Convert the status string directly to WorkflowStatus enum
        try:
            status = WorkflowStatus(status_str)
            bulk_statuses[workflow_name][status] = count
        except ValueError:
            # Skip invalid status strings (shouldn't happen with valid data)
            logger.exception(
                "invalid status string encountered for workflow",
                status_str=status_str,
                workflow_name=workflow_name,
            )
            pass

    # Ensure all requested workflows have an entry, even if empty
    for workflow_name in workflow_names:
        if workflow_name not in bulk_statuses:
            bulk_statuses[workflow_name] = {}

    logger.debug("returning bulk statuses", bulk_statuses=bulk_statuses)
    return bulk_statuses


async def get_workflow_run_statuses(
    workflow_name: str, session: AsyncSession, filters: list[tuple[Any, str, Any]] = []
) -> dict[WorkflowStatus, int]:
    """
    Get the status counts for a workflow.
    """
    bulk_result = await get_bulk_workflow_run_statuses(
        [workflow_name], session, filters
    )
    return bulk_result.get(workflow_name, {})


async def calculate_bulk_workflow_duration_stats(
    workflow_names: list[str],
    session: AsyncSession,
    filters: list[tuple[Any, str, Any]] = [],
) -> dict[str, DurationStats | None]:
    """Calculate min, avg, and max execution duration for multiple workflows in a single query."""
    logger.debug(
        "calculating bulk workflow duration stats",
        workflow_names=workflow_names,
        filters=filters,
    )
    if not workflow_names:
        return {}

    duration_query = (
        select(
            col(Workflow.function_name).label("workflow_name"),
            sql_func.cast(
                sql_func.min(
                    (
                        sql_func.extract("epoch", col(Workflow.updated_at))
                        - sql_func.extract("epoch", col(Workflow.created_at))
                    )
                ),
                types.Integer,
            ).label("min_duration"),
            sql_func.cast(
                sql_func.avg(
                    (
                        sql_func.extract("epoch", col(Workflow.updated_at))
                        - sql_func.extract("epoch", col(Workflow.created_at))
                    )
                ),
                types.Integer,
            ).label("avg_duration"),
            sql_func.cast(
                sql_func.max(
                    (
                        sql_func.extract("epoch", col(Workflow.updated_at))
                        - sql_func.extract("epoch", col(Workflow.created_at))
                    )
                ),
                types.Integer,
            ).label("max_duration"),
        )
        .where(
            col(Workflow.function_name).in_(workflow_names),
            (
                (Workflow.status == WorkflowStatus.SUCCEEDED)
                | (Workflow.status == WorkflowStatus.FAILED)
            ),
        )
        .group_by(col(Workflow.function_name))
    )

    completed_workflows = (
        await session.exec(
            build_paginated_query(
                duration_query,
                filters=filters,
            )[0]
        )
    ).all()
    logger.debug("raw duration stats from db", completed_workflows=completed_workflows)

    # Group results by workflow name
    bulk_durations: dict[str, DurationStats | None] = {}
    for workflow_name, min_duration, avg_duration, max_duration in completed_workflows:
        if min_duration is not None:
            bulk_durations[workflow_name] = DurationStats(
                min_seconds=min_duration,
                avg_seconds=avg_duration,
                max_seconds=max_duration,
            )
        else:
            bulk_durations[workflow_name] = None

    # Ensure all requested workflows have an entry, even if None
    for workflow_name in workflow_names:
        if workflow_name not in bulk_durations:
            bulk_durations[workflow_name] = None

    logger.debug("returning bulk durations", bulk_durations=bulk_durations)
    return bulk_durations


async def calculate_workflow_duration_stats(
    session: AsyncSession, function_name: str, filters: list[tuple[Any, str, Any]] = []
) -> DurationStats | None:
    """Calculate min, avg, and max execution duration for a workflow."""
    bulk_result = await calculate_bulk_workflow_duration_stats(
        [function_name], session, filters
    )
    return bulk_result.get(function_name)


async def calculate_effective_status(
    session: AsyncSession, workflow: Workflow
) -> WorkflowStatus:
    """Calculate the effective status for a workflow, considering virtual states."""
    logger.debug("calculating effective status for workflow", workflow_id=workflow.id)
    effective_status_str = (
        await session.exec(
            select(build_effective_status_case())
            .select_from(Workflow)
            .outerjoin(LockedResource, workflow_lock_join_cond())
            .where(Workflow.id == workflow.id)
        )
    ).first()
    logger.debug(
        "effective status string from db for workflow",
        workflow_id=workflow.id,
        effective_status_str=effective_status_str,
    )

    # Convert the status string directly to WorkflowStatus enum
    if effective_status_str is None:
        logger.debug(
            "effective status string is none, returning original status",
            original_status=workflow.status,
        )
        return workflow.status

    try:
        status = WorkflowStatus(effective_status_str)
        logger.debug(
            "converted effective status for workflow",
            workflow_id=workflow.id,
            status=status,
        )
        return status
    except ValueError:
        # Fallback to the workflow's actual status if conversion fails
        logger.exception(
            "invalid effective status string, falling back to actual status",
            effective_status_str=effective_status_str,
            workflow_id=workflow.id,
            actual_status=workflow.status,
        )
        return workflow.status
