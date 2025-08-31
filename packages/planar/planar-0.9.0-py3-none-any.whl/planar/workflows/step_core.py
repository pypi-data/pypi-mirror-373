import inspect
import json
import traceback
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Coroutine, Type, cast

from sqlmodel import col, select

from planar.logging import get_logger
from planar.session import get_session
from planar.utils import P, R, T, U, utc_now
from planar.workflows.context import get_context
from planar.workflows.exceptions import (
    NonDeterministicStepCallError,
    try_restore_exception,
)
from planar.workflows.misc import func_full_name
from planar.workflows.models import StepStatus, StepType, WorkflowStep
from planar.workflows.notifications import step_failed, step_running, step_succeeded
from planar.workflows.serialization import (
    deserialize_result,
    serialize_args,
    serialize_result,
)

logger = get_logger(__name__)


def deep_equals(obj1, obj2):
    """Recursively compares two JSON-like objects for equality"""

    if isinstance(obj1, Mapping) and isinstance(obj2, Mapping):
        if len(obj1) != len(obj2):
            return False
        for k1, v1 in obj1.items():
            if k1 not in obj2:
                return False
            if not deep_equals(v1, obj2[k1]):
                return False
    elif (
        isinstance(obj1, Sequence)
        and isinstance(obj2, Sequence)
        and not isinstance(obj1, (str, bytes))
    ):
        if len(obj1) != len(obj2):
            return False
        for item1, item2 in zip(obj1, obj2):
            if not deep_equals(item1, item2):
                return False

    elif obj1 != obj2:
        return False

    return True


@dataclass(kw_only=True, frozen=True)
class Suspend:
    wakeup_at: datetime | None
    event_key: str | None
    exception: Exception | None

    def __await__(self):
        result = yield self
        return result


def suspend_workflow(
    wakeup_at: datetime | None = None,
    interval: timedelta | None = None,
    event_key: str | None = None,
    exception: Exception | None = None,
) -> Suspend:
    logger.debug(
        "suspending workflow",
        wakeup_at=wakeup_at,
        interval_seconds=interval.total_seconds() if interval else None,
        event_key=event_key,
        exception=str(exception) if exception else None,
    )
    if exception is not None:
        return Suspend(wakeup_at=None, event_key=None, exception=exception)

    ctx = get_context()
    workflow = ctx.workflow

    if interval and wakeup_at:
        raise ValueError("Only one of interval or wakeup_at must be provided")

    # Set the workflow waiting_for_event, when provided
    workflow.waiting_for_event = event_key

    if wakeup_at is None and interval is None:
        if event_key is None:
            raise ValueError("Either wakeup_at or interval must be provided")
        else:
            workflow.wakeup_at = None
            logger.debug(
                "workflow suspended waiting for event",
                workflow_id=ctx.workflow_id,
                event_key=event_key,
            )
            return Suspend(wakeup_at=None, event_key=event_key, exception=None)

    if interval is not None:
        wakeup_at = utc_now() + interval
    workflow.wakeup_at = wakeup_at
    logger.debug(
        "workflow suspended until",
        workflow_id=ctx.workflow_id,
        wakeup_at=wakeup_at,
        event_key=event_key,
    )
    return Suspend(wakeup_at=wakeup_at, event_key=event_key, exception=None)


def _step(
    *,
    max_retries: int = 0,
    return_type: Type | None = None,
):
    def decorator(
        func: Callable[P, Coroutine[T, U, R]],
        step_type: StepType = StepType.COMPUTE,
        display_name: str | None = None,
    ) -> Callable[P, Coroutine[T, U, R]]:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Step functions must be coroutines")

        name = func_full_name(func)

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            session = get_session()
            ctx = get_context()
            ctx.current_step_id += 1
            logger.debug(
                "executing step", step_name=name, args=str(args), kwargs=kwargs
            )
            step_id = ctx.current_step_id
            validate_repeated_call_args = False

            step = (
                await session.exec(
                    select(WorkflowStep)
                    .where(col(WorkflowStep.workflow_id) == ctx.workflow_id)
                    .where(col(WorkflowStep.step_id) == step_id)
                )
            ).first()

            if not step:
                logger.debug(
                    "first time executing step",
                    step_name=name,
                    step_id=step_id,
                    workflow_id=ctx.workflow_id,
                )
                # first time executing this step
                # Get parent from the step stack if available
                parent_step_id = None
                if ctx.step_stack:
                    parent_step_id = ctx.step_stack[-1].step_id

                step = WorkflowStep(
                    step_id=step_id,
                    workflow_id=ctx.workflow_id,
                    function_name=name,
                    step_type=step_type,
                    args=[],
                    kwargs={},
                    status=StepStatus.RUNNING,
                    parent_step_id=parent_step_id,
                    display_name=display_name,
                )
                session.add(step)

            elif step.status == StepStatus.SUCCEEDED:
                logger.info(
                    "step already completed, returning cached result",
                    step_name=name,
                    step_id=step_id,
                )
                # already completed, return cached result
                # have to update the current_step_id in the context
                ctx.current_step_id += step.sub_step_count
                deserialized_result = deserialize_result(
                    func, step.result, return_type, args, kwargs
                )
                return cast(R, deserialized_result)
            elif step.status == StepStatus.FAILED:
                logger.debug(
                    "step previously failed, checking for retry or non-determinism",
                    step_name=name,
                    step_id=step_id,
                )
                # Check that the function name is the same as the previous call. Note
                # that we need to check this before checking max_retries, because if
                # the step is different and has a different max_retries setting, we could
                # try to restore/raise the exception of the initial step
                if step.function_name != name:
                    step.status = StepStatus.FAILED
                    err_msg = (
                        f"Non-deterministic step call detected at step ID {step_id}. "
                        f"Previous function name: {step.function_name}, current: {name}"
                    )
                    logger.warning(
                        "non-deterministic step call detected",
                        step_id=step_id,
                        previous_function_name=step.function_name,
                        current_function_name=name,
                    )
                    await suspend_workflow(
                        exception=NonDeterministicStepCallError(err_msg)
                    )
                    assert False, "Non-deterministic step call detected"

                validate_repeated_call_args = True

                if max_retries < 0 or step.retry_count < max_retries:
                    logger.info(
                        "retrying step",
                        step_name=name,
                        step_id=step_id,
                        retry_count=step.retry_count + 1,
                        max_retries=max_retries if max_retries >= 0 else "unlimited",
                    )
                    # failed previously but will be retried
                    step.retry_count += 1
                    step.status = StepStatus.RUNNING
                else:
                    assert step.error
                    logger.warning(
                        "max retries reached for step, raising original error",
                        step_name=name,
                        step_id=step_id,
                    )
                    # max retries reached
                    raise try_restore_exception(step.error)

            # Add step input parameters to the step record
            serialized_args, serialized_kwargs = serialize_args(func, args, kwargs)

            if validate_repeated_call_args:
                logger.debug(
                    "validating repeated call arguments for step",
                    step_name=name,
                    step_id=step_id,
                )
                # Check that the arguments are the same - deep compare args tuple
                if not deep_equals(step.args, serialized_args):
                    step.status = StepStatus.FAILED
                    err_msg = (
                        f"Non-deterministic step call detected at step ID {step_id}. "
                        f"Previous args: {json.dumps(step.args)}, current: {json.dumps(serialized_args)}"
                    )
                    logger.warning(
                        "non-deterministic step call detected on args",
                        step_id=step_id,
                        previous_args=json.dumps(step.args),
                        current_args=json.dumps(serialized_args),
                    )
                    await suspend_workflow(
                        exception=NonDeterministicStepCallError(err_msg)
                    )
                    assert False, "Non-deterministic step call detected"

                # Check keyword arguments determinism - deep compare kwargs dict
                if not deep_equals(step.kwargs, serialized_kwargs):
                    step.status = StepStatus.FAILED
                    err_msg = (
                        f"Non-deterministic step call detected at step ID {step_id}. "
                        f"Previous kwargs: {json.dumps(step.kwargs)}, current: {json.dumps(serialized_kwargs)}"
                    )
                    logger.warning(
                        "non-deterministic step call detected on kwargs",
                        step_id=step_id,
                        previous_kwargs=json.dumps(step.kwargs),
                        current_kwargs=json.dumps(serialized_kwargs),
                    )
                    await suspend_workflow(
                        exception=NonDeterministicStepCallError(err_msg)
                    )
                    assert False, "Non-deterministic step call detected"

            step.args = serialized_args
            step.kwargs = serialized_kwargs

            await session.commit()
            step_running(step)

            ctx.step_stack.append(step)
            logger.debug(
                "step pushed to stack",
                step_name=name,
                step_id=step_id,
                stack_size=len(ctx.step_stack),
            )

            try:
                result = await func(*args, **kwargs)
                step.status = StepStatus.SUCCEEDED
                step.result = serialize_result(func, result)
                step.error = None
                step.sub_step_count = ctx.current_step_id - step_id
                await session.commit()
                step_succeeded(step)
                logger.info(
                    "step succeeded",
                    step_name=name,
                    step_id=step_id,
                    result=step.result,
                )
                # Deserialize the result to ensure consistency
                # between initial run and re-runs (due to suspension).
                deserialized_result = deserialize_result(
                    func, step.result, return_type, args, kwargs
                )
                return cast(R, deserialized_result)
            except BaseException as e:
                if isinstance(e, GeneratorExit):
                    raise
                logger.exception("exception in step", step_name=name, step_id=step_id)
                # rollback user changes
                await session.rollback()
                step.status = StepStatus.FAILED
                step.error = {
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": str(traceback.format_exc()),
                }
                # rollback would have removed the added step (if it was new),
                # so we use `merge` as an "insert or update"
                await session.merge(step)
                await session.commit()
                step_failed(step)

                if max_retries < 0 or step.retry_count < max_retries:
                    logger.info(
                        "step failed, will suspend for retry",
                        step_name=name,
                        step_id=step_id,
                        error=str(e),
                    )
                    # This step is going to be retried, so we will suspend the workflow
                    # TODO add configurable backoff delay
                    await suspend_workflow(interval=timedelta(seconds=5))

                raise e
            finally:
                ctx.step_stack.pop()
                logger.debug(
                    "step popped from stack",
                    step_name=name,
                    step_id=step_id,
                    stack_size=len(ctx.step_stack),
                )

        return wrapper

    return decorator


@_step()
async def suspend(
    *, interval: timedelta | None = None, wakeup_at: datetime | None = None
):
    ctx = get_context()
    step = ctx.step_stack[-1]
    session = get_session()
    step.status = StepStatus.SUCCEEDED
    await session.merge(step)
    await suspend_workflow(wakeup_at=wakeup_at, interval=interval)
