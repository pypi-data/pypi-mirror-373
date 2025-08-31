from datetime import datetime, timedelta
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import Select
from sqlmodel import case, col, func, select

from planar.modeling.orm.query_filter_builder import build_paginated_query
from planar.object_registry import ObjectRegistry
from planar.routers.event import create_workflow_event_routes
from planar.routers.models import (
    SortDirection,
    StepRunError,
    StepStats,
    WorkflowDefinition,
    WorkflowList,
    WorkflowRun,
    WorkflowRunList,
    WorkflowRunStatusCounts,
    WorkflowStartResponse,
    WorkflowStatusResponse,
    WorkflowStepInfo,
    WorkflowStepList,
)
from planar.security.authorization import (
    WorkflowAction,
    WorkflowResource,
    validate_authorization_for,
)
from planar.session import get_session
from planar.utils import utc_now
from planar.workflows import LockedResource, Workflow, WorkflowStep
from planar.workflows.models import (
    StepStatus,
    WorkflowStatus,
    workflow_lock_join_cond,
)
from planar.workflows.query import (
    build_effective_status_case,
    calculate_bulk_workflow_duration_stats,
    calculate_workflow_duration_stats,
    get_bulk_workflow_run_statuses,
    get_workflow_run_statuses,
)
from planar.workflows.step_metadata import get_steps_metadata


def build_base_workflow_query(
    workflow_name: str,
) -> Select[
    tuple[
        UUID,  # Workflow.id
        list[Any] | None,  # Workflow.args
        Dict[str, Any] | None,  # Workflow.kwargs
        Any | None,  # Workflow.result
        Dict[str, Any] | None,  # Workflow.error
        datetime,  # Workflow.created_at
        datetime,  # Workflow.updated_at
        str,  # effective_status_expr
        int,  # succeeded_step_count
        int,  # failed_steps_count
        int,  # running_steps_count
    ]
]:
    effective_status_expr = build_effective_status_case().label("effective_status")

    return (
        select(  # type: ignore[call-overload]
            Workflow.id,
            Workflow.args,
            Workflow.kwargs,
            Workflow.result,
            Workflow.error,
            Workflow.created_at,
            Workflow.updated_at,
            effective_status_expr,
            func.count(
                case((col(WorkflowStep.status) == StepStatus.SUCCEEDED, 1))
            ).label("succeeded_step_count"),
            func.count(case((col(WorkflowStep.status) == StepStatus.FAILED, 1))).label(
                "failed_steps_count"
            ),
            func.count(case((col(WorkflowStep.status) == StepStatus.RUNNING, 1))).label(
                "running_steps_count"
            ),
        )
        .select_from(Workflow)
        .outerjoin(LockedResource, workflow_lock_join_cond())
        .outerjoin(WorkflowStep, col(Workflow.id) == col(WorkflowStep.workflow_id))
        .where(Workflow.function_name == workflow_name)
        .group_by(
            col(Workflow.id),
            col(LockedResource.lock_until),
        )
    )


def create_workflow_router(
    registry: ObjectRegistry,
) -> APIRouter:
    router = APIRouter(tags=["Workflow Management"])

    create_workflow_event_routes(router)

    async def get_validated_body(workflow_name: str, body: dict = Body(...)):
        workflow = next(
            (wf for wf in registry.get_workflows() if wf.name == workflow_name), None
        )
        if not workflow:
            raise HTTPException(
                status_code=404, detail=f"Workflow '{workflow_name}' not found"
            )

        try:
            # Validate the request body against the model
            validated_body = workflow.pydantic_model(**body)

            return {"body": validated_body, "start_fn": workflow.obj.start}
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid request body for workflow '{workflow_name}': {str(e)}\nJSON Schema:\n{workflow.pydantic_model.model_json_schema()}",
            )

    @router.post("/{workflow_name}/start", response_model=WorkflowStartResponse)
    async def start_workflow(workflow_name: str, wf_data=Depends(get_validated_body)):
        validate_authorization_for(
            WorkflowResource(function_name=workflow_name), WorkflowAction.WORKFLOW_RUN
        )
        workflow = await wf_data["start_fn"](**wf_data["body"].model_dump(mode="json"))
        return WorkflowStartResponse(id=workflow.id)

    @router.get("/{run_id}/status", response_model=WorkflowStatusResponse)
    async def get_workflow_status(run_id: UUID):
        session = get_session()
        workflow = await session.get(Workflow, run_id)
        if not workflow:
            raise HTTPException(
                status_code=404, detail=f"Workflow run with id {run_id} not found"
            )
        validate_authorization_for(
            WorkflowResource(function_name=workflow.function_name),
            WorkflowAction.WORKFLOW_VIEW_DETAILS,
        )
        return WorkflowStatusResponse(workflow=workflow)

    @router.get("/", response_model=WorkflowList)
    async def list_workflows(
        seconds_ago: int | None = None,
        offset: int | None = 0,
        limit: int | None = 10,
    ):
        """
        Note that workflows are registered with the app using the `.register_workflow` method.

        Hence, we do not need to query the database to get the list of workflows.

        The workflow database tables track workflow RUNS.
        """
        # Check list permission on any workflow since we're listing all workflows
        validate_authorization_for(WorkflowResource(), WorkflowAction.WORKFLOW_LIST)

        session = get_session()

        # Prepare filters
        filters = []

        if seconds_ago:
            filters.append(
                (
                    Workflow.created_at,
                    ">=",
                    utc_now() - timedelta(seconds=seconds_ago),
                )
            )

        # Get stats for each workflow
        items = []
        all_workflows = registry.get_workflows()

        end_offset = limit
        if offset is not None:
            end_offset = offset + (limit or 0)

        workflows = all_workflows[offset or 0 : end_offset]

        # Bulk fetch all status counts and duration stats in 2 queries instead of 2*N queries
        workflow_names = [wf.name for wf in workflows]
        bulk_run_statuses = await get_bulk_workflow_run_statuses(
            workflow_names, session, filters
        )
        bulk_duration_stats = await calculate_bulk_workflow_duration_stats(
            workflow_names, session, filters
        )

        for workflow in workflows:
            # Get docstring description if available
            name = workflow.name.split(".")[-1]  # Get last part of function name
            description = workflow.description

            run_statuses = bulk_run_statuses.get(workflow.name, {})
            duration_stats = bulk_duration_stats.get(workflow.name)

            items.append(
                WorkflowDefinition(
                    fully_qualified_name=workflow.name,
                    name=name,
                    description=description,
                    input_schema=workflow.input_schema,
                    output_schema=workflow.output_schema,
                    total_runs=sum(run_statuses.values()),
                    run_statuses=WorkflowRunStatusCounts(
                        **{
                            status.value: count
                            for status, count in run_statuses.items()
                        }
                    ),
                    durations=duration_stats,
                )
            )

        return WorkflowList(items=items, total=len(items), offset=offset, limit=limit)

    @router.get("/{workflow_name}", response_model=WorkflowDefinition)
    async def get_workflow_stats(workflow_name: str):
        validate_authorization_for(
            WorkflowResource(function_name=workflow_name),
            WorkflowAction.WORKFLOW_VIEW_DETAILS,
        )
        session = get_session()

        wf = next(
            (wf for wf in registry.get_workflows() if wf.name == workflow_name), None
        )

        # Check if workflow exists in registry
        if not wf:
            raise HTTPException(
                status_code=404, detail=f"Workflow '{workflow_name}' not found"
            )

        description = wf.description
        name = wf.name.split(".")[-1]  # Get last part of function name

        run_statuses = await get_workflow_run_statuses(workflow_name, session)
        duration_stats = await calculate_workflow_duration_stats(session, workflow_name)

        return WorkflowDefinition(
            fully_qualified_name=workflow_name,
            name=name,
            description=description,
            input_schema=wf.input_schema,
            output_schema=wf.output_schema,
            total_runs=sum(run_statuses.values()),
            run_statuses=WorkflowRunStatusCounts(
                **{status.value: count for status, count in run_statuses.items()}
            ),
            durations=duration_stats,
        )

    @router.get("/{workflow_name}/runs", response_model=WorkflowRunList)
    async def list_workflow_runs(
        workflow_name: str,
        status: WorkflowStatus | None = None,
        offset: int | None = 0,
        limit: int | None = 10,
    ):
        validate_authorization_for(
            WorkflowResource(function_name=workflow_name),
            WorkflowAction.WORKFLOW_VIEW_DETAILS,
        )
        session = get_session()

        base_query = build_base_workflow_query(workflow_name)

        # Prepare filters - can filter on effective status using SQL
        filters = []
        if status:
            # Add a filter on the effective_status expression directly
            effective_status_expr = build_effective_status_case()
            filters.append((effective_status_expr, "==", status.value))

        # Apply filtering, pagination and ordering
        query, total_query = build_paginated_query(
            base_query,
            filters=filters,
            offset=offset,
            limit=limit,
            order_by=Workflow.created_at,
            order_direction=SortDirection.DESC,
        )

        # Calculate total count
        total = (await session.exec(total_query)).one()

        # Execute the query
        results = (await session.exec(query)).all()

        items = [
            WorkflowRun(
                id=row.id,
                status=row.effective_status,
                args=row.args,
                kwargs=row.kwargs,
                result=row.result,
                error=row.error,
                created_at=row.created_at,
                updated_at=row.updated_at,
                step_stats=StepStats(
                    completed=row.succeeded_step_count,
                    failed=row.failed_steps_count,
                    running=row.running_steps_count,
                ),
            )
            for row in results
        ]

        return WorkflowRunList(items=items, total=total, offset=offset, limit=limit)

    @router.get("/{workflow_name}/runs/{run_id}", response_model=WorkflowRun)
    async def get_workflow_run(workflow_name: str, run_id: UUID):
        validate_authorization_for(
            WorkflowResource(function_name=workflow_name),
            WorkflowAction.WORKFLOW_VIEW_DETAILS,
        )
        session = get_session()

        base_query = build_base_workflow_query(workflow_name)

        workflow_info = (
            await session.exec(
                base_query.where(col(Workflow.id) == run_id)  # type: ignore[arg-type]
            )
        ).first()

        if not workflow_info:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow run with id {run_id} not found for workflow {workflow_name}",
            )

        (
            workflow_id,
            args,
            kwargs,
            result,
            error,
            created_at,
            updated_at,
            effective_status,
            step_count,
            failed_steps_count,
            running_steps_count,
        ) = workflow_info

        return WorkflowRun(
            id=workflow_id,
            status=effective_status,
            args=args,
            kwargs=kwargs,
            result=result,
            error=error,
            created_at=created_at,
            updated_at=updated_at,
            step_stats=StepStats(
                completed=step_count,
                failed=failed_steps_count,
                running=running_steps_count,
            ),
        )

    @router.get("/{workflow_name}/runs/{run_id}/steps", response_model=WorkflowStepList)
    async def list_workflow_steps(
        workflow_name: str,
        run_id: UUID,
        status: StepStatus | None = None,
        step_type: str | None = None,
        offset: int | None = 0,
        limit: int | None = 10,
    ):
        validate_authorization_for(
            WorkflowResource(function_name=workflow_name),
            WorkflowAction.WORKFLOW_VIEW_DETAILS,
        )
        """
        List workflow steps with optional filtering.

        Returns rich metadata for each step based on its type in the 'meta' field.
        """
        session = get_session()

        # First verify the workflow exists
        workflow = (
            await session.exec(
                select(Workflow).where(
                    Workflow.function_name == workflow_name, Workflow.id == run_id
                )
            )
        ).first()

        if not workflow:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow run with id {run_id} not found for workflow {workflow_name}",
            )

        # Build base query for steps
        base_query = select(WorkflowStep).where(WorkflowStep.workflow_id == run_id)

        # Prepare filters
        filters = []

        # Add status filter if provided
        if status:
            filters.append((WorkflowStep.status, "==", status))

        # Add step type filter if provided
        if step_type:
            filters.append((WorkflowStep.step_type, "==", step_type))

        # Apply filtering, pagination and ordering
        query, total_query = build_paginated_query(
            base_query,
            filters=filters,
            offset=offset,
            limit=limit,
            order_by=WorkflowStep.step_id,
            order_direction=SortDirection.ASC,
        )

        # Calculate total count
        total = (await session.exec(total_query)).one()

        steps: list[WorkflowStep] = (await session.exec(query)).all()

        # Create step info objects with metadata
        items = []
        for step in steps:
            step_info = WorkflowStepInfo(
                step_id=step.step_id,
                parent_step_id=step.parent_step_id,
                workflow_id=step.workflow_id,
                function_name=step.function_name,
                display_name=WorkflowStepInfo.get_display_name(
                    step.display_name, step.function_name
                ),
                description=None,  # get_function_docs(step.function_name),
                status=step.status,
                step_type=step.step_type,
                args=step.args,
                kwargs=step.kwargs,
                result=step.result,
                error=StepRunError.model_validate(step.error) if step.error else None,
                retry_count=step.retry_count,
                created_at=step.created_at,
                updated_at=step.updated_at,
                meta=None,
            )

            items.append(step_info)

        return WorkflowStepList(items=items, total=total, offset=offset, limit=limit)

    @router.get(
        "/{workflow_name}/runs/{run_id}/steps/{step_id}",
        response_model=WorkflowStepInfo,
    )
    async def get_workflow_step(
        workflow_name: str,
        run_id: UUID,
        step_id: int,
    ):
        validate_authorization_for(
            WorkflowResource(function_name=workflow_name),
            WorkflowAction.WORKFLOW_VIEW_DETAILS,
        )
        """
        Get metadata for a specific workflow step.
        """
        session = get_session()

        # Build base query for steps
        async with session.begin_read():
            step = (
                await session.exec(
                    select(WorkflowStep).where(
                        WorkflowStep.workflow_id == run_id,
                        WorkflowStep.step_id == step_id,
                    )
                )
            ).first()

            if not step:
                raise HTTPException(
                    status_code=404,
                    detail=f"Workflow step with id {step_id} not found for workflow run {run_id}",
                )

        metadata = await get_steps_metadata([step], registry)

        # Create step info objects with metadata
        step_info = WorkflowStepInfo(
            step_id=step.step_id,
            parent_step_id=step.parent_step_id,
            workflow_id=step.workflow_id,
            function_name=step.function_name,
            display_name=WorkflowStepInfo.get_display_name(
                step.display_name, step.function_name
            ),
            description=None,  # get_function_docs(step.function_name),
            status=step.status,
            step_type=step.step_type,
            args=step.args,
            kwargs=step.kwargs,
            result=step.result,
            error=StepRunError.model_validate(step.error) if step.error else None,
            retry_count=step.retry_count,
            created_at=step.created_at,
            updated_at=step.updated_at,
            # Compute steps do not produce metadata, so use .get to avoid KeyError
            meta=metadata.get(step.step_id),
        )

        return step_info

    return router
