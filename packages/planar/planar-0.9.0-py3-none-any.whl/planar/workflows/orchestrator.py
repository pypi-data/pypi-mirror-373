from asyncio import (
    FIRST_COMPLETED,
    AbstractEventLoop,
    CancelledError,
    Task,
    create_task,
    get_running_loop,
    sleep,
    wait,
)
from contextlib import asynccontextmanager
from contextvars import ContextVar
from datetime import timedelta
from heapq import heappop, heappush
from time import monotonic
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import aliased
from sqlmodel import col, delete, exists, select

from planar.db import new_session
from planar.logging import get_logger
from planar.session import engine_var, get_engine, get_session, session_context
from planar.utils import utc_now
from planar.workflows.execution import (
    _DEFAULT_LOCK_DURATION,
    lock_and_execute,
    workflow_result,
)
from planar.workflows.models import (
    LockedResource,
    Workflow,
    WorkflowStatus,
    workflow_lock_join_cond,
)
from planar.workflows.notifications import (
    WorkflowNotificationCallback,
    workflow_notification_context,
)
from planar.workflows.step_core import Suspend
from planar.workflows.tracing import trace

logger = get_logger(__name__)


def workflow_can_be_executed():
    ChildWorkflow = aliased(Workflow)
    return (
        # condition 1: workflow must be pending.
        (col(Workflow.status) == WorkflowStatus.PENDING)
        &
        # condition 2:
        #   (wakeup_at must be NULL (not suspended) AND must not be waiting for event) OR
        #    wakeup_at is in the past
        (
            (
                col(Workflow.wakeup_at).is_(None)
                & col(Workflow.waiting_for_event).is_(None)
            )
            | (col(Workflow.wakeup_at) < utc_now())
        )
        &
        # condition 3: lock_until must be NULL (not locked) or in the past (lock expired)
        (
            (col(LockedResource.lock_until).is_(None))
            | (col(LockedResource.lock_until) < utc_now())
        )
        &
        # condition 4: workflow cannot have any pending children
        ~(
            exists().where(
                (
                    (col(ChildWorkflow.status) == WorkflowStatus.PENDING)
                    & (col(ChildWorkflow.parent_id) == col(Workflow.id))
                )
            )
        )
    )


class WorkflowOrchestrator:
    context_var = ContextVar["WorkflowOrchestrator"]("orchestrator")

    def __init__(self, engine: AsyncEngine):
        self.__engine = engine
        self.__event_loop: AbstractEventLoop | None = None
        self.__running = False
        self.__next_poll_time: float = 0
        # This will be managed with heapq push/pop, making it behave like a
        # priority queue. In other words, the list will always have the
        # smallest poll time at index 0
        self.__extra_polls: list[float] = []
        # keep track of workflow currently being processed.
        self.__active_workflows: dict[UUID, Task] = {}

    @staticmethod
    def get():
        return WorkflowOrchestrator.context_var.get()

    @staticmethod
    def is_set():
        return WorkflowOrchestrator.context_var.get(None) is not None

    @staticmethod
    def set(orchestrator: "WorkflowOrchestrator"):
        return WorkflowOrchestrator.context_var.set(orchestrator)

    @staticmethod
    def reset(token):
        return WorkflowOrchestrator.context_var.reset(token)

    @asynccontextmanager
    @staticmethod
    async def ensure_started(**run_kwargs):
        is_set = WorkflowOrchestrator.context_var.get(None) is not None
        orchestrator = None
        tok = None
        task = None
        if not is_set:
            orchestrator = WorkflowOrchestrator(get_engine())
            task = create_task(orchestrator.run(**run_kwargs))
            tok = WorkflowOrchestrator.set(orchestrator)
        try:
            yield WorkflowOrchestrator.get()
        finally:
            if task:
                WorkflowOrchestrator.reset(tok)
                task.cancel()
                try:
                    await task
                except CancelledError:
                    pass

    async def __enqueue_suspended_workflows(
        self,
        query_limit: int,
        lock_duration: timedelta,
    ):
        # exclude workflows that are currently being processed
        # or that have been enqueued for processing
        active_workflow_ids = set(self.__active_workflows.keys())

        condition = workflow_can_be_executed()
        if active_workflow_ids:
            condition &= col(Workflow.id).not_in(active_workflow_ids)
        async with new_session(self.__engine) as session:
            # delete expired locks
            async with session.begin():
                deleted = (
                    await session.exec(
                        delete(LockedResource)  # type: ignore
                        .where(col(LockedResource.lock_until) < utc_now())
                        .returning(col(LockedResource.lock_key)),
                    )
                ).all()
            await trace(
                "delete-expired-lock",
                deleted_count=len(deleted),
            )

            workflow_ids = (
                await session.exec(
                    select(Workflow.id)
                    .select_from(Workflow)
                    .outerjoin(LockedResource, workflow_lock_join_cond())
                    .where(condition)
                    .limit(query_limit)
                )
            ).all()

        if len(workflow_ids) == query_limit:
            logger.info(
                "query limit reached, more workflows might be available",
                query_limit=query_limit,
            )
        for workflow_id in workflow_ids:
            task = create_task(
                self.__resume_workflow(
                    workflow_id,
                    lock_duration=lock_duration,
                )
            )
            # add the current task to the active dictionary
            self.__active_workflows[workflow_id] = task
        return len(workflow_ids)

    async def __resume_workflow(
        self,
        workflow_id: UUID,
        lock_duration: timedelta = _DEFAULT_LOCK_DURATION,
    ):
        async with session_context(self.__engine) as session:
            try:
                logger.debug("resuming workflow", workflow_id=workflow_id)
                async with session.begin():
                    # Wrap this in a transaction to ensure we hold no locks
                    # when entering "execute", which will first try to acquire
                    # the lock before starting actual execution.
                    workflow = await session.get(Workflow, workflow_id)
                if not workflow:
                    raise ValueError(f"Workflow {workflow_id} not found")

                parent_id = workflow.parent_id

                result = await lock_and_execute(
                    workflow,
                    lock_duration=lock_duration,
                )

                if isinstance(result, Suspend):
                    if result.wakeup_at is not None:
                        # calculate in how many seconds it is supposed to wakeup
                        interval_seconds = (
                            result.wakeup_at - utc_now()
                        ).total_seconds()
                        logger.info(
                            "workflow suspended",
                            workflow_id=workflow_id,
                            interval_seconds=interval_seconds,
                        )
                        # get current monotonic time
                        monotonic_now = monotonic()
                        # compute next poll time required to wakeup the workflow
                        next_poll_time = monotonic_now + interval_seconds
                        self.poll_soon(next_poll_time)
                        logger.info(
                            "scheduling poll",
                            workflow_id=workflow_id,
                            next_poll_time=next_poll_time,
                        )
                elif parent_id is not None:
                    # Workflow has a parent, adjust poll time.
                    # We could also call self.enqueue_workflow here, but that
                    # would be assuming that the parent workflow is ready to be
                    # executed, and I'd rather leave the decision to the query
                    # logic.
                    logger.info(
                        "adjusting poll time to run parent",
                        workflow_id=workflow_id,
                        parent_id=parent_id,
                    )
                    self.poll_soon()

            except BaseException as e:
                if isinstance(e, GeneratorExit):
                    # GeneratorExit should never be handled
                    raise
                logger.exception(
                    "exception during workflow resumption", workflow_id=workflow_id
                )
            finally:
                # remove the task from the active dictionary
                logger.debug("removing from active workflows", workflow_id=workflow_id)
                self.__active_workflows.pop(workflow_id, None)

    async def wait_for_completion(self, workflow_id: UUID):
        self.poll_soon()
        session = get_session()
        async with session.begin_read():
            workflow = await session.get(Workflow, workflow_id)
        assert workflow
        while True:
            async with session.begin_read():
                await session.refresh(workflow)
            if workflow.status != WorkflowStatus.PENDING:
                return workflow_result(workflow)
            # Currently this method is only used in tests and when calling subworkflows.
            # When calling subworkflows, the parent always suspends when the child has not
            # completed, so in practice this poll won't be used a lot.
            await sleep(1)

    def poll_soon(self, time: float | None = None):
        if time is None:
            time = monotonic()
        heappush(self.__extra_polls, time)

    async def __run(
        self,
        *,
        poll_interval: float,
        max_concurrent_workflows: int,
        lock_duration: timedelta,
    ):
        event_loop = get_running_loop()
        if self.__event_loop is not None and self.__event_loop != event_loop:
            raise RuntimeError("Orchestrator already started on a different event loop")
        if self.__running:
            raise RuntimeError("Orchestrator already running")
        self.__event_loop = event_loop
        self.__running = True
        orchestrator_tok = WorkflowOrchestrator.set(self)
        engine_tok = engine_var.set(self.__engine)

        # This loop will sleep for 1 second between each iteration, sending a
        # poll query to the database when current time >= self.__next_poll_time or when
        # another poll was scheduled in `self.__extra_polls`
        # self.__next_poll_time advanced by poll_interval seconds
        while True:
            sleep_seconds = 1
            # get monotonic time
            monotonic_now = monotonic()
            next_poll = self.__next_poll_time
            # check if we have any extra polls to do
            while self.__extra_polls and self.__extra_polls[0] <= monotonic_now:
                next_poll = heappop(self.__extra_polls)

            if monotonic_now >= next_poll:
                free_slots = max_concurrent_workflows - len(self.__active_workflows)
                if free_slots == 0:
                    # No free slots, wait until at least one task completes
                    #
                    # Note that we collect the active tasks in a normal set to
                    # Ensure that `asyncio.wait` coroutine object will receive
                    # the same tasks that are in the WeakSet at the time of the call.
                    # To understand this better, consider the follwing scenario:

                    #   - The max_concurrent_workflows is set to 1
                    #   - We have 1 task in the set, meaning this branch will be taken
                    #   - We pass the 1 task WeakSet to `asyncio.wait` coroutine factory,
                    #     which creates the coroutine object referencing the WeakSet
                    #   - We yield back to the event loop (`await`)
                    #   - Before the `asyncio.wait` coroutine has a chance to start,
                    #     the task finishes and is garbage collected, causing the WeakSet
                    #     to be empty
                    #   - asyncio.wait coroutine object starts with an empty set, causing
                    #     an exception to be raised.
                    #
                    # Even though the above situation is extremely unlikely,
                    # especially in the default case of 100 max_concurrent_workflows,
                    # (and might be impossible, depending on how the order asyncio
                    # runs things), it is still a theoreticall possibility from the POV
                    # of the caller, so we have to do the correct thing.
                    #
                    # Another possibility would be to surround this on a try/except, but
                    # this would be less elegant.
                    logger.debug("no free slots, waiting for active tasks to complete")
                    await wait(
                        set(self.__active_workflows.values()),
                        return_when=FIRST_COMPLETED,
                    )
                    continue
                logger.debug("polling workflows", poll_time=monotonic_now)
                await self.__enqueue_suspended_workflows(free_slots, lock_duration)

                if monotonic_now >= self.__next_poll_time:
                    self.__next_poll_time = monotonic_now + poll_interval
                    logger.debug("next poll time", next_poll_time=self.__next_poll_time)
                    # Not really used in practice, but tests can set poll
                    # interval to < 1 second, so we handle that here
                    sleep_seconds = min(1, poll_interval)
            await sleep(sleep_seconds)

        self.__running = False
        WorkflowOrchestrator.reset(orchestrator_tok)
        engine_var.reset(engine_tok)

    async def run(
        self,
        *,
        poll_interval: float = 300,
        max_concurrent_workflows: int = 100,
        lock_duration: timedelta = _DEFAULT_LOCK_DURATION,
        notification_callback: WorkflowNotificationCallback | None = None,
    ):
        if notification_callback:
            async with workflow_notification_context(notification_callback):
                await self.__run(
                    poll_interval=poll_interval,
                    max_concurrent_workflows=max_concurrent_workflows,
                    lock_duration=lock_duration,
                )
        else:
            await self.__run(
                poll_interval=poll_interval,
                max_concurrent_workflows=max_concurrent_workflows,
                lock_duration=lock_duration,
            )


@asynccontextmanager
async def orchestrator_context(orchestrator: WorkflowOrchestrator):
    """Context manager for setting up and tearing down orchestrator context"""
    tok = WorkflowOrchestrator.set(orchestrator)
    try:
        yield orchestrator
    finally:
        WorkflowOrchestrator.reset(tok)
