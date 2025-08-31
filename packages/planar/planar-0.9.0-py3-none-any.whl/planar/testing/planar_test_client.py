import asyncio
from contextlib import asynccontextmanager

from httpx import ASGITransport, AsyncClient

from planar import PlanarApp
from planar.db import DatabaseManager
from planar.session import session_var
from planar.testing.workflow_observer import WorkflowObserver


class PlanarTestClient(AsyncClient):
    def __init__(self, app: PlanarApp):
        self.app = app
        super().__init__(
            base_url="http://testserver", transport=ASGITransport(app=app.fastapi)
        )


@asynccontextmanager
async def planar_test_client(
    app: PlanarApp, connection_string: str, observer: WorkflowObserver | None = None
):
    # Override the db manager with a new one that uses test database
    app.db_manager = DatabaseManager(connection_string)
    app.db_manager.connect()
    if observer:
        app.on_workflow_notification = observer.on_workflow_notification
        app.sse_proxy.enable_builtin_hub = False
        app.sse_proxy.hub_url = ""

    async with PlanarTestClient(app) as client:
        # run the app lifespan
        async with app._lifespan(app.fastapi):
            # Create a session and set it in the contextvar
            async with app.db_manager.get_session() as session:
                token = session_var.set(session)
                try:
                    yield client
                finally:
                    session_var.reset(token)
    await wait_all_event_loop_tasks()


async def wait_all_event_loop_tasks():
    # Workaround prevent the event loop from exiting before aiosqlite
    # has a chance to cleanup its background threads:
    # Keep yielding back to the event loop until the only task left is this one
    current_task = asyncio.current_task()
    while True:
        other_tasks = [task for task in asyncio.all_tasks() if task is not current_task]
        if not other_tasks:
            break
        try:
            await asyncio.gather(*other_tasks)
        except asyncio.CancelledError:
            pass
