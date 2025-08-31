import inspect
import weakref
from datetime import timedelta
from functools import wraps
from typing import Callable, Coroutine, Type, cast
from uuid import UUID
from weakref import WeakKeyDictionary

import planar.workflows.notifications as notifications
from planar.logging import get_logger
from planar.session import get_session
from planar.utils import P, R, T, U
from planar.workflows.context import (
    get_context,
    in_context,
)
from planar.workflows.execution import register_workflow_function
from planar.workflows.models import StepType, Workflow, WorkflowStatus
from planar.workflows.orchestrator import WorkflowOrchestrator
from planar.workflows.serialization import serialize_args
from planar.workflows.step_core import _step, suspend_workflow
from planar.workflows.wrappers import StepWrapper, WorkflowWrapper

logger = get_logger(__name__)


def step(
    *,
    max_retries: int = 0,
    step_type: StepType = StepType.COMPUTE,
    return_type: Type | None = None,
    display_name: str | None = None,
):
    """
    Decorator to define a step in a workflow.

    This decorator is used to define a step function.
    It will register the function with the workflow engine and allow it to be executed.

    """
    step_decorator = _step(max_retries=max_retries, return_type=return_type)

    def decorator(
        func: Callable[P, Coroutine[T, U, R]],
        step_type: StepType = step_type,
        display_name: str | None = display_name,
    ) -> StepWrapper[P, T, U, R]:
        wrapper = step_decorator(func, step_type=step_type, display_name=display_name)

        @workflow(name=func.__name__ + ".auto_workflow")
        async def auto_workflow(*args: P.args, **kwargs: P.kwargs) -> R:
            """
            This is a special workflow that is used to run a step in a separate asyncio task
            """
            result = await wrapper(*args, **kwargs)
            return result

        @wraps(func)
        def run_step(*args: P.args, **kwargs: P.kwargs) -> Coroutine[T, U, R]:
            """
            If not in workflow context, then simply call the function directly.

            This allows users to use their workflow code within and outside of
            workflows.
            """
            if not in_context():
                return func(*args, **kwargs)
            return wrapper(*args, **kwargs)

        step_wrapper = StepWrapper(
            original_fn=func,
            wrapper=wrapper,
            wrapped_fn=run_step,
            auto_workflow=auto_workflow,
        )
        return step_wrapper

    return decorator


def workflow(*, name: str | None = None):
    """
    Decorator to define a workflow.

    This decorator is used to define a workflow function.
    It will register the function with the workflow engine and allow it to be executed.

    """

    def decorator(func: Callable[P, Coroutine[T, U, R]]) -> WorkflowWrapper[P, T, U, R]:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Workflow functions must be coroutines")

        function_name = name or func.__name__

        @wraps(func)
        async def start_workflow(*args: P.args, **kwargs: P.kwargs) -> Workflow:
            session = get_session()
            serialized_args, serialized_kwargs = serialize_args(func, args, kwargs)
            workflow = Workflow(
                function_name=function_name,
                args=serialized_args,
                kwargs=serialized_kwargs,
            )

            if in_context():
                ctx = get_context()
                if ctx.bind_parent_workflow:
                    logger.debug(
                        "binding parent workflow", parent_workflow_id=ctx.workflow_id
                    )
                    workflow.parent_id = ctx.workflow.id

            session.add(workflow)
            await session.commit()
            notifications.workflow_started(workflow)
            if WorkflowOrchestrator.is_set():
                orchestrator = WorkflowOrchestrator.get()
                orchestrator.poll_soon()
            return workflow

        @_step()
        async def start_workflow_step(*args: P.args, **kwargs: P.kwargs) -> UUID:
            workflow = await start_workflow(*args, **kwargs)
            return workflow.id

        async def wait_for_completion(workflow_id: UUID):
            orchestrator = WorkflowOrchestrator.get()
            return cast(R, await orchestrator.wait_for_completion(workflow_id))

        async def run_workflow_in_new_context(*args: P.args, **kwargs: P.kwargs) -> R:
            async with WorkflowOrchestrator.ensure_started():
                # Running outside of a workflow execution context.
                # Start workflow normally and wait for completion.
                workflow = await start_workflow(*args, **kwargs)
                workflow_id = workflow.id
                return await wait_for_completion(workflow_id)

        async def run_child_workflow(*args: P.args, **kwargs: P.kwargs) -> R:
            ctx = get_context()
            # Since the parent will wait, we have to
            # create the association when creating
            # the child
            ctx.bind_parent_workflow = True
            workflow_id = await start_workflow_step(*args, **kwargs)
            # Considering the current workflow will
            # suspend (this lose the context) it is
            # not necessary to reset the flag here.
            # Leaving it only for documenting intent
            # that this is a temporary setting.
            ctx.bind_parent_workflow = False
            session = get_session()
            async with session.begin_read():
                workflow = await session.get(Workflow, workflow_id)
            assert workflow

            if workflow.status == WorkflowStatus.PENDING:
                # Suspend for 0 seconds. Since the poll query only selects
                # workflows that have no children, suspending for 0 seconds
                # mean this workflow will wakeup as soon as all children finish
                await suspend_workflow(interval=timedelta(seconds=0))

            return await wait_for_completion(workflow_id)

        @wraps(func)
        def run_workflow(*args: P.args, **kwargs: P.kwargs) -> Coroutine[T, U, R]:
            if not in_context():
                return run_workflow_in_new_context(*args, **kwargs)
            return run_child_workflow(*args, **kwargs)

        register_workflow_function(function_name, func)

        wf_wrapper = WorkflowWrapper(
            function_name=function_name,
            original_fn=func,
            start=start_workflow,
            start_step=start_workflow_step,
            wait_for_completion=wait_for_completion,
            wrapped_fn=run_workflow,
        )

        return wf_wrapper

    return decorator


__AS_STEP_CACHE = WeakKeyDictionary()


def __is_workflow_step(callable: Callable[P, Coroutine[T, U, R]]) -> bool:
    return isinstance(callable, StepWrapper)


def as_step(
    func: Callable[P, Coroutine[T, U, R]],
    step_type: StepType,
    display_name: str | None = None,
    return_type: Type[R] | None = None,
) -> Callable[P, Coroutine[T, U, R]]:
    """
    This utility fn is for treating async functions as steps without modifying
    the original function.

    Only use this where it doesn't make sense to use the @step decorator (such as third
    party functions)
    """
    if __is_workflow_step(func):
        return func
    # cache the result to avoid reapplying the step decorator for this callable in the future
    weak_step_callable = __AS_STEP_CACHE.get(func, None)
    step_callable = weak_step_callable() if weak_step_callable is not None else None
    if step_callable is None:
        step_callable = step(return_type=return_type)(
            func, step_type=step_type, display_name=display_name
        )
        __AS_STEP_CACHE[func] = weakref.ref(step_callable)
    return step_callable
