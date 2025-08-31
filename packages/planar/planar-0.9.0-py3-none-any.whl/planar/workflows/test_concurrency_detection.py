import asyncio
import multiprocessing
import multiprocessing.connection
from multiprocessing.connection import Connection
from uuid import UUID

from planar.db import DatabaseManager, new_session
from planar.session import engine_var, get_engine, session_var
from planar.workflows.decorators import step, workflow
from planar.workflows.exceptions import LockResourceFailed
from planar.workflows.execution import (
    _DEFAULT_LOCK_DURATION,
    execute,
)
from planar.workflows.lock import lock_workflow
from planar.workflows.models import Workflow, WorkflowStatus

# bidirectional communication between the test process and the worker processes.
conn: Connection


@step(max_retries=0)
async def dummy_step():
    conn.send("waiting")
    # Wait until "proceed" is received from the queue.
    if conn.recv() != "proceed":
        raise Exception('Expected "proceed"')
    return "success"


@workflow()
async def dummy_workflow():
    # Run the dummy step and return its result.
    result = await dummy_step()
    return result


# copy of the resume_workflow function which allows more fine grained control from
# the test process. This is fine because our goal is to test concurrency detection
# implemented by the execute function.
async def resume_with_semaphores(workflow_id: UUID):
    engine = get_engine()
    async with new_session(engine) as session:
        tok = session_var.set(session)
        try:
            async with session.begin():
                workflow = await session.get(Workflow, workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            conn.send("ready")
            # Wait until "start" is received on stdin.
            if conn.recv() != "start":
                raise Exception('Expected "start"')
            async with lock_workflow(
                workflow,
                _DEFAULT_LOCK_DURATION,
                retry_count=0,
            ):
                await execute(workflow)
            conn.send("completed")
        except LockResourceFailed:
            conn.send("conflict")
        finally:
            session_var.reset(tok)


# This worker function will be launched as a separate process.
# It takes the workflow id, db_url and a multiprocess Pipe.
def worker(wf_id: UUID, db_url: str, connection: Connection):
    global conn
    conn = connection
    # Create a new engine for this process.
    db_manager = DatabaseManager(db_url)
    db_manager.connect()
    engine = db_manager.get_engine()
    engine_var.set(engine)
    # Run the resume_with_semaphores coroutine.
    # We use asyncio.run so that the worker’s event loop is independent.
    asyncio.run(resume_with_semaphores(wf_id))


async def test_concurrent_workflow_execution(tmp_db_url, tmp_db_engine):
    async with new_session(tmp_db_engine) as session:
        session_var.set(session)
        wf: Workflow = await dummy_workflow.start()
        wf_id = wf.id

        # Launch two separate processes that attempt to resume the workflow concurrently.
        p1_parent, p1_worker = multiprocessing.Pipe(duplex=True)
        p2_parent, p2_worker = multiprocessing.Pipe(duplex=True)
        p1 = multiprocessing.Process(target=worker, args=(wf_id, tmp_db_url, p1_worker))
        p2 = multiprocessing.Process(target=worker, args=(wf_id, tmp_db_url, p2_worker))
        p1.start()
        p2.start()
        # wait for both workers to fetch the workflow from the database.
        assert p1_parent.recv() == "ready"
        assert p2_parent.recv() == "ready"
        # allow worker 1 to proceed.
        p1_parent.send("start")
        # wait for worker 1 to start the workflow and pause in the dummy step.
        assert p1_parent.recv() == "waiting"
        # allow worker 2 to proceed.
        p2_parent.send("start")
        # worker 2 should fail and will send a "conflict" message.
        assert p2_parent.recv() == "conflict"
        # allow worker 1 to proceed
        p1_parent.send("proceed")
        # worker 1 should complete the workflow and send a "completed" message.
        assert p1_parent.recv() == "completed"
        # cleanup workers
        p1.join()
        p2.join()

        await session.refresh(wf)
        assert wf, f"Workflow {wf_id} not found"
        # Assert that the workflow completed successfully.
        assert wf.status == WorkflowStatus.SUCCEEDED, (
            f"Unexpected workflow status: {wf.status}"
        )
        assert wf.result == "success", f"Unexpected workflow result: {wf.result}"
