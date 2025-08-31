from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, engine_from_config, pool

from planar.db import PLANAR_FRAMEWORK_METADATA, PLANAR_SCHEMA

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = PLANAR_FRAMEWORK_METADATA

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    raise NotImplementedError(
        "Offline mode is not supported for Planar system migrations."
    )


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Check if we're being called programmatically (runtime) or from command line (development)
    connectable = config.attributes.get("connection", None)

    if isinstance(connectable, Connection):
        # Runtime mode: use the connection passed by DatabaseManager
        is_sqlite = connectable.dialect.name == "sqlite"

        context.configure(
            connection=connectable,
            target_metadata=target_metadata,
            # For SQLite, don't use schema since it's not supported
            version_table_schema=None if is_sqlite else PLANAR_SCHEMA,
            include_schemas=not is_sqlite,
            compare_type=True,
            # SQLite doesn't support alter table, so we need to use render_as_batch
            # to create the tables in a single transaction. For other databases,
            # the batch op is no-op.
            # https://alembic.sqlalchemy.org/en/latest/batch.html#running-batch-migrations-for-sqlite-and-other-databases
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()
    else:
        # Development mode: create engine from alembic.ini
        # Used for alembic to generate migrations
        # Import models to ensure they're registered with PLANAR_FRAMEWORK_METADATA
        try:
            from planar.files.models import PlanarFileMetadata  # noqa: F401, PLC0415
            from planar.human.models import HumanTask  # noqa: F401, PLC0415
            from planar.object_config.models import (  # noqa: F401, PLC0415
                ObjectConfiguration,
            )
            from planar.workflows.models import (  # noqa: PLC0415
                LockedResource,  # noqa: F401
                Workflow,  # noqa: F401
                WorkflowEvent,  # noqa: F401
                WorkflowStep,  # noqa: F401
            )
        except ImportError as e:
            raise RuntimeError(
                f"Failed to import system models for migration generation: {e}"
            )

        config_dict = config.get_section(config.config_ini_section, {})
        url = config_dict["sqlalchemy.url"]
        is_sqlite = url.startswith("sqlite://")
        translate_map = {"planar": None} if is_sqlite else {}
        connectable = engine_from_config(
            config_dict,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            execution_options={
                # SQLite doesn't support schemas, so we need to translate the planar schema
                # name to None in order to ignore it.
                "schema_translate_map": translate_map,
            },
        )

        with connectable.connect() as connection:
            is_sqlite = connection.dialect.name == "sqlite"
            if is_sqlite:
                connection.dialect.default_schema_name = "planar"

            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                # For SQLite, don't use schema since it's not supported
                version_table_schema=None if is_sqlite else PLANAR_SCHEMA,
                include_schemas=not is_sqlite,
                compare_type=True,
                # SQLite doesn't support alter table, so we need to use render_as_batch
                # to create the tables in a single transaction. For other databases,
                # the batch op is no-op.
                # https://alembic.sqlalchemy.org/en/latest/batch.html#running-batch-migrations-for-sqlite-and-other-databases
                render_as_batch=True,
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
