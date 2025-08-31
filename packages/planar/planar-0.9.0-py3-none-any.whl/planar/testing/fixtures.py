"""
Pytest fixtures for the Planar library.

This module provides pytest fixtures that can be used both internally by the planar library
and by external users who want to test their code that uses planar.

Usage in external projects:
- By default, these fixtures are auto-loaded when planar is installed
- To disable auto-loading: set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
- To manually enable: use `uv run pytest -p planar` or add to conftest.py:
  `pytest_plugins = ["planar.testing.fixtures"]`
  or add to pyproject.toml:
  `[project.entry-points.pytest11]
  planar = "planar.testing.fixtures"
  `

Available fixtures:
- storage: In-memory file storage for tests
- tmp_db_url: Parametrized database URL (SQLite/PostgreSQL)
- session: Database session
- client: Planar test client
- observer: Workflow observer for testing
- tracer: Tracer for workflow testing
"""

import asyncio
import os
import subprocess
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import pytest

from planar.config import load_config
from planar.db import DatabaseManager, new_session
from planar.files.storage.context import set_storage
from planar.logging import set_context_metadata
from planar.object_registry import ObjectRegistry
from planar.session import engine_var, session_var
from planar.testing.memory_storage import MemoryStorage
from planar.testing.planar_test_client import (
    planar_test_client,
)
from planar.testing.workflow_observer import WorkflowObserver
from planar.workflows.tracing import Tracer

_TEST_DATABASES = []
if os.getenv("PLANAR_TEST_SQLITE", "1") == "1":
    _TEST_DATABASES.append("sqlite")
if os.getenv("PLANAR_TEST_POSTGRESQL", "0") == "1":
    _TEST_DATABASES.append("postgresql")


def load_logging_config():
    logging_config = os.getenv("PLANAR_TEST_LOGGING_CONFIG", None)
    if logging_config is None:
        return None
    f = Path(logging_config)
    if not f.exists():
        print("Logging configuration file does not exist:", f)
        return None
    try:
        text = f.read_text()
        return load_config(text)
    except Exception as e:
        print("Failed to load logging configuration:", e)
        return None


@pytest.fixture(autouse=True, scope="session")
def configure_session_logging():
    test_config = load_logging_config()
    if test_config:
        if test_config.otel:
            test_config.otel.resource_attributes = {
                **(test_config.otel.resource_attributes or {}),
                "service.name": f"{time.strftime('%Y-%m-%d %H:%M:%S')}-planar-test-run",
            }
        test_config.configure_logging()


@pytest.fixture(autouse=True)
async def configure_test_logging(request):
    # get the current test name
    set_context_metadata("test.id", request.node.name)


@pytest.fixture(autouse=True)
def reset_object_registry():
    """
    Reset the ObjectRegistry singleton before each test to ensure clean state.
    """
    ObjectRegistry.get_instance().reset()
    yield  # Run the test


@pytest.fixture()
def tmp_db_path(tmp_path_factory):
    """
    Create a temporary SQLite database file and return its URL. The database
    file is created in a temporary directory managed by pytest.
    """
    tmp_dir = tmp_path_factory.mktemp("sqlite_db")
    db_file = tmp_dir / "test.db"
    return str(db_file)


@pytest.fixture()
async def storage():
    storage = MemoryStorage()
    set_storage(storage)
    yield storage


@pytest.fixture()
def tmp_sqlite_url(tmp_db_path: str):
    return f"sqlite+aiosqlite:///{tmp_db_path}"


@pytest.fixture(scope="session")
def tmp_postgresql_container():
    container_name = "planar-postgres-" + uuid.uuid4().hex

    # Start the postgres container.
    container_process = subprocess.Popen(
        [
            "docker",
            "run",
            "--rm",
            "--name",
            container_name,
            "-e",
            "POSTGRES_PASSWORD=123",
            "-p",
            "127.0.0.1:5432:5432",
            "docker.io/library/postgres",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait until Postgres is ready to accept connections.
    remaining_tries = 10
    while remaining_tries > 0:
        process = subprocess.run(
            [
                "docker",
                "exec",
                container_name,
                "psql",
                "-U",
                "postgres",
                "-c",
                "CREATE DATABASE dummy;",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if process.returncode != 0:
            remaining_tries -= 1
            if remaining_tries == 0:
                # Terminate container if it fails to start.
                container_process.terminate()
                container_process.wait()
                raise Exception("Failed to create database")
            time.sleep(10)
        else:
            break

    try:
        yield container_name
    finally:
        container_process.terminate()
        container_process.wait()


@pytest.fixture()
def tmp_postgresql_url(request):
    container_name = os.getenv("PLANAR_TEST_POSTGRESQL_CONTAINER", None)

    if container_name is None:
        # lazy load the session-scoped container fixture, which will
        # create a temporary docker container for the duration of the session
        container_name = request.getfixturevalue("tmp_postgresql_container")

    db_name = "test_" + uuid.uuid4().hex

    process = subprocess.run(
        [
            "docker",
            "exec",
            container_name,
            "psql",
            "-U",
            "postgres",
            "-c",
            f"CREATE DATABASE {db_name};",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if process.returncode != 0:
        raise Exception("Failed to create database")

    url = f"postgresql+asyncpg://postgres:123@127.0.0.1:5432/{db_name}"

    try:
        yield url
    finally:
        kill_all_sessions = f"""
            SELECT
                pg_terminate_backend(pid)
            FROM
                pg_stat_activity
            WHERE
                -- don't kill my own connection!
                pid <> pg_backend_pid()
                -- don't kill the connections to other databases
                AND datname = '{db_name}'
                ;
            """
        process = subprocess.run(
            [
                "docker",
                "exec",
                container_name,
                "psql",
                "-U",
                "postgres",
                "-c",
                kill_all_sessions,
                "-c",
                f"DROP DATABASE {db_name};",
            ],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        if process.returncode != 0:
            raise Exception("Failed to drop database")


@pytest.fixture(params=_TEST_DATABASES)
def tmp_db_url(request):
    fixture_name = f"tmp_{request.param}_url"
    return request.getfixturevalue(fixture_name)


@pytest.fixture()
async def tmp_db_engine(tmp_db_url: str):
    async with engine_context(tmp_db_url) as engine:
        yield engine


@pytest.fixture()
async def mem_db_engine(tmp_db_engine):
    # Memory databases don't work well with aiosqlite due to the "database
    # table is locked" error (which doesn't respect timeouts), so just use a
    # temporary db file for now until we figure out a fix.
    yield tmp_db_engine

    # name = uuid4()
    # async with engine_context(
    #     f"sqlite+aiosqlite:///file:{name}?mode=memory&cache=shared&uri=true"
    # ) as engine:
    #     yield engine


@pytest.fixture(name="session")
async def session_fixture(mem_db_engine):
    async with new_session(mem_db_engine) as session:
        tok = session_var.set(session)
        yield session
        session_var.reset(tok)


@pytest.fixture(name="observer")
def workflow_observer_fixture():
    yield WorkflowObserver()


@pytest.fixture(name="client")
async def planar_test_client_fixture(
    request,
    tmp_db_url: str,
    tracer: Tracer,
    observer: WorkflowObserver,
    storage: MemoryStorage,
):
    """
    Create a PlanarTestClient for testing.

    This fixture requires an 'app' fixture to be defined in your test file
    or conftest.py that returns a PlanarApp instance.

    Example:
        @pytest.fixture(name="app")
        def app_fixture():
            app = PlanarApp()
            app.register_workflow(my_workflow)
            return app
    """
    app = request.getfixturevalue("app")
    app.tracer = tracer
    app.storage = storage
    async with planar_test_client(app, tmp_db_url, observer) as client:
        yield client


@pytest.fixture(name="tracer")
async def tracer_fixture():
    yield None


@asynccontextmanager
async def engine_context(url: str):
    db_manager = DatabaseManager(url)
    db_manager.connect()
    await db_manager.migrate(use_alembic=True)
    engine = db_manager.get_engine()
    tok = engine_var.set(engine)
    yield engine
    engine_var.reset(tok)
