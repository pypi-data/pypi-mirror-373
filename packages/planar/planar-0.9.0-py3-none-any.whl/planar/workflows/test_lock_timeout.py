import asyncio
from datetime import timedelta

from planar.db import new_session
from planar.session import session_var
from planar.testing.synchronizable_tracer import SynchronizableTracer, TraceSpec
from planar.utils import utc_now
from planar.workflows.decorators import workflow
from planar.workflows.execution import execute
from planar.workflows.models import (
    LockedResource,
    Workflow,
    WorkflowStatus,
    workflow_exec_lock_key,
)
from planar.workflows.orchestrator import WorkflowOrchestrator
from planar.workflows.step_core import Suspend, suspend
from planar.workflows.tracing import tracer_var


# Define a long-running workflow.
@workflow()
async def long_running_workflow():
    # Simulate a long-running operation by sleeping 1 second.
    await asyncio.sleep(1)
    return "finished"


async def test_lock_timer_extension(mem_db_engine):
    tracer = SynchronizableTracer()
    tracer_var.set(tracer)
    lock_acquired = tracer.instrument(
        TraceSpec(function_name="lock_resource", message="commit")
    )
    lock_heartbeat = tracer.instrument(
        TraceSpec(function_name="lock_heartbeat", message="commit")
    )

    async with new_session(mem_db_engine) as session:
        # This test verifies that when a workflow is executing, the heartbeat task
        # (lock_heartbeat) extends the workflow's lock_until field. We run a
        # long-running workflow (which sleeps for 1 second) with a short lock
        # duration and heartbeat interval. While the workflow is running we query
        # the stored workflow record and ensure that lock_until is updated
        # (extended) by the heartbeat.

        session_var.set(session)
        # Start the workflow.
        # Run workflow execution in the background with short durations so
        # heartbeat kicks in quickly.
        async with WorkflowOrchestrator.ensure_started(
            lock_duration=timedelta(seconds=1)
        ) as orchestrator:
            wf: Workflow = await long_running_workflow.start()
            wf_id = wf.id
            lock_key = workflow_exec_lock_key(wf_id)

            await lock_acquired.wait()

            async with session.begin():
                locked_resource = await session.get(LockedResource, lock_key)
            assert locked_resource, "Expected a locked resource record"
            lock_time_1 = locked_resource.lock_until
            assert lock_time_1, "Lock time should be set"

            # Wait a bit longer to allow another heartbeat cycle.
            await lock_heartbeat.wait()
            async with session.begin():
                await session.refresh(locked_resource)
            lock_time_2 = locked_resource.lock_until
            assert lock_time_2, "Lock time should be set"

            # The lock_time_2 should be later than lock_time_1 if the heartbeat is working.
            assert lock_time_2 > lock_time_1, (
                f"Expected lock_until to be extended by heartbeat: {lock_time_1} vs {lock_time_2}"
            )

            # Let the workflow finish.
            await orchestrator.wait_for_completion(wf_id)

            # Verify the workflow completed successfully.
            await session.refresh(wf)
            assert wf.status == WorkflowStatus.SUCCEEDED
            assert wf.result == "finished"


@workflow()
async def crashed_worker_workflow():
    # This workflow uses suspend() to simulate work that is paused.
    # The first execution returns a Suspend object.
    # When resumed it completes and returns "completed".
    # First step: suspend (simulate waiting, e.g. because a worker had locked it).
    await suspend(interval=timedelta(seconds=5))
    # After the suspension it resumes here.
    return "completed"


async def test_orchestrator_resumes_crashed_worker(mem_db_engine):
    # This test simulates the scenario where a worker has “crashed” after
    # locking a workflow. We start a workflow that suspends. Then we add a LockedResource
    # record with an expired lock_until time to simulate a crashed

    # Invoking the workflow_orchestrator (which polls for suspended workflows
    # whose wakeup time is reached or that have expired locks) should cause the
    # the workflow to be resumed. Finally, we verify that the workflow
    # completes successfully. Start the workflow – its first execution will
    # suspend.
    async with new_session(mem_db_engine) as session:
        session_var.set(session)
        wf = await crashed_worker_workflow.start()

        result = await execute(wf)
        assert isinstance(result, Suspend), (
            "Expected the workflow to suspend on first execution."
        )
        # Simulate a crashed worker by directly changing the workflow record.
        await session.refresh(wf)
        # Force wakeup_at and lock_until to be in the past.
        past_time = utc_now() - timedelta(seconds=1)
        wf.wakeup_at = past_time
        session.add(LockedResource(lock_key=f"workflow:{wf.id}", lock_until=past_time))
        # Ensure it is marked as running, which would not normally be picked by
        # the orchestrator
        await session.commit()

        # Now run the orchestrator, which polls for suspended workflows with
        # wakeup_at <= now.
        # We use a short poll interval.
        async with WorkflowOrchestrator.ensure_started(
            poll_interval=0.2
        ) as orchestrator:
            await orchestrator.wait_for_completion(wf.id)

        await session.refresh(wf)
        assert wf.status == WorkflowStatus.SUCCEEDED, (
            f"Expected workflow status 'success' but got {wf.status}"
        )
        assert wf.result == "completed", (
            f"Expected workflow result 'completed' but got {wf.result}"
        )
