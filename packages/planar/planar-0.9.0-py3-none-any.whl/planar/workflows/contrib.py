from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Coroutine, Dict

from planar.logging import get_logger
from planar.session import get_session
from planar.utils import P, T, U, utc_now
from planar.workflows import step
from planar.workflows.context import get_context
from planar.workflows.events import check_event_exists, get_latest_event
from planar.workflows.step_core import Suspend, suspend_workflow
from planar.workflows.tracing import trace

logger = get_logger(__name__)


@step()
async def get_deadline(max_wait_time: float) -> datetime:
    return utc_now() + timedelta(seconds=max_wait_time)


@step(display_name="Wait for event")
async def wait_for_event(
    event_key: str,
    max_wait_time: float = -1,
) -> Dict[str, Any]:
    """
    Creates a durable step that waits for a specific event to be emitted.

    Args:
        event_key: The event identifier to wait for

    Returns:
        The event payload as a dictionary
    """
    logger.debug("waiting for event", event_key=event_key, max_wait_time=max_wait_time)
    await trace("enter", event_key=event_key)

    # Get workflow context
    ctx = get_context()
    workflow_id = ctx.workflow.id

    deadline = None
    if max_wait_time >= 0:
        deadline = await get_deadline(max_wait_time)
        logger.debug(
            "calculated deadline for event", event_key=event_key, deadline=deadline
        )
        await trace(
            "deadline",
            event_key=event_key,
            max_wait_time=max_wait_time,
            deadline=deadline,
        )

    async def transaction():
        # Check if the event already exists
        event_exists = await check_event_exists(event_key, workflow_id=workflow_id)
        logger.debug(
            "event exists check for workflow",
            event_key=event_key,
            exists=event_exists,
        )
        await trace("check-event-exists", event_key=event_key, exists=event_exists)

        if event_exists:
            # Event exists, get the event data and continue execution immediately
            event = await get_latest_event(event_key, workflow_id=workflow_id)
            logger.info(
                "event already exists, proceeding with payload",
                event_key=event_key,
                payload=event.payload if event else None,
            )
            await trace("existing-event", event_key=event_key)
            return event.payload if event and event.payload else {}

        # If deadline has passed, raise an exception
        now = utc_now()
        if deadline is not None and now > deadline:
            logger.warning(
                "timeout waiting for event",
                event_key=event_key,
                deadline=deadline,
                current_time=now,
            )
            await trace("deadline-timeout", event_key=event_key)
            raise ValueError(f"Timeout waiting for event ${event_key}")

        logger.info(
            "event not found, suspending workflow",
            event_key=event_key,
        )
        return suspend_workflow(
            interval=timedelta(seconds=max_wait_time) if max_wait_time > 0 else None,
            event_key=event_key,
        )

    session = get_session()
    result = await session.run_transaction(transaction)
    if isinstance(result, Suspend):
        # Suspend until event is emitted
        logger.debug(
            "workflow suspended, waiting for event",
            event_key=event_key,
        )
        await trace("suspend", event_key=event_key)
        await (
            result
        )  # This will re-raise the Suspend object's exception or re-enter the generator
        assert False, "Suspend should never return normally"  # Should not be reached
    logger.info(
        "event received or processed for workflow",
        event_key=event_key,
        result=result,
    )
    return result


def wait(
    poll_interval: float = 60.0,
    max_wait_time: float = 3600.0,
):
    """
    Creates a durable step that repeatedly checks a condition until it returns True.

    This decorator wraps a function that returns a boolean. The function will be
    called repeatedly until it returns True or until max_wait_time is reached.

    Args:
        poll_interval: How often to check the condition
        max_wait_time: Maximum time to wait before failing

    Returns:
        A decorator that converts a boolean-returning function into a step
        that waits for the condition to be true
    """

    def decorator(
        func: Callable[P, Coroutine[T, U, bool]],
    ) -> Callable[P, Coroutine[T, U, None]]:
        @step()
        @wraps(func)
        async def wait_step(*args: P.args, **kwargs: P.kwargs) -> None:
            logger.debug(
                "wait step called",
                func_name=func.__name__,
                poll_interval=poll_interval,
                max_wait_time=max_wait_time,
            )
            # Set up deadline for timeout
            deadline = None
            if max_wait_time >= 0:
                deadline = await get_deadline(max_wait_time)
                logger.debug(
                    "calculated deadline for wait step",
                    func_name=func.__name__,
                    deadline=deadline,
                )

            # Check the condition
            result = await func(*args, **kwargs)
            logger.debug(
                "condition check returned", func_name=func.__name__, result=result
            )

            # If condition is met, return immediately
            if result:
                logger.info("condition met, proceeding", func_name=func.__name__)
                return

            # If deadline has passed, raise an exception
            if deadline is not None and utc_now() > deadline:
                logger.warning(
                    "timeout waiting for condition to be met",
                    func_name=func.__name__,
                    deadline=deadline,
                )
                raise ValueError("Timeout waiting for condition to be met")

            # Otherwise, suspend the workflow to retry later
            logger.info(
                "condition not met, suspending",
                func_name=func.__name__,
                poll_interval_seconds=poll_interval,
            )
            await suspend_workflow(interval=timedelta(seconds=poll_interval))

        return wait_step

    return decorator
