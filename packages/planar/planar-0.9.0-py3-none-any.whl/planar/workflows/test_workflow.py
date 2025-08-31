import asyncio
import gc
import json
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

import pytest
from freezegun import freeze_time
from pydantic import BaseModel
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from planar.session import get_session
from planar.testing.workflow_observer import WorkflowObserver
from planar.utils import utc_now
from planar.workflows.decorators import (
    __AS_STEP_CACHE,
    __is_workflow_step,
    as_step,
    step,
    workflow,
)
from planar.workflows.exceptions import NonDeterministicStepCallError
from planar.workflows.execution import execute, lock_and_execute
from planar.workflows.models import (
    StepStatus,
    StepType,
    Workflow,
    WorkflowStatus,
    WorkflowStep,
)
from planar.workflows.notifications import Notification, workflow_notification_context
from planar.workflows.orchestrator import WorkflowOrchestrator
from planar.workflows.step_core import (
    Suspend,
    suspend,
)
from planar.workflows.step_testing_utils import (
    get_step_ancestors,
    get_step_children,
    get_step_descendants,
    get_step_parent,
)


# =============================================================================
# Test 1 – Basic Workflow Lifecycle
# =============================================================================
async def test_workflow_lifecycle(session: AsyncSession):
    @workflow()
    async def sample_workflow():
        return "success"

    wf = await sample_workflow.start()
    await execute(wf)
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf is not None
    assert updated_wf.status == WorkflowStatus.SUCCEEDED
    assert updated_wf.result == "success"


# =============================================================================
# Test 2 – Session Context Is Set
# =============================================================================
async def test_session_context_is_set(session: AsyncSession):
    @workflow()
    async def session_workflow():
        s = get_session()
        # Ensure that the session returned is the one we set from the fixture.
        assert s is session
        return "success"

    wf = await session_workflow.start()
    await execute(wf)
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    assert updated_wf.status == WorkflowStatus.SUCCEEDED
    assert updated_wf.result == "success"


# =============================================================================
# Test 3 – Step Execution and Tracking
# =============================================================================
async def test_step_execution(session: AsyncSession):
    @step()
    async def step1():
        return "step1_result"

    @step()
    async def step2():
        return "step2_result"

    @workflow()
    async def multistep_workflow():
        await step1()
        await step2()
        return "done"

    wf = await multistep_workflow.start()
    await execute(wf)

    steps = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).all()
    assert len(steps) == 2
    fnames = {s.function_name.split(".")[-1] for s in steps}
    assert "step1" in fnames
    assert "step2" in fnames
    for s in steps:
        assert s.status == StepStatus.SUCCEEDED
        assert s.workflow_id == wf.id


# =============================================================================
# Test 4 – Step Error Handling
# =============================================================================
async def test_step_error_handling(session: AsyncSession):
    @step()
    async def failing_step():
        raise ValueError("Intentional failure")

    @workflow()
    async def error_workflow():
        await failing_step()
        return "done"

    wf = await error_workflow.start()
    with pytest.raises(ValueError, match="Intentional failure"):
        await execute(wf)

    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    assert updated_wf.status == WorkflowStatus.FAILED
    step_entry = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).one()
    assert step_entry.error is not None
    assert "Intentional failure" in step_entry.error["message"]


# =============================================================================
# Test 5 – Workflow Resumption (Retry a Failing Step)
# =============================================================================
async def test_workflow_resumption(session: AsyncSession):
    should_fail = True

    @step(max_retries=1)
    async def dynamic_step():
        nonlocal should_fail
        if should_fail:
            raise RuntimeError("Temporary failure")
        return "done"

    @workflow()
    async def resumable_workflow():
        return await dynamic_step()

    wf = await resumable_workflow.start()
    # First execution should suspend (i.e. return a Suspend object) because of failure.
    result1 = await execute(wf)
    assert isinstance(result1, Suspend)
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    assert updated_wf.status == WorkflowStatus.PENDING

    # Fix the error and resume.
    should_fail = False
    result2 = await execute(wf)
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    assert updated_wf.status == WorkflowStatus.SUCCEEDED
    assert result2 == "done"


# =============================================================================
# Test 6 – Input Data Persistence
# =============================================================================
async def test_input_data_persistence(session: AsyncSession):
    @workflow()
    async def data_workflow(a: int, b: int):
        return a + b

    wf = await data_workflow.start(10, 20)
    await execute(wf)
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    assert updated_wf.args == [10, 20]
    assert updated_wf.kwargs == {}
    assert updated_wf.result == 30


# =============================================================================
# Test 7 – Completed Workflow Resumption
# =============================================================================
async def test_completed_workflow_resumption(session: AsyncSession):
    @workflow()
    async def completed_workflow():
        return "final_result"

    wf = await completed_workflow.start()
    result1 = await execute(wf)
    result2 = await execute(wf)
    assert result1 == "final_result"
    assert result2 == "final_result"


# =============================================================================
# Test 8 – Step Idempotency
# =============================================================================
async def test_step_idempotency(session: AsyncSession):
    execution_count = 0

    @step()
    async def idempotent_step():
        nonlocal execution_count
        execution_count += 1
        return "idempotent"

    @workflow()
    async def idempotent_workflow():
        await idempotent_step()
        return "done"

    wf = await idempotent_workflow.start()
    await execute(wf)
    # On resumption the step should not run again.
    await execute(wf)
    assert execution_count == 1


# =============================================================================
# Test 9 – Error Traceback Storage (Adjusted)
# =============================================================================
async def test_error_traceback_storage(session: AsyncSession):
    @step()
    async def error_step():
        raise ValueError("Error with traceback")

    @workflow()
    async def traceback_workflow():
        await error_step()
        return "done"

    wf = await traceback_workflow.start()
    with pytest.raises(ValueError, match="Error with traceback"):
        await execute(wf)

    step_entry = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).one()
    assert step_entry.error is not None
    # The new engine does not store full tracebacks, so we check only the error message.
    assert "Error with traceback" in step_entry.error["message"]


# =============================================================================
# Test 10 – Empty Workflow (No Steps)
# =============================================================================
async def test_empty_workflow(session: AsyncSession):
    @workflow()
    async def empty_workflow():
        return "direct_result"

    wf = await empty_workflow.start()
    await execute(wf)
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    assert updated_wf.status == WorkflowStatus.SUCCEEDED
    assert updated_wf.result == "direct_result"
    # Verify no DurableStep records were created.
    step_entry = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).first()
    assert step_entry is None


# =============================================================================
# Test 11 – Complex Workflow with Retries and Data Persistence
# =============================================================================
async def test_complex_workflow_with_retries_and_data_persistence(
    session: AsyncSession,
):
    step1_attempts = 0
    step2_attempts = 0
    step3_attempts = 0

    @step(max_retries=1)
    async def step1(input_val: int) -> int:
        nonlocal step1_attempts
        step1_attempts += 1
        if step1_attempts == 1:
            raise RuntimeError("Step 1 temporary failure")
        return input_val + 10

    @step(max_retries=1)
    async def step2(input_val: int) -> int:
        nonlocal step2_attempts
        step2_attempts += 1
        if step2_attempts == 1:
            raise RuntimeError("Step 2 temporary failure")
        return input_val * 2

    @step(max_retries=1)
    async def step3(input_val: int) -> int:
        nonlocal step3_attempts
        step3_attempts += 1
        if step3_attempts == 1:
            raise RuntimeError("Step 3 temporary failure")
        return input_val - 5

    @workflow()
    async def chained_workflow(initial_input: int) -> int:
        r1 = await step1(initial_input)
        r2 = await step2(r1)
        r3 = await step3(r2)
        return r3

    wf = await chained_workflow.start(5)
    # First run: step1 fails → workflow suspended.
    await execute(wf)
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    assert updated_wf.status == WorkflowStatus.PENDING
    step1_entry = (
        await session.exec(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == wf.id)
            .where(col(WorkflowStep.function_name).like("%step1%"))
        )
    ).one()
    assert step1_entry.status == StepStatus.FAILED
    assert step1_attempts == 1

    # Second run: step1 succeeds, step2 fails.
    await execute(wf)
    updated_wf = await session.get(Workflow, wf.id)
    step1_entry = (
        await session.exec(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == wf.id)
            .where(col(WorkflowStep.function_name).like("%step1%"))
        )
    ).one()
    assert step1_entry.status == StepStatus.SUCCEEDED
    assert step1_entry.result == 15  # 5 + 10
    assert step1_attempts == 2
    step2_entry = (
        await session.exec(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == wf.id)
            .where(col(WorkflowStep.function_name).like("%step2%"))
        )
    ).one()
    assert step2_entry.status == StepStatus.FAILED
    assert step2_attempts == 1

    # Third run: step2 succeeds, step3 fails.
    await execute(wf)
    updated_wf = await session.get(Workflow, wf.id)
    step2_entry = (
        await session.exec(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == wf.id)
            .where(col(WorkflowStep.function_name).like("%step2%"))
        )
    ).one()
    assert step2_entry.status == StepStatus.SUCCEEDED
    assert step2_entry.result == 30  # 15 * 2
    assert step2_attempts == 2
    step3_entry = (
        await session.exec(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == wf.id)
            .where(col(WorkflowStep.function_name).like("%step3%"))
        )
    ).one()
    assert step3_entry.status == StepStatus.FAILED
    assert step3_attempts == 1

    # Fourth run: step3 succeeds → final result.
    final_result = await execute(wf)
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    assert updated_wf.status == WorkflowStatus.SUCCEEDED
    assert final_result == 25  # 30 - 5
    assert updated_wf.result == 25
    step3_entry = (
        await session.exec(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == wf.id)
            .where(col(WorkflowStep.function_name).like("%step3%"))
        )
    ).one()
    assert step3_entry.status == StepStatus.SUCCEEDED
    assert step3_entry.result == 25
    assert step3_attempts == 2

    # Verify workflow input data persistence.
    assert updated_wf.args == [5]
    assert updated_wf.kwargs == {}


# =============================================================================
# Test 12 – Step Retries
# =============================================================================
async def test_step_retries(session: AsyncSession):
    retry_limit = 3
    attempt_count = 0

    @step(max_retries=retry_limit)
    async def retry_step():
        nonlocal attempt_count
        attempt_count += 1
        raise RuntimeError("Temporary failure")

    @workflow()
    async def retry_workflow():
        await retry_step()
        return "done"

    wf = await retry_workflow.start()

    # Attempt 1
    await execute(wf)
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    assert updated_wf.status == WorkflowStatus.PENDING
    step_entry = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).one()
    assert step_entry.retry_count == 0
    assert attempt_count == 1

    # Attempt 2
    await execute(wf)
    step_entry = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).one()
    assert step_entry.retry_count == 1
    assert attempt_count == 2

    # Attempt 3
    await execute(wf)
    step_entry = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).one()
    assert step_entry.retry_count == 2
    assert attempt_count == 3

    # Attempt 4 – exceed retries so that execution raises.
    with pytest.raises(RuntimeError, match="Temporary failure"):
        await execute(wf)
    step_entry = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).one()
    assert step_entry.retry_count == 3
    assert attempt_count == 4

    # Further execution should not increment attempts.
    with pytest.raises(RuntimeError, match="Temporary failure"):
        await execute(wf)
    step_entry = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).one()
    assert step_entry.retry_count == 3
    assert attempt_count == 4


# =============================================================================
# Test 13 – Looped Step Execution
# =============================================================================
async def test_looped_step_execution(session: AsyncSession):
    loop_count = 3

    @step()
    async def say_hello_step():
        return "hello"

    @workflow()
    async def looped_workflow(count: int):
        for _ in range(count):
            await say_hello_step()
        return "done"

    wf = await looped_workflow.start(loop_count)
    await execute(wf)

    steps = (
        await session.exec(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == wf.id)
            .order_by(col(WorkflowStep.step_id))
        )
    ).all()
    assert len(steps) == loop_count
    for i, s in enumerate(steps, start=1):
        assert s.function_name.split(".")[-1] == "say_hello_step"
        assert s.step_id == i
        assert s.status == StepStatus.SUCCEEDED


# =============================================================================
# Test 14 – Basic Sleep Functionality
# =============================================================================
async def test_basic_sleep_functionality(session: AsyncSession):
    with freeze_time("2024-01-01 00:00:00") as frozen_time:

        @workflow()
        async def sleeping_workflow():
            await suspend(interval=timedelta(seconds=10))
            return "awake"

        wf = await sleeping_workflow.start()
        result = await execute(wf)
        updated_wf = await session.get(Workflow, wf.id)
        assert updated_wf
        # The suspend step should have returned a Suspend object.
        assert isinstance(result, Suspend)
        assert updated_wf.status == WorkflowStatus.PENDING
        expected_wakeup = datetime(2024, 1, 1, 0, 0, 10)
        assert updated_wf.wakeup_at == expected_wakeup

        # Check that the suspend step record has function_name 'suspend'
        sleep_step = (
            await session.exec(
                select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
            )
        ).one()
        assert sleep_step.function_name.split(".")[-1] == "suspend"

        # Move time forward and resume.
        frozen_time.move_to("2024-01-01 00:00:11")
        final_result = await execute(wf)
        assert final_result == "awake"
        assert updated_wf.status == WorkflowStatus.SUCCEEDED


# =============================================================================
# Test 15 – Worker Skips Sleeping Workflows
# =============================================================================
async def test_worker_skips_sleeping_workflows(session: AsyncSession):
    @workflow()
    async def sleeping_workflow():
        await suspend(interval=timedelta(minutes=5))
        return "done"

    wf = await sleeping_workflow.start()
    # Execute once to suspend.
    result = await execute(wf)
    assert isinstance(result, Suspend)

    # Simulate the worker’s query for ready workflows.
    ready_wfs = (
        await session.exec(
            select(Workflow)
            .where(Workflow.status == WorkflowStatus.PENDING)
            .where(col(Workflow.wakeup_at) <= utc_now())
        )
    ).all()
    # At 12:00 the wakeup time (12:05) is in the future.
    assert len(ready_wfs) == 0

    result = await execute(wf)
    assert result == "done"


# =============================================================================
# Test 16 – Multiple Sleep Steps
# =============================================================================
async def test_multiple_sleep_steps(session: AsyncSession):
    @workflow()
    async def multi_sleep_workflow():
        await suspend(interval=timedelta(seconds=2))
        await suspend(interval=timedelta(seconds=4))
        return 42

    start_date = utc_now()
    wf = await multi_sleep_workflow.start()
    assert wf
    # First run: suspend for 10 seconds.
    result = await execute(wf)
    assert isinstance(result, Suspend)
    await session.refresh(wf)
    assert wf.wakeup_at
    assert (wf.wakeup_at - start_date) >= timedelta(seconds=2)
    assert (wf.wakeup_at - start_date) <= timedelta(seconds=3)

    # Move time forward and resume.
    await asyncio.sleep(2)
    result = await execute(wf)
    assert isinstance(result, Suspend)
    await session.refresh(wf)
    assert (wf.wakeup_at - start_date) >= timedelta(seconds=6)
    assert (wf.wakeup_at - start_date) <= timedelta(seconds=7)

    # Verify that two suspend steps were recorded.
    sleep_steps = (
        await session.exec(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == wf.id)
            .order_by(col(WorkflowStep.step_id))
        )
    ).all()
    assert len(sleep_steps) == 2
    assert [s.step_id for s in sleep_steps] == [1, 2]

    # Final execution after second sleep.
    await asyncio.sleep(4.5)
    final_result = await execute(wf)
    assert final_result == 42


# =============================================================================
# Test 17 – Looped Execution with Step Dependencies
# =============================================================================
async def test_looped_execution_with_step_dependencies(session: AsyncSession):
    step_attempts = defaultdict(int)
    expected_results = []

    @step(max_retries=1)
    async def process_step(input_val: int) -> int:
        step_attempts[input_val] += 1
        if step_attempts[input_val] == 1:
            raise RuntimeError(f"Temporary failure for input {input_val}")
        return input_val + 5

    @workflow()
    async def looped_dependency_workflow(initial: int) -> int:
        nonlocal expected_results
        expected_results = []
        current = initial
        for _ in range(3):
            current = await process_step(current)
            expected_results.append(current)
        return current

    wf = await looped_dependency_workflow.start(10)
    # Run through several execution attempts until the workflow finishes.
    for _ in range(6):
        try:
            await execute(wf)
        except Exception:
            pass

    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    assert updated_wf.status == WorkflowStatus.SUCCEEDED
    # 10 → 15 → 20 → 25
    assert updated_wf.result == 25

    steps = (
        await session.exec(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == wf.id)
            .order_by(col(WorkflowStep.step_id))
        )
    ).all()
    assert len(steps) == 3
    assert all("process_step" in s.function_name for s in steps)
    assert [s.result for s in steps] == [15, 20, 25]

    # Each step should have retried exactly once.
    for s in steps:
        assert s.retry_count == 1

    # Verify that error messages were recorded on failed attempts.
    step_errors = (
        await session.exec(
            select(WorkflowStep.error)
            .where(WorkflowStep.workflow_id == wf.id)
            .where(WorkflowStep.status == StepStatus.SUCCEEDED)
        )
    ).all()
    for err in step_errors:
        if err:
            assert "Temporary failure" in err["message"]

    assert expected_results == [15, 20, 25]


async def test_handling_step_errors(session: AsyncSession):
    @step(max_retries=0)
    async def step1():
        raise ValueError("Step 1 error")

    @workflow()
    async def step_try_catch_workflow():
        try:
            await step1()
        except ValueError:
            # Suspend the workflow in the except block
            await suspend(interval=timedelta(seconds=5))
            return "handled"
        return "done"

    # Start the workflow
    wf = await step_try_catch_workflow.start()

    # First execution: should raise ValueError in step1, catch it, call
    # sleep(...) -> suspended
    result = await execute(wf)
    # Expect a Suspend object because the workflow is waiting
    assert isinstance(result, Suspend)

    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf is not None
    assert updated_wf.status == WorkflowStatus.PENDING
    assert updated_wf.wakeup_at is not None

    # Verify that two step records were created:
    steps = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).all()
    assert len(steps) == 2
    # The first step (step1) failed
    assert steps[0].status == StepStatus.FAILED
    assert steps[0].result is None

    # --- Second execution: after wakeup time
    final_result = await execute(wf)
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    # Now the workflow should resume and finish, returning "handled"
    assert final_result == "handled"
    assert updated_wf.status == WorkflowStatus.SUCCEEDED
    assert updated_wf.result == "handled"

    # Finally, verify the step records remain as expected.
    steps = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).all()
    assert len(steps) == 2
    assert steps[0].status == StepStatus.FAILED
    assert steps[0].result is None
    assert steps[1].status == StepStatus.SUCCEEDED
    assert steps[1].error is None


async def test_exceute_properly_intercepts_coroutine(session: AsyncSession):
    async def shell(cmd: str):
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        return stdout.decode().strip()

    @step()
    async def step1():
        echo_output = await non_step1()
        assert echo_output == "echoing 20"
        count = int(echo_output.split()[-1])
        for _ in range(10):
            await asyncio.sleep(0.01)
            count += 1
        return count

    async def non_step1():
        count = 0
        for _ in range(10):
            await asyncio.sleep(0.01)
            count += 1
        return await step2(count)

    @step()
    async def step2(count: int):
        return await non_step2(count)

    async def non_step2(count: int):
        for _ in range(count):
            await asyncio.sleep(0.01)
            count += 1
        return await shell(f"echo echoing {count}")

    @step()
    async def step3(count: int):
        for _ in range(10):
            await asyncio.sleep(0.01)
            count += 1
        return count

    @workflow()
    async def nested_step_and_non_step_calls():
        count = await step1()
        count = await step3(count)
        return count

    wf = await nested_step_and_non_step_calls.start()
    await execute(wf)
    assert wf.status == WorkflowStatus.SUCCEEDED
    assert wf.result == 40

    steps = (
        await session.exec(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == wf.id)
            .order_by(col(WorkflowStep.step_id))
        )
    ).all()
    for s in steps:
        s.function_name = s.function_name.split(".")[-1]

    assert all(s.status == StepStatus.SUCCEEDED for s in steps)
    assert tuple(s.function_name.split(".")[-1] for s in steps) == (
        "step1",
        "step2",
        "step3",
    )
    assert tuple(s.result for s in steps) == (30, "echoing 20", 40)


async def test_sub_workflows(session: AsyncSession):
    @step()
    async def step1(n: int) -> Decimal:
        await suspend(interval=timedelta(seconds=0.1))
        return Decimal(1 + n)

    @step()
    async def step2(n: int) -> Decimal:
        await suspend(interval=timedelta(seconds=0.1))
        return Decimal(2 + n)

    @step()
    async def step3(n: int) -> Decimal:
        await suspend(interval=timedelta(seconds=0.1))
        return Decimal(3 + n)

    @workflow()
    async def workflow1(n: int) -> Decimal:
        return await step1(n)

    @workflow()
    async def workflow2(n: int) -> Decimal:
        return await step2(n)

    @workflow()
    async def workflow3(n: int) -> Decimal:
        return await step3(n)

    @workflow()
    async def call_sub_workflows() -> Decimal:
        w1 = await workflow1(1)
        w2 = await workflow2(2)
        w3 = await workflow3(3)
        assert w1 == Decimal(2)
        assert w2 == Decimal(4)
        assert w3 == Decimal(6)
        return w1 + w2 + w3

    async with WorkflowOrchestrator.ensure_started() as orchestrator:
        wf = await call_sub_workflows.start()
        result = await orchestrator.wait_for_completion(wf.id)

    await session.refresh(wf)
    assert wf.status == WorkflowStatus.SUCCEEDED
    assert result == Decimal(12)

    all_workflows = []
    workflows = (
        await session.exec(select(Workflow).order_by(col(Workflow.created_at)))
    ).all()
    for w in workflows:
        steps = (
            await session.exec(
                select(WorkflowStep)
                .where(col(WorkflowStep.workflow_id) == w.id)
                .order_by(col(WorkflowStep.step_id))
            )
        ).all()
        all_workflows.append(
            {
                "status": w.status,
                "function_name": w.function_name.split(".")[-1],
                "steps": [
                    {
                        "step_id": s.step_id,
                        "step_status": s.status,
                        "function_name": s.function_name.split(".")[-1],
                    }
                    for s in steps
                ],
            }
        )

    assert all_workflows == [
        {
            "status": WorkflowStatus.SUCCEEDED,
            "function_name": "call_sub_workflows",
            "steps": [
                {
                    "step_id": 1,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "start_workflow_step",
                },
                {
                    "step_id": 2,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "start_workflow_step",
                },
                {
                    "step_id": 3,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "start_workflow_step",
                },
            ],
        },
        {
            "status": WorkflowStatus.SUCCEEDED,
            "function_name": "workflow1",
            "steps": [
                {
                    "step_id": 1,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "step1",
                },
                {
                    "step_id": 2,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "suspend",
                },
            ],
        },
        {
            "status": WorkflowStatus.SUCCEEDED,
            "function_name": "workflow2",
            "steps": [
                {
                    "step_id": 1,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "step2",
                },
                {
                    "step_id": 2,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "suspend",
                },
            ],
        },
        {
            "status": WorkflowStatus.SUCCEEDED,
            "function_name": "workflow3",
            "steps": [
                {
                    "step_id": 1,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "step3",
                },
                {
                    "step_id": 2,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "suspend",
                },
            ],
        },
    ]


@pytest.mark.xfail(reason="Not supported for now")
async def test_sub_workflows_concurrent_execution(session: AsyncSession):
    @step()
    async def step1(n: int):
        await suspend(interval=timedelta(seconds=0.1))
        return 1 + n

    @step()
    async def step2(n: int):
        await suspend(interval=timedelta(seconds=0.1))
        return 2 + n

    @step()
    async def step3(n: int):
        await suspend(interval=timedelta(seconds=0.1))
        return 3 + n

    @workflow()
    async def workflow1(n: int):
        return await step1(n)

    @workflow()
    async def workflow2(n: int):
        return await step2(n)

    @workflow()
    async def workflow3(n: int):
        return await step3(n)

    @workflow()
    async def concurrent_call_sub_workflows():
        w1, w2, w3 = await asyncio.gather(workflow1(1), workflow2(2), workflow3(3))
        return w1 + w2 + w3

    async with WorkflowOrchestrator.ensure_started() as orchestrator:
        wf = await concurrent_call_sub_workflows.start()
        await orchestrator.wait_for_completion(wf.id)

    await session.refresh(wf)
    assert wf.status == WorkflowStatus.SUCCEEDED
    assert wf.result == 12

    all_workflows = []
    workflows = (
        await session.exec(select(Workflow).order_by(col(Workflow.created_at)))
    ).all()
    for w in workflows:
        steps = (
            await session.exec(
                select(WorkflowStep)
                .where(col(WorkflowStep.workflow_id) == w.id)
                .order_by(col(WorkflowStep.step_id))
            )
        ).all()
        all_workflows.append(
            {
                "status": w.status,
                "function_name": w.function_name.split(".")[-1],
                "steps": [
                    {
                        "step_id": s.step_id,
                        "step_status": s.status,
                        "function_name": s.function_name.split(".")[-1],
                    }
                    for s in steps
                ],
                "result": w.result,
            }
        )

    assert all_workflows == [
        {
            "status": WorkflowStatus.SUCCEEDED,
            "function_name": "concurrent_call_sub_workflows",
            "steps": [
                {
                    "step_id": 1,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "start_workflow_step",
                },
                {
                    "step_id": 2,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "start_workflow_step",
                },
                {
                    "step_id": 3,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "start_workflow_step",
                },
            ],
            "result": 12,
        },
        {
            "status": WorkflowStatus.SUCCEEDED,
            "function_name": "workflow1",
            "steps": [
                {
                    "step_id": 1,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "step1",
                },
                {
                    "step_id": 2,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "suspend",
                },
            ],
            "result": 2,
        },
        {
            "status": WorkflowStatus.SUCCEEDED,
            "function_name": "workflow2",
            "steps": [
                {
                    "step_id": 1,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "step2",
                },
                {
                    "step_id": 2,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "suspend",
                },
            ],
            "result": 4,
        },
        {
            "status": WorkflowStatus.SUCCEEDED,
            "function_name": "workflow3",
            "steps": [
                {
                    "step_id": 1,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "step3",
                },
                {
                    "step_id": 2,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "suspend",
                },
            ],
            "result": 6,
        },
    ]


@pytest.mark.xfail(reason="Not supported for now")
async def test_step_can_be_scheduled_as_tasks(session: AsyncSession):
    @step()
    async def step1():
        s2, s3, s4 = await asyncio.gather(step2(), step3(), step4())
        return s2 + s3 + s4

    @step()
    async def step2():
        await suspend(interval=timedelta(seconds=0.1))
        return 2

    @step()
    async def step3():
        await suspend(interval=timedelta(seconds=0.1))
        return 3

    @step()
    async def step4():
        await suspend(interval=timedelta(seconds=0.1))
        return 4

    @workflow()
    async def execute_steps_in_parallel():
        return await step1()

    async with WorkflowOrchestrator.ensure_started() as orchestrator:
        wf = await execute_steps_in_parallel.start()
        await orchestrator.wait_for_completion(wf.id)

    await session.refresh(wf)
    assert wf.status == WorkflowStatus.SUCCEEDED
    assert wf.result == 9

    all_workflows = []
    workflows = (
        await session.exec(select(Workflow).order_by(col(Workflow.created_at)))
    ).all()
    for w in workflows:
        steps = (
            await session.exec(
                select(WorkflowStep)
                .where(col(WorkflowStep.workflow_id) == w.id)
                .order_by(col(WorkflowStep.step_id))
            )
        ).all()
        all_workflows.append(
            {
                "status": w.status,
                "function_name": w.function_name.split(".")[-1],
                "steps": [
                    {
                        "step_id": s.step_id,
                        "step_status": s.status,
                        "function_name": s.function_name.split(".")[-1],
                    }
                    for s in steps
                ],
                "result": w.result,
            }
        )

    assert all_workflows == [
        {
            "status": WorkflowStatus.SUCCEEDED,
            "function_name": "execute_steps_in_parallel",
            "steps": [
                {
                    "step_id": 1,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "step1",
                },
                {
                    "step_id": 2,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "start_workflow_step",
                },
                {
                    "step_id": 3,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "start_workflow_step",
                },
                {
                    "step_id": 4,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "start_workflow_step",
                },
            ],
            "result": 9,
        },
        {
            "status": WorkflowStatus.SUCCEEDED,
            "function_name": "auto_workflow",
            "steps": [
                {
                    "step_id": 1,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "step2",
                },
                {
                    "step_id": 2,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "suspend",
                },
            ],
            "result": 2,
        },
        {
            "status": WorkflowStatus.SUCCEEDED,
            "function_name": "auto_workflow",
            "steps": [
                {
                    "step_id": 1,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "step3",
                },
                {
                    "step_id": 2,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "suspend",
                },
            ],
            "result": 3,
        },
        {
            "status": WorkflowStatus.SUCCEEDED,
            "function_name": "auto_workflow",
            "steps": [
                {
                    "step_id": 1,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "step4",
                },
                {
                    "step_id": 2,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "suspend",
                },
            ],
            "result": 4,
        },
    ]


async def test_nested_workflow_started_from_nested_step_failed(session: AsyncSession):
    @step()
    async def update_inbound_document_with_classification(
        item_id: str, classification: str
    ) -> bool:
        await asyncio.sleep(0.1)
        raise Exception(f"some issue with {item_id}/{classification}")

    @workflow()
    async def classify_inbound_document(item_id: str, attachment_id: str):
        await update_inbound_document_with_classification(item_id, "classified")

    @step()
    async def upload_documents_from_email(limit: int) -> list[str]:
        await asyncio.sleep(0.1)
        return [
            json.dumps({"item_id": "doc 1", "attachment_id": "attachment 1"}),
        ]

    @step()
    async def start_classify_inbound_document_workflow(
        inbound_document_with_attachment: str,
    ):
        obj = json.loads(inbound_document_with_attachment)
        await classify_inbound_document(obj["item_id"], obj["attachment_id"])

    @workflow()
    async def email_documents_uploader(limit: int = 10) -> list[str]:
        inbound_documents_with_attachments = await upload_documents_from_email(limit)
        for doc in inbound_documents_with_attachments:
            await start_classify_inbound_document_workflow(doc)
        return inbound_documents_with_attachments

    wf = await email_documents_uploader.start()
    async with WorkflowOrchestrator.ensure_started(poll_interval=1) as orchestrator:
        with pytest.raises(Exception, match="some issue with doc 1/classified"):
            await orchestrator.wait_for_completion(wf.id)

    all_workflows = []
    workflows = (
        await session.exec(select(Workflow).order_by(col(Workflow.created_at)))
    ).all()
    for w in workflows:
        steps = (
            await session.exec(
                select(WorkflowStep)
                .where(col(WorkflowStep.workflow_id) == w.id)
                .order_by(col(WorkflowStep.step_id))
            )
        ).all()
        all_workflows.append(
            {
                "status": w.status,
                "function_name": w.function_name.split(".")[-1],
                "steps": [
                    {
                        "step_id": s.step_id,
                        "step_status": s.status,
                        "function_name": s.function_name.split(".")[-1],
                    }
                    for s in steps
                ],
            }
        )

    assert all_workflows == [
        {
            "status": WorkflowStatus.FAILED,
            "function_name": "email_documents_uploader",
            "steps": [
                {
                    "step_id": 1,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "upload_documents_from_email",
                },
                {
                    "step_id": 2,
                    "step_status": StepStatus.FAILED,
                    "function_name": "start_classify_inbound_document_workflow",
                },
                {
                    "step_id": 3,
                    "step_status": StepStatus.SUCCEEDED,
                    "function_name": "start_workflow_step",
                },
            ],
        },
        {
            "status": WorkflowStatus.FAILED,
            "function_name": "classify_inbound_document",
            "steps": [
                {
                    "function_name": "update_inbound_document_with_classification",
                    "step_id": 1,
                    "step_status": StepStatus.FAILED,
                }
            ],
        },
    ]


# =============================================================================
# Tests for Non-Deterministic Step Call Detection
# =============================================================================
async def test_non_deterministic_step_detection_args(session: AsyncSession):
    # Track whether we're in first or second execution attempt
    is_first_execution = [True]

    class ConfigModel(BaseModel):
        name: str
        value: int
        nested: dict[str, str]

    @step(max_retries=1)
    async def failing_step_with_model(config: ConfigModel) -> str:
        # First execution will always fail
        if is_first_execution[0]:
            is_first_execution[0] = False
            raise RuntimeError("First attempt fails deliberately")

        # Return something (won't matter for the test)
        return f"Processed {config.name} with value {config.value}"

    @workflow()
    async def model_workflow() -> str:
        # First execution will use this config
        config = ConfigModel(name="test-config", value=42, nested={"key": "original"})

        # On retry, we'll modify the config in a non-deterministic way
        if not is_first_execution[0]:
            # This change should be detected as non-deterministic
            config = ConfigModel(
                name="test-config",
                value=42,
                nested={"key": "modified"},  # Change in nested field
            )

        return await failing_step_with_model(config)

    # Start and execute the workflow
    wf = await model_workflow.start()

    # First execution will fail but set up for retry
    await execute(wf)

    # Verify the workflow is in pending state with a failed step
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    assert updated_wf.status == WorkflowStatus.PENDING

    # Find the step record
    s = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).one()
    assert s.status == StepStatus.FAILED
    assert s.retry_count == 0

    # Second execution should fail with NonDeterministicStepCallError
    # because the nested field was changed
    with pytest.raises(
        NonDeterministicStepCallError,
        match="Non-deterministic step call detected at step ID 1. Previous args",
    ) as excinfo:
        await execute(wf)

    # Verify error message contains information about the non-deterministic input
    err_msg = str(excinfo.value)
    assert "Non-deterministic step call detected" in err_msg
    assert "nested" in err_msg or "original" in err_msg or "modified" in err_msg


async def test_non_deterministic_step_detection_kwargs(session: AsyncSession):
    # Track whether we're in first or second execution attempt
    is_first_execution = [True]

    class ConfigModel(BaseModel):
        name: str
        value: int
        options: dict[str, bool]

    @step(max_retries=1)
    async def failing_step_with_kwargs(
        basic_value: int, *, config: ConfigModel, flag: bool = False
    ) -> str:
        # First execution will always fail
        if is_first_execution[0]:
            is_first_execution[0] = False
            raise RuntimeError("First attempt fails deliberately")

        # Return something (won't matter for the test)
        return f"Processed with {basic_value} and {config.name}"

    @workflow()
    async def kwargs_workflow() -> str:
        # First execution will use these values
        basic_value = 100
        config = ConfigModel(
            name="config-1", value=42, options={"debug": True, "verbose": False}
        )
        flag = False

        # On retry, we'll modify the kwargs in a non-deterministic way
        if not is_first_execution[0]:
            # This kwargs change should be detected as non-deterministic
            flag = True  # Changed from False to True

        return await failing_step_with_kwargs(basic_value, config=config, flag=flag)

    # Start and execute the workflow
    wf = await kwargs_workflow.start()

    # First execution will fail but set up for retry
    await execute(wf)

    # Verify the workflow is in pending state with a failed step
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    assert updated_wf.status == WorkflowStatus.PENDING

    # Find the step record
    s = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).one()
    assert s.status == StepStatus.FAILED
    assert s.retry_count == 0

    # Second execution should fail with NonDeterministicStepCallError
    # because the flag kwarg was changed
    with pytest.raises(
        NonDeterministicStepCallError,
        match="Non-deterministic step call detected at step ID 1. Previous kwargs",
    ) as excinfo:
        await execute(wf)

    # Verify error message contains information about the non-deterministic input
    err_msg = str(excinfo.value)
    assert "Non-deterministic step call detected" in err_msg
    assert "flag" in err_msg


async def test_non_deterministic_step_detection_function(session: AsyncSession):
    # Track whether we're in first or second execution attempt
    is_first_execution = [True]

    @step(max_retries=1)
    async def first_step(value: int) -> int:
        is_first_execution[0] = False
        raise RuntimeError("First step fails deliberately")

    @step()
    async def second_step(value: int) -> int:
        return value * 2

    @workflow()
    async def different_step_workflow() -> int:
        initial_value = 5

        # On first execution, call first_step
        if is_first_execution[0]:
            return await first_step(initial_value)
        else:
            # On retry, call a completely different step
            # This should be detected as non-deterministic
            return await second_step(initial_value)

    # Start and execute the workflow
    wf = await different_step_workflow.start()

    # First execution will fail but set up for retry
    await execute(wf)

    # Verify the workflow is in pending state with a failed step
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    assert updated_wf.status == WorkflowStatus.PENDING

    # Find the step record
    s = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).one()
    assert s.status == StepStatus.FAILED
    assert s.retry_count == 0

    # Second execution should fail with NonDeterministicStepCallError
    # because we're calling a completely different step
    with pytest.raises(
        NonDeterministicStepCallError,
        match="Non-deterministic step call detected at step ID 1. Previous function name",
    ) as excinfo:
        await execute(wf)

    # Verify error message contains information about the non-deterministic function call
    err_msg = str(excinfo.value)
    assert "Non-deterministic step call detected" in err_msg
    assert "first_step" in err_msg and "second_step" in err_msg


async def test_task_cancellation(session: AsyncSession):
    @step()
    async def handled_cancellation_step():
        try:
            asyncio.create_task(canceller(asyncio.current_task()))
            await asyncio.sleep(10)
            return "completed"
        except asyncio.CancelledError:
            return "cancelled"

    @step()
    async def unhandled_cancellation_step():
        asyncio.create_task(canceller(asyncio.current_task()))
        await asyncio.sleep(10)
        return "completed2"

    @workflow()
    async def cancellation_workflow():
        result = await handled_cancellation_step()
        try:
            return await unhandled_cancellation_step()
        except asyncio.CancelledError:
            return f'first step result: "{result}". second step cancelled'

    async def canceller(task: asyncio.Task | None):
        assert task
        task.cancel()

    async with WorkflowOrchestrator.ensure_started() as orchestrator:
        wf = await cancellation_workflow.start()
        await orchestrator.wait_for_completion(wf.id)

    await session.refresh(wf)
    steps = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).all()
    assert len(steps) == 2
    assert steps[0].status == StepStatus.SUCCEEDED
    assert steps[0].result == "cancelled"
    assert steps[1].status == StepStatus.FAILED
    assert steps[1].error
    assert steps[1].error["type"] == "CancelledError"
    assert wf.status == WorkflowStatus.SUCCEEDED
    assert wf.result == 'first step result: "cancelled". second step cancelled'


async def test_as_step_helper(session: AsyncSession):
    # Force garbage collection to ensure any non-referenced cached functions are removed
    gc.collect()

    # Store the initial cache count since our assertions will be based on it
    initial_cache_count = len(__AS_STEP_CACHE)

    # Create a regular coroutine function (not a step)
    async def regular_function(value: int) -> int:
        return value * 2

    # Verify it's not already a step
    assert not __is_workflow_step(regular_function)

    # Convert it to a step
    step_function = as_step(regular_function, step_type=StepType.COMPUTE)

    # Verify it's now recognized as a step
    assert __is_workflow_step(step_function)

    # Calling as_step again should return the same cached step function
    step_function_again = as_step(regular_function, step_type=StepType.COMPUTE)
    assert step_function is step_function_again

    # Create a workflow that uses the step
    @workflow()
    async def as_step_workflow(input_value: int) -> int:
        result = await step_function(input_value)
        return result

    # Execute the workflow
    wf = await as_step_workflow.start(5)
    result = await execute(wf)

    # Verify the workflow completed successfully
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf
    assert updated_wf.status == WorkflowStatus.SUCCEEDED
    assert result == 10  # 5 * 2

    # Verify a step was created and executed
    steps = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).all()
    assert len(steps) == 1
    assert steps[0].status == StepStatus.SUCCEEDED
    assert steps[0].result == 10

    # Test with an already-decorated step function
    @step()
    async def already_step_function(value: int) -> int:
        return value + 10

    # as_step should return the original function if it's already a step
    same_step = as_step(already_step_function, step_type=StepType.COMPUTE)
    assert same_step is already_step_function

    # Create and execute a workflow using the already-step function
    @workflow()
    async def existing_step_workflow(input_value: int) -> int:
        result = await already_step_function(input_value)
        return result

    wf2 = await existing_step_workflow.start(7)
    result2 = await execute(wf2)

    # Verify workflow execution
    updated_wf2 = await session.get(Workflow, wf2.id)
    assert updated_wf2
    assert updated_wf2.status == WorkflowStatus.SUCCEEDED
    assert result2 == 17  # 7 + 10

    #  We should have 1 entry in the cache at this point.
    assert len(__AS_STEP_CACHE) == initial_cache_count + 1

    # Test that WeakKeyDictionary prevents memory leaks
    def create_temp_function():
        # Create a function that will go out of scope
        async def temp_function(x: int) -> int:
            return x * 3

        # Apply as_step to the function
        as_step(temp_function, step_type=StepType.COMPUTE)

        return temp_function

    # Create a temporary function which will have `as_step` applied on it
    temp_function = create_temp_function()

    # Verify that the new function is in the cache
    assert len(__AS_STEP_CACHE) == initial_cache_count + 2

    # Clear the reference to the function
    temp_function = None
    assert temp_function is None  # use the variable to make linter happy

    # Force garbage collection
    gc.collect()

    # Verify the weak reference is now None (object was garbage collected)
    assert len(__AS_STEP_CACHE) == initial_cache_count + 1


async def test_workflow_notifications(session: AsyncSession):
    """Test that all workflow notifications are delivered correctly."""
    # Create a WorkflowObserver to capture notifications
    observer = WorkflowObserver()
    exec_count = 0

    @step(max_retries=1)
    async def some_step():
        nonlocal exec_count
        if exec_count == 0:
            exec_count += 1
            raise Exception("First execution")
        return "success"

    @workflow()
    async def notification_workflow():
        await some_step()
        return "done"

    async def wait_notifications(workflow_id: UUID):
        # First execution fails
        await observer.wait(Notification.WORKFLOW_STARTED, workflow_id)
        await observer.wait(Notification.WORKFLOW_RESUMED, workflow_id)
        await observer.wait(Notification.STEP_RUNNING, workflow_id)
        await observer.wait(Notification.STEP_FAILED, workflow_id)
        await observer.wait(Notification.WORKFLOW_SUSPENDED, workflow_id)

        # # Second execution succeeds
        await observer.wait(Notification.WORKFLOW_RESUMED, workflow_id)
        await observer.wait(Notification.STEP_RUNNING, workflow_id)
        await observer.wait(Notification.STEP_SUCCEEDED, workflow_id)
        await observer.wait(Notification.WORKFLOW_SUCCEEDED, workflow_id)

    async with workflow_notification_context(observer.on_workflow_notification):
        wf = await notification_workflow.start()
        wait_task = asyncio.create_task(wait_notifications(wf.id))
        # execution 1
        await lock_and_execute(wf)
        # execution 2
        await lock_and_execute(wf)

    # Verify we received all notifications by simply waiting the task
    await wait_task


# =============================================================================
# Test for Step Hierarchy Implementation
# =============================================================================
async def test_step_hierarchy_implementation(session: AsyncSession):
    """Test that the step hierarchy is correctly implemented with parent-child relationships."""

    @step()
    async def parent_step():
        return await child_step()

    @step()
    async def child_step():
        return await grandchild_step()

    @step()
    async def grandchild_step():
        return "done"

    @workflow()
    async def hierarchy_workflow():
        return await parent_step()

    # Run the workflow
    wf = await hierarchy_workflow.start()
    await lock_and_execute(wf)

    # Get all steps for this workflow
    steps = (
        await session.exec(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == wf.id)
            .order_by(col(WorkflowStep.step_id))
        )
    ).all()

    # We should have 3 steps
    assert len(steps) == 3

    # Verify step types
    assert steps[0].function_name.split(".")[-1] == "parent_step"
    assert steps[1].function_name.split(".")[-1] == "child_step"
    assert steps[2].function_name.split(".")[-1] == "grandchild_step"

    parent_step_id = steps[0].step_id
    descendant_step_ids = [steps[1].step_id, steps[2].step_id]

    for descendant_step_id in descendant_step_ids:
        assert parent_step_id < descendant_step_id

    # Verify parent-child relationships
    assert steps[0].parent_step_id is None  # Parent has no parent
    assert steps[1].parent_step_id == steps[0].step_id  # Child's parent is parent
    assert steps[2].parent_step_id == steps[1].step_id  # Grandchild's parent is child

    # Verify hierarchy utility functions

    # 1. Get parent
    parent = await get_step_parent(steps[2])  # Get parent of grandchild
    assert parent is not None
    assert parent.step_id == steps[1].step_id
    assert parent.function_name == steps[1].function_name

    # 2. Get children
    children = await get_step_children(steps[0])  # Get children of parent
    assert len(children) == 1
    assert children[0].step_id == steps[1].step_id

    # 3. Get descendants
    descendants = await get_step_descendants(steps[0])  # Get all descendants of parent
    assert len(descendants) == 2
    descendant_ids = sorted([d.step_id for d in descendants])
    assert descendant_ids == [steps[1].step_id, steps[2].step_id]

    # Get ancestors of grandchild
    ancestors = await get_step_ancestors(steps[2])
    assert len(ancestors) == 2
    assert (
        ancestors[0].step_id == steps[1].step_id
    )  # First ancestor is the immediate parent
    assert (
        ancestors[1].step_id == steps[0].step_id
    )  # Second ancestor is the grandparent


async def test_basic_step_parent_child(session: AsyncSession):
    """Basic test of parent-child relationship."""

    @step()
    async def parent():
        return await child()

    @step()
    async def child():
        return "done"

    @workflow()
    async def parent_child_workflow():
        return await parent()

    wf = await parent_child_workflow.start()
    await lock_and_execute(wf)

    steps = (
        await session.exec(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == wf.id)
            .order_by(col(WorkflowStep.step_id))
        )
    ).all()

    assert len(steps) == 2
    parent_step = steps[0]
    child_step = steps[1]

    assert parent_step.step_id < child_step.step_id

    # Test parent-child relationship
    assert child_step.parent_step_id == parent_step.step_id
    assert parent_step.parent_step_id is None


async def test_child_workflow_called_as_function_has_parent_id(session: AsyncSession):
    @workflow()
    async def child_workflow():
        return "child_result"

    @workflow()
    async def parent_workflow():
        # Call child workflow as async function - this should set parent_id
        result = await child_workflow()
        return f"parent got: {result}"

    # Start parent workflow
    parent_wf = await parent_workflow.start()

    async with WorkflowOrchestrator.ensure_started() as orchestrator:
        await orchestrator.wait_for_completion(parent_wf.id)

    # Verify parent workflow completed successfully
    await session.refresh(parent_wf)
    assert parent_wf.status == WorkflowStatus.SUCCEEDED
    assert parent_wf.result == "parent got: child_result"

    # Get all workflows and find the child workflow
    all_workflows = (
        await session.exec(select(Workflow).order_by(col(Workflow.created_at)))
    ).all()

    assert len(all_workflows) == 2
    child_wf = next(wf for wf in all_workflows if wf.id != parent_wf.id)

    # Verify child workflow has parent_id set to parent workflow
    assert child_wf.parent_id == parent_wf.id
    assert child_wf.status == WorkflowStatus.SUCCEEDED
    assert child_wf.result == "child_result"


async def test_child_workflow_called_as_start_step(session: AsyncSession):
    child_workflow_id = None

    @workflow()
    async def child_workflow():
        return "child_result"

    @workflow()
    async def parent_workflow():
        nonlocal child_workflow_id
        # Call child workflow using start_step - this should NOT set parent_id
        child_workflow_id = await child_workflow.start_step()
        return f"started child: {child_workflow_id}"

    # Start parent workflow
    parent_wf = await parent_workflow.start()

    async with WorkflowOrchestrator.ensure_started() as orchestrator:
        await orchestrator.wait_for_completion(parent_wf.id)
        assert child_workflow_id
        await orchestrator.wait_for_completion(child_workflow_id)

    # Verify parent workflow completed successfully
    await session.refresh(parent_wf)
    assert parent_wf.status == WorkflowStatus.SUCCEEDED

    # Get all workflows and find the child workflow
    all_workflows = (
        await session.exec(select(Workflow).order_by(col(Workflow.created_at)))
    ).all()

    assert len(all_workflows) == 2
    child_wf = next(wf for wf in all_workflows if wf.id != parent_wf.id)

    # Verify child workflow has NO parent_id set
    assert child_wf.parent_id is None
    assert child_wf.status == WorkflowStatus.SUCCEEDED
    assert child_wf.result == "child_result"
