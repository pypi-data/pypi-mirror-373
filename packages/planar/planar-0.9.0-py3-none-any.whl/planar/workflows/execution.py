import traceback
from datetime import timedelta
from typing import Any, Callable, Coroutine, Generic
from weakref import WeakValueDictionary

import planar.workflows.notifications as notifications
from planar.logging import get_logger
from planar.session import get_session
from planar.utils import R, T, U
from planar.workflows.context import ExecutionContext, delete_context, set_context
from planar.workflows.exceptions import try_restore_exception
from planar.workflows.lock import lock_workflow
from planar.workflows.models import Workflow, WorkflowStatus
from planar.workflows.serialization import (
    deserialize_args,
    deserialize_result,
    serialize_result,
)
from planar.workflows.step_core import Suspend
from planar.workflows.tracing import trace

_DEFAULT_LOCK_DURATION = timedelta(minutes=10)
_WORKFLOW_FUNCTION_REGISTRY: WeakValueDictionary[str, Callable[..., Any]] = (
    WeakValueDictionary()
)

logger = get_logger(__name__)


class YieldWrapper:
    def __init__(self, value):
        self.value = value

    def __await__(self):
        return (yield self.value)


def register_workflow_function(name: str, func: Callable[..., Any]):
    _WORKFLOW_FUNCTION_REGISTRY[name] = func


class StepperResult(Generic[R]):
    def __init__(self, *, value: R | None, suspend: Suspend | None):
        self.value = value
        self.suspend = suspend


async def stepper(coro: Coroutine[T, U, R]) -> StepperResult[R]:
    logger.debug("stepper started")
    coroutine_iterator = coro.__await__()
    try:
        yielded = next(coroutine_iterator)  # Start the coroutine
        while True:
            if isinstance(yielded, Suspend):
                logger.debug("stepper encountered suspend")
                return StepperResult(value=None, suspend=yielded)
            else:
                try:
                    result = await YieldWrapper(yielded)
                except BaseException as e:
                    # if an exception is raised by the event loop
                    # (most likely a cancellation), propagate it to the coroutine
                    logger.debug(
                        "stepper propagating exception to coroutine",
                        exception_type=type(e).__name__,
                    )
                    yielded = coroutine_iterator.throw(e)
                    continue
                # send the result back to the coroutine
                yielded = coroutine_iterator.send(result)
    except StopIteration as e:
        logger.debug("stepper finished with stopiteration")
        return StepperResult(value=e.value, suspend=None)


def workflow_result(workflow: Workflow):
    if workflow.status == WorkflowStatus.SUCCEEDED:
        original_fn = _WORKFLOW_FUNCTION_REGISTRY[workflow.function_name]
        return deserialize_result(original_fn, workflow.result)
    elif workflow.status == WorkflowStatus.FAILED:
        assert workflow.error
        raise try_restore_exception(workflow.error)
    assert False, "May only be called on finished workflows"


async def execute(workflow: Workflow):
    logger.debug(
        "executing workflow",
        workflow_id=workflow.id,
        function_name=workflow.function_name,
    )
    session = get_session()
    original_fn = _WORKFLOW_FUNCTION_REGISTRY[workflow.function_name]
    serialized_args = workflow.args or []
    serialized_kwargs = workflow.kwargs or {}
    args, kwargs = deserialize_args(original_fn, serialized_args, serialized_kwargs)

    # Cache the workflow id here to avoid "Was IO attempted in an unexpected
    # place?" SQLAlchemy errors when acessing expired attributes in an
    # AsyncSession.
    #
    # Even though we unconditionally set expire_on_commit=True on
    # PlanarSession, this is still necessary because SQLAlchemy will expire all
    # attributes of the workflow object on a session rollback. More details:
    # https://github.com/sqlalchemy/sqlalchemy/discussions/8282#discussioncomment-3213994
    workflow_id = workflow.id
    set_context(
        ExecutionContext(
            workflow=workflow,
            workflow_id=workflow_id,
        )
    )
    logger.debug("execution context set for workflow", workflow_id=workflow_id)

    try:
        stepper_result = await stepper(original_fn(*args, **kwargs))
        logger.debug(
            "stepper result for workflow",
            workflow_id=workflow_id,
            has_suspend=stepper_result.suspend is not None,
            has_value=stepper_result.value is not None,
        )
        if stepper_result.suspend:
            if stepper_result.suspend.exception:
                logger.error(
                    "workflow suspended due to an exception from stepper",
                    workflow_id=workflow_id,
                    exception=str(stepper_result.suspend.exception),
                )
                raise stepper_result.suspend.exception
            workflow.status = WorkflowStatus.PENDING
            logger.info(
                "workflow suspended",
                workflow_id=workflow_id,
                wakeup_at=workflow.wakeup_at,
                event_key=workflow.waiting_for_event,
            )
            return stepper_result.suspend
        workflow.status = WorkflowStatus.SUCCEEDED
        workflow.result = serialize_result(original_fn, stepper_result.value)
        logger.info(
            "workflow succeeded", workflow_id=workflow_id, result=workflow.result
        )
        return stepper_result.value
    except Exception as e:
        logger.exception("exception during workflow execution", workflow_id=workflow_id)
        workflow.status = WorkflowStatus.FAILED
        workflow.error = {
            "type": type(e).__name__,
            "message": str(e),
            "traceback": str(traceback.format_exc()),
        }
        raise e
    finally:
        delete_context()
        logger.debug("execution context deleted for workflow", workflow_id=workflow_id)
        await session.commit()
        # notify after committing to the db
        if workflow.status == WorkflowStatus.SUCCEEDED:
            notifications.workflow_succeeded(workflow)
        elif workflow.status == WorkflowStatus.FAILED:
            notifications.workflow_failed(workflow)
        else:
            notifications.workflow_suspended(workflow)


async def lock_and_execute(
    workflow: Workflow,
    lock_duration: timedelta = _DEFAULT_LOCK_DURATION,
):
    logger.debug("attempting to lock and execute workflow", workflow_id=workflow.id)
    session = get_session()

    async with lock_workflow(workflow, lock_duration):
        logger.debug("lock acquired for workflow", workflow_id=workflow.id)
        async with session.begin_read():
            await session.refresh(workflow)

        if workflow.status != WorkflowStatus.PENDING:
            logger.info(
                "workflow is not pending, returning existing result",
                workflow_id=workflow.id,
                status=workflow.status,
            )
            return workflow_result(workflow)

        notifications.workflow_resumed(workflow)
        logger.info("workflow resumed", workflow_id=workflow.id)

        # Execute until the next suspend or completion
        result = await execute(workflow)
        await trace("return", workflow_id=workflow.id)
        logger.debug(
            "execution finished for workflow",
            workflow_id=workflow.id,
            result_type=str(type(result)),
        )
        return result
