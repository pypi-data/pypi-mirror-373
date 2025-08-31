import asyncio
import re
from contextlib import asynccontextmanager
from pathlib import Path
from sqlite3 import LEGACY_TRANSACTION_CONTROL
from typing import Any, Callable, Coroutine, cast

from alembic import command
from alembic.config import Config as AlembicConfig
from pydantic import ConfigDict
from sqlalchemy import Connection, MetaData, event, make_url, text
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql.expression import ClauseElement, Executable
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

import planar
from planar.logging import get_logger
from planar.modeling.orm.planar_base_entity import PLANAR_APPLICATION_METADATA
from planar.utils import P, R, T, U, exponential_backoff_with_jitter


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


PLANAR_SCHEMA = "planar"
PLANAR_FRAMEWORK_METADATA = MetaData(schema=PLANAR_SCHEMA)
logger = get_logger(__name__)


class explain(Executable, ClauseElement):
    inherit_cache = False

    def __init__(self, stmt):
        self.statement = stmt
        self._inline = False


@compiles(explain, "postgresql")
def pg_explain(element, compiler, **kw):
    text = "EXPLAIN ANALYZE "
    text += compiler.process(element.statement, **kw)
    return text


class PlanarInternalBase(SQLModel, table=False):
    """
    Base model with common fields for all database tables.
    Not a table itself - meant to be inherited by concrete model classes.

    Usage conventions:
    - Primary keys should be "id" and be UUID with default_factory=uuid4 when possible
    - Use TimeStampMixin for auto-timestamp fields
    - Field names should use snake_case consistently
    - Table schema is set to 'planar' automatically
    - Foreign keys should specify the full schema.table_name
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore
        return camel_to_snake(cls.__name__)

    __abstract__ = True
    # __table_args__ = {"schema": PLANAR_SCHEMA}
    metadata = PLANAR_FRAMEWORK_METADATA
    model_config = ConfigDict(validate_assignment=True)  # type: ignore


class PlanarSession(AsyncSession):
    def __init__(self, engine: AsyncEngine | None = None):
        assert engine
        self.engine = engine
        self.dialect = engine.dialect
        self.max_conflict_retries: int = 10
        # dynamic import since planar.session depends on this
        from planar.session import config_var

        config = config_var.get(None)
        if config is not None and config.app.max_db_conflict_retries:
            self.max_conflict_retries = config.app.max_db_conflict_retries
        super().__init__(engine, expire_on_commit=False)

    async def set_serializable_isolation(self):
        if self.dialect.name == "postgresql":
            await self.exec(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))  # type: ignore[arg-type]

    @asynccontextmanager
    async def begin_read(self):
        """Context manager for read-only transactions.

        This is useful when reading from the database since it ensures that if
        a transaction has not started before the context, it will ensure no
        transactions are open after the context.
        """
        in_transaction = self.in_transaction()
        try:
            yield
            if not in_transaction:
                await self.commit()
        except Exception:
            if not in_transaction:
                await self.rollback()
            raise

    async def run_transaction(
        self,
        fn: Callable[P, Coroutine[T, U, R]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        max_conflict_retries = self.max_conflict_retries

        if self.in_transaction():
            await self.commit()

        remaining_retries = max_conflict_retries

        while True:
            try:
                async with self.begin():
                    await self.set_serializable_isolation()
                    return await fn(*args, **kwargs)
            except Exception as e:
                if remaining_retries == 0:
                    logger.exception("transaction failed after maximum retries")
                    raise

                if isinstance(e, DBAPIError) and "could not serialize access" in str(e):
                    delay = exponential_backoff_with_jitter(
                        max_conflict_retries - remaining_retries
                    )
                    await asyncio.sleep(delay)
                    remaining_retries -= 1
                    continue
                logger.exception(
                    "transaction failed due to unrecoverable error",
                    remaining_retries=remaining_retries,
                )
                raise

    async def explain(self, query: Executable, log_identifier: str) -> str:
        if self.dialect.name != "postgresql" or not logger.isDebugEnabled():
            return ""
        # Reusing the current session will mess things up
        # (implicit transaction starting, for example), so use
        # a separate session to run the explain command
        async with PlanarSession(self.engine) as session:
            result = await session.exec(cast(Any, explain(query)))
            query_plan = "\n".join([str(row[0]) for row in result])
            compiled_sql = str(query)
            logger.debug(
                f"query_plan:{log_identifier}",
                query_plan=query_plan,
                compiled_sql=compiled_sql,
            )
            return query_plan


def new_session(engine: AsyncEngine) -> PlanarSession:
    return PlanarSession(engine)


class DatabaseManager:
    def __init__(
        self,
        db_url: str | URL,
    ):
        self.db_url = make_url(db_url) if isinstance(db_url, str) else db_url
        self.engine: AsyncEngine | None = None

    def _create_sqlite_engine(self, url: URL) -> AsyncEngine:
        # in practice this high timeout is only use
        timeout = int(str(url.query.get("timeout", 60)))
        logger.info("Setting up SQLite engine with timeout", timeout=timeout)

        engine = create_async_engine(
            url,
            connect_args=dict(
                timeout=timeout,
                isolation_level=None,
                # If autocommit is not LEGACY_TRANSACTION_CONTROL, isolation_level
                # is ignored, so we set here explicitly to make the intention clear,
                # even though it is the default value.
                autocommit=LEGACY_TRANSACTION_CONTROL,
            ),
            # SQLite doesn't support schemas, so we need to translate the planar schema
            # name to None.
            execution_options={"schema_translate_map": {"planar": None}},
        )

        def do_begin(conn: Connection):
            conn.exec_driver_sql("BEGIN IMMEDIATE")

        event.listen(engine.sync_engine, "begin", do_begin)

        return engine

    def _create_postgresql_engine(self, url: URL) -> AsyncEngine:
        engine = create_async_engine(url)

        return engine

    def connect(self):
        """Creates and initializes the database engine."""
        if self.engine:
            logger.warning("database engine already initialized")
            return

        db_backend = self.db_url.get_backend_name()

        match db_backend:
            case "sqlite":
                logger.info(
                    "connecting to database", db_backend=db_backend, db_url=self.db_url
                )
                self.engine = self._create_sqlite_engine(self.db_url)
            case "postgresql":
                logger.info("connecting to database", db_backend=db_backend)
                self.engine = self._create_postgresql_engine(self.db_url)
            case _:
                raise NotImplementedError(
                    f'Unsupported database backend "{db_backend}"'
                )

    async def disconnect(self):
        """Disposes of the database engine."""
        if self.engine:
            logger.info("disconnecting database engine")
            await self.engine.dispose()
            self.engine = None
        else:
            logger.warning("attempted to disconnect an uninitialized engine")

    def get_engine(self) -> AsyncEngine:
        """Returns the initialized AsyncEngine."""
        if not self.engine:
            raise RuntimeError("Database engine not initialized. Call connect() first.")
        return self.engine

    def get_session(self) -> PlanarSession:
        """Returns a new PlanarSession."""
        if not self.engine:
            raise RuntimeError("Database engine not initialized. Call connect() first.")
        return PlanarSession(self.engine)

    async def _run_system_migrations(self):
        logger.info("running planar system migrations")

        module_path = Path(planar.__file__).parent
        script_location = str(module_path / "db" / "alembic")

        alembic_cfg = AlembicConfig()
        alembic_cfg.set_main_option("script_location", script_location)

        if not self.engine:
            raise RuntimeError("Database engine not initialized. Call connect() first.")
        try:
            async with self.engine.begin() as conn:
                # Pass the *synchronous* connection produced by `run_sync` to Alembic.

                def _upgrade(sync_conn):
                    """Run Alembic upgrade using the given synchronous connection."""

                    # Inject the sync SQLAlchemy Connection so that planar/db/alembic/env.py
                    # recognises we're running in programmatic (runtime) mode instead of
                    # development mode. This prevents it from trying to create a new engine
                    # via `engine_from_config`, which expects a URL in the Alembic config.
                    alembic_cfg.attributes["connection"] = sync_conn

                    # Execute migrations up to the latest revision.
                    command.upgrade(alembic_cfg, "head")

                # Execute the upgrade inside the green-thread aware sync context.
                await conn.run_sync(_upgrade)
            logger.info("planar system migrations completed successfully")
        except Exception:
            logger.exception("planar system migration failed")
            raise

    async def _setup_database(self):
        if not self.engine:
            raise RuntimeError("Database engine not initialized. Call connect() first.")

        async with self.engine.begin() as conn:
            if "sqlite" in self.db_url.drivername:
                await conn.execute(text("PRAGMA foreign_keys=ON"))
            else:
                # Ensure planar schema exists
                await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {PLANAR_SCHEMA}"))

    async def migrate(self, use_alembic: bool):
        """
        Runs database migrations.
        By default, uses SQLModel.metadata.create_all.
        Set use_alembic=True to use Alembic (requires Alembic setup).
        """
        if not self.engine:
            raise RuntimeError("Database engine not initialized. Call connect() first.")

        logger.info("starting database migration")
        if use_alembic:
            logger.info("using alembic for migrations")
            await self._setup_database()
            await self._run_system_migrations()
            # For now user migrations are not supported, so we fall back to SQLModel.metadata.create_all
            async with self.engine.begin() as conn:
                await conn.run_sync(PLANAR_APPLICATION_METADATA.create_all)

        else:
            async with self.engine.begin() as conn:
                await self._setup_database()
                await conn.run_sync(PLANAR_FRAMEWORK_METADATA.create_all)
                await conn.run_sync(PLANAR_APPLICATION_METADATA.create_all)
