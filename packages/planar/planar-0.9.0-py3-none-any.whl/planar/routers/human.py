"""
Human tasks API router for Planar workflows.

This module provides API routes for managing human task instances,
including task listing, completion, cancellation, and retrieval.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel

from planar.human.human import (
    HumanTask,
    HumanTaskStatus,
    cancel_human_task,
    complete_human_task,
    get_human_task,
    get_human_tasks,
)
from planar.logging import get_logger

logger = get_logger(__name__)


class CompleteTaskRequest(BaseModel):
    """Request model for completing a human task."""

    output_data: Dict[str, Any]
    completed_by: Optional[str] = None


class CancelTaskRequest(BaseModel):
    """Request model for cancelling a human task."""

    reason: str = "cancelled"
    cancelled_by: Optional[str] = None


def create_human_task_routes() -> APIRouter:
    router = APIRouter(tags=["Human Tasks"])

    """Register human task routes on the provided router and return it."""

    @router.get("/", response_model=List[HumanTask])
    async def list_human_tasks(
        status: Optional[HumanTaskStatus] = None,
        workflow_id: Optional[UUID] = None,
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
    ):
        """
        List human tasks with optional filtering.

        Args:
            status: Filter by task status
            workflow_id: Filter by workflow ID
            limit: Maximum number of tasks to return
            offset: Pagination offset
        """
        try:
            tasks = await get_human_tasks(
                status=status,
                workflow_id=workflow_id,
                limit=limit,
                offset=offset,
            )
            return tasks
        except Exception as e:
            logger.exception("error listing human tasks")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/{task_id}", response_model=HumanTask)
    async def get_task(task_id: UUID):
        """
        Get a human task by its ID.

        Args:
            task_id: The ID of the task to retrieve
        """
        task = await get_human_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        return task

    @router.post("/{task_id}/complete", response_model=HumanTask)
    async def complete_task(task_id: UUID, request: CompleteTaskRequest = Body(...)):
        """
        Complete a human task with the provided output data.

        Args:
            task_id: The ID of the task to complete
            request: The completion data
        """
        try:
            await complete_human_task(
                task_id=task_id,
                output_data=request.output_data,
                completed_by=request.completed_by,
            )

            # Fetch the updated task to return
            task = await get_human_task(task_id)
            if not task:  # Should not happen if complete_human_task succeeded
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

            logger.info("human task completed successfully", task_id=task_id)
            return task
        except ValueError as e:
            logger.exception("valueerror completing task", task_id=task_id)
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.exception("exception completing task", task_id=task_id)
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/{task_id}/cancel", response_model=HumanTask)
    async def cancel_task(task_id: UUID, request: CancelTaskRequest = Body(...)):
        """
        Cancel a pending human task.

        Args:
            task_id: The ID of the task to cancel
            request: The cancellation details
        """
        try:
            await cancel_human_task(
                task_id=task_id,
                reason=request.reason,
                cancelled_by=request.cancelled_by,
            )

            # Fetch the updated task to return
            task = await get_human_task(task_id)
            if not task:  # Should not happen if cancel_human_task succeeded
                logger.warning(
                    "human task not found after cancellation attempt", task_id=task_id
                )
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

            logger.info("human task cancelled successfully", task_id=task_id)
            return task
        except ValueError as e:
            logger.exception("valueerror cancelling task", task_id=task_id)
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.exception("exception cancelling task", task_id=task_id)
            raise HTTPException(status_code=500, detail=str(e))

    return router
