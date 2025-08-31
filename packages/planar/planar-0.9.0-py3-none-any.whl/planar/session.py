from contextlib import asynccontextmanager
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncEngine

from planar.config import PlanarConfig
from planar.db import PlanarSession

session_var: ContextVar[PlanarSession] = ContextVar("session")
engine_var: ContextVar[AsyncEngine] = ContextVar("engine")
config_var: ContextVar[PlanarConfig] = ContextVar("config")


def get_engine():
    return engine_var.get()


def get_session():
    return session_var.get()


def get_config():
    return config_var.get()


@asynccontextmanager
async def session_context(engine: AsyncEngine):
    """Context manager for setting up and tearing down SQLAlchemy session context"""
    # Set the engine in the context
    engine_tok = engine_var.set(engine)

    async with PlanarSession(engine) as session:
        session_tok = session_var.set(session)
        try:
            yield session
        finally:
            session_var.reset(session_tok)

    # Reset engine context
    engine_var.reset(engine_tok)
