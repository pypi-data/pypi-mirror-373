import asyncio
import traceback
from contextlib import asynccontextmanager
from datetime import timedelta

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm.exc import StaleDataError, UnmappedInstanceError

from planar.db import new_session
from planar.logging import get_logger
from planar.session import engine_var, get_session
from planar.utils import utc_now
from planar.workflows.exceptions import LockResourceFailed
from planar.workflows.models import LockedResource, Workflow, workflow_exec_lock_key
from planar.workflows.tracing import trace

_DEFAULT_RETRY_INTERVAL_SECONDS = 5
_DEFAULT_RETRY_COUNT = 30  # with default retry interval, wait 2.5 minutes

logger = get_logger(__name__)


async def lock_heartbeat(
    lock: LockedResource,
    lock_duration: timedelta,
    lock_owner: asyncio.Task,
):
    lock_key = lock.lock_key
    engine = engine_var.get()
    heartbeat_interval = lock_duration / 3
    await trace(
        "enter",
        lock_key=lock_key,
        lock_duration=lock_duration.total_seconds(),
        lock_heartbeat_interval=heartbeat_interval.total_seconds(),
    )
    logger.debug(
        "lock heartbeat started",
        lock_key=lock_key,
        duration_seconds=lock_duration.total_seconds(),
        interval_seconds=heartbeat_interval.total_seconds(),
    )
    async with new_session(engine) as session:
        try:
            async with session.begin():
                session.add(lock)
            while True:
                try:
                    sleep_seconds = heartbeat_interval.total_seconds()
                    await trace("sleep", lock_key=lock_key, sleep_seconds=sleep_seconds)
                    await asyncio.sleep(sleep_seconds)
                    # Renew the lock
                    async with session.begin():
                        lock.lock_until = utc_now() + lock_duration
                        await trace(
                            "renew-lock",
                            lock_key=lock_key,
                            lock_until=lock.lock_until,
                        )
                        logger.debug(
                            "lock renewed",
                            lock_key=lock_key,
                            lock_until=lock.lock_until,
                        )
                    await trace("commit", lock_key=lock_key)
                except StaleDataError:
                    logger.exception(
                        "stale data error in lock heartbeat, cancelling owner task",
                        lock_key=lock_key,
                    )
                    await trace("stale-data-error", lock_key=lock_key)
                    # This would happen if the process paused for too long and some
                    # other worker acquired the lock. Some possible causes:
                    #
                    # - "stop the world" GC that took too long
                    # - Some network call took too long. For example, imagine that
                    #   `await session.commit()` took minutes to return after the
                    #   changes were actually committed
                    #
                    # No matter what the cause was (and however unlikely it is to
                    # happen in practice), it is no longer safe to continue
                    # processing this resource. Kill the main task.
                    lock_owner.cancel()
                    break
                except asyncio.CancelledError:
                    logger.debug("lock heartbeat cancelled by owner", lock_key=lock_key)
                    # Cancelled by the lock owner
                    break
                except Exception:
                    logger.exception(
                        "exception in lock heartbeat, cancelling owner task",
                        lock_key=lock_key,
                    )

                    await trace(
                        "exception",
                        lock_key=lock_key,
                        traceback=traceback.format_exc(),
                    )
                    # similarly to the `StaleDataError, kill the main task
                    lock_owner.cancel()
                    break
        finally:
            # ensure the lock object is detached from the session
            try:
                session.expunge(lock)
            except UnmappedInstanceError:
                # it is possible that the lock was not added to the session yet
                pass
    await trace("exit", lock_key=lock_key)
    logger.debug("lock heartbeat stopped", lock_key=lock_key)


@asynccontextmanager
async def lock_resource(
    lock_key: str,
    lock_duration: timedelta,
    retry_count: int = _DEFAULT_RETRY_COUNT,
    retry_interval_seconds: int = _DEFAULT_RETRY_INTERVAL_SECONDS,
):
    assert retry_count >= 0
    await trace("enter", lock_key=lock_key)
    logger.debug(
        "attempting to lock resource",
        lock_key=lock_key,
        duration_seconds=lock_duration.total_seconds(),
        retries=retry_count,
    )
    session = get_session()

    lock = None
    for remaining in range(retry_count, -1, -1):
        try:
            async with session.begin():
                lock = LockedResource(
                    lock_key=lock_key,
                    lock_until=utc_now() + lock_duration,
                )
                session.add(lock)
                await trace("add-locked-resource", lock_key=lock_key)
            await trace("commit")
            logger.info(
                "resource locked", lock_key=lock_key, lock_until=lock.lock_until
            )
            # This LockedResource instance will be passed to the heartbeat task
            # which will use a different session to manage it.
            session.expunge(lock)
            break
        except (OperationalError, IntegrityError) as e:
            logger.exception(
                "failed to acquire lock for resource on attempt",
                lock_key=lock_key,
                attempt=retry_count - remaining + 1,
            )
            await trace("add-locked-resource-error", lock_key=lock_key, error=str(e))
        finally:
            # ensure the session is ready for re-use after an exception
            await session.rollback()
        lock = None
        await trace("retry", lock_key=lock_key, remaining_retry_count=remaining)
        if remaining > 0:
            logger.debug(
                "retrying lock for resource",
                lock_key=lock_key,
                retry_interval_seconds=retry_interval_seconds,
                retries_left=remaining,
            )
            await asyncio.sleep(retry_interval_seconds)

    if lock is None:
        logger.warning(
            "failed to lock resource after all attempts",
            lock_key=lock_key,
            attempts=retry_count + 1,
        )
        await trace("no-remaining-retries", lock_key=lock_key)
        raise LockResourceFailed(f'Failed to lock resource "{lock_key}"')

    # Start the heartbeat to renew the lock periodically
    await trace("start-heartbeat", lock_key=lock_key)
    current_task = asyncio.current_task()
    assert current_task
    heartbeat_task = asyncio.create_task(
        lock_heartbeat(lock, lock_duration, current_task)
    )

    try:
        await trace("yield", lock_key=lock_key)
        yield
    finally:
        # Stop the heartbeat
        await trace("cancel-heartbeat", lock_key=lock_key)
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
        if session.in_transaction():
            # Session should not be in a transaction here. This is probably the
            # result of an exception which was not handled by calling rollback.
            # We'll do it here because we need to release the lock, which has
            # to be done in another transaction, but leave a warning in the
            # logs
            logger.warning(
                "session is still in transaction, rolling back", lock_key=lock_key
            )
            await session.rollback()
        async with session.begin():
            session.add(lock)
            await session.delete(lock)
            await trace("release-lock", lock_key=lock_key)
        await trace("exit", lock_key=lock_key)


@asynccontextmanager
async def lock_workflow(
    workflow: Workflow,
    lock_duration: timedelta,
    retry_count: int = _DEFAULT_RETRY_COUNT,
    retry_interval_seconds: int = _DEFAULT_RETRY_INTERVAL_SECONDS,
):
    lock_key = workflow_exec_lock_key(workflow.id)
    async with lock_resource(
        lock_key,
        lock_duration,
        retry_count=retry_count,
        retry_interval_seconds=retry_interval_seconds,
    ):
        yield
