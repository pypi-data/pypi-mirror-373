from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, distinct, func, select

from planar.human.models import HumanTask, HumanTaskStatus
from planar.logging import get_logger
from planar.object_config import ConfigurableObjectType, ObjectConfiguration
from planar.session import get_session
from planar.workflows.models import Workflow, WorkflowStatus

logger = get_logger(__name__)


class SystemInfo(BaseModel):
    """Combined application information and system statistics"""

    # App info
    title: str
    description: str

    # System stats
    total_workflow_runs: int = 0
    completed_runs: int = 0
    in_progress_runs: int = 0
    pending_human_tasks: int = 0
    active_agents: int = 0


async def get_system_stats(session: AsyncSession = Depends(get_session)) -> dict:
    """
    Get system-wide statistics directly from the database.

    This optimizes the calculation by doing aggregations at the database level
    rather than fetching all records and calculating in the application.
    """
    try:
        # Get workflow run counts
        workflow_stats = await session.execute(
            select(
                func.count().label("total_runs"),
                func.count(col(Workflow.id))
                .filter(col(Workflow.status) == WorkflowStatus.SUCCEEDED)
                .label("completed_runs"),
                func.count(col(Workflow.id))
                .filter(col(Workflow.status) == WorkflowStatus.PENDING)
                .label("in_progress_runs"),
            ).select_from(Workflow)
        )
        workflow_row = workflow_stats.one()

        # Get pending human task count
        human_task_query = await session.execute(
            select(func.count())
            .select_from(HumanTask)
            .where(HumanTask.status == HumanTaskStatus.PENDING)
        )
        pending_tasks = human_task_query.scalar() or 0

        # Get agent count from the registry or count distinct agent configs
        agent_count = 0
        try:
            # Count distinct agent names in the AgentConfig table
            agent_query = await session.execute(
                select(
                    func.count(distinct(ObjectConfiguration.object_name))
                ).select_from(
                    select(ObjectConfiguration)
                    .where(
                        ObjectConfiguration.object_type == ConfigurableObjectType.AGENT
                    )
                    .subquery()
                )
            )
            agent_count = agent_query.scalar() or 0
        except Exception:
            logger.exception("error counting agents")
            # Fallback to 0
            agent_count = 0

        # Return stats dict
        return {
            "total_workflow_runs": workflow_row.total_runs or 0,
            "completed_runs": workflow_row.completed_runs or 0,
            "in_progress_runs": workflow_row.in_progress_runs or 0,
            "pending_human_tasks": pending_tasks,
            "active_agents": agent_count,
        }
    except Exception:
        logger.exception("error fetching system stats")
        # Return default stats if there's an error
        return {
            "total_workflow_runs": 0,
            "completed_runs": 0,
            "in_progress_runs": 0,
            "pending_human_tasks": 0,
            "active_agents": 0,
        }


def create_info_router(title: str, description: str) -> APIRouter:
    """
    Create a router for serving combined application information and system statistics.

    This router provides a single endpoint to retrieve the application's title,
    description, and system-wide statistics on workflow runs, human tasks,
    and registered agents.

    Args:
        title: The application title
        description: The application description

    Returns:
        An APIRouter instance with a combined info route
    """
    router = APIRouter()

    @router.get("/system-info", response_model=SystemInfo)
    async def get_system_info(
        session: AsyncSession = Depends(get_session),
    ) -> SystemInfo:
        """
        Get combined application information and system statistics.

        Returns:
            SystemInfo object containing app details and system stats
        """
        stats = await get_system_stats(session)
        return SystemInfo(title=title, description=description, **stats)

    return router
