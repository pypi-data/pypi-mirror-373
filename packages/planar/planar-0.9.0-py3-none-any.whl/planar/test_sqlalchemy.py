from uuid import uuid4

import pytest
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import col, insert, select

from planar.db import PlanarSession, new_session
from planar.modeling.orm.planar_base_entity import PlanarBaseEntity


class SomeModel(PlanarBaseEntity, table=True):
    name: str
    value: int = 0


async def test_run_transaction_success(tmp_db_engine):
    uuid = uuid4()
    uuid2 = uuid4()

    async def transaction_func(session: PlanarSession):
        await session.exec(
            insert(SomeModel).values(id=uuid, name="test_item", value=42)  # type: ignore
        )
        await session.exec(
            insert(SomeModel).values(id=uuid2, name="test_item2", value=42)  # type: ignore
        )

    async with new_session(tmp_db_engine) as session:
        session.max_conflict_retries = 3
        await session.run_transaction(transaction_func, session)

    async with new_session(tmp_db_engine) as session:
        items = (
            await session.exec(select(SomeModel).order_by(col(SomeModel.name)))
        ).all()
        assert items == [
            SomeModel(id=uuid, name="test_item", value=42),
            SomeModel(id=uuid2, name="test_item2", value=42),
        ]


async def test_run_transaction_failure(tmp_db_engine):
    async def transaction_func(session: PlanarSession):
        await session.exec(insert(SomeModel).values(name="test_item", value=42))  # type: ignore
        raise ValueError("Test error")
        await session.exec(insert(SomeModel).values(name="test_item2", value=42))  # type: ignore

    async with new_session(tmp_db_engine) as session:
        with pytest.raises(ValueError, match="Test error"):
            session.max_conflict_retries = 3
            await session.run_transaction(transaction_func, session)

    async with new_session(tmp_db_engine) as session:
        items = (await session.exec(select(SomeModel))).all()
        assert items == []


async def test_run_transaction_concurrent_retry_success(tmp_db_engine):
    attempts = 0
    uuid = uuid4()
    uuid2 = uuid4()

    async def transaction_func(session: PlanarSession):
        nonlocal attempts
        await session.exec(
            insert(SomeModel).values(id=uuid, name="test_item", value=42)  # type: ignore
        )
        if attempts == 0:
            attempts += 1
            raise DBAPIError(
                "Test error", None, Exception("could not serialize access")
            )
        await session.exec(
            insert(SomeModel).values(id=uuid2, name="test_item2", value=42)  # type: ignore
        )

    async with new_session(tmp_db_engine) as session:
        session.max_conflict_retries = 1
        await session.run_transaction(transaction_func, session)

    async with new_session(tmp_db_engine) as session:
        items = (
            await session.exec(select(SomeModel).order_by(col(SomeModel.name)))
        ).all()
        assert items == [
            SomeModel(id=uuid, name="test_item", value=42),
            SomeModel(id=uuid2, name="test_item2", value=42),
        ]


async def test_run_transaction_concurrent_retry_failure(tmp_db_engine):
    attempts = 0

    async def transaction_func(session: PlanarSession):
        nonlocal attempts
        await session.exec(insert(SomeModel).values(name="test_item", value=42))  # type: ignore
        if attempts < 2:
            attempts += 1
            raise DBAPIError(
                "Test error", None, Exception("could not serialize access")
            )
        await session.exec(insert(SomeModel).values(name="test_item2", value=42))  # type: ignore

    async with new_session(tmp_db_engine) as session:
        with pytest.raises(DBAPIError, match="Test error"):
            session.max_conflict_retries = 1
            await session.run_transaction(transaction_func, session)

    async with new_session(tmp_db_engine) as session:
        items = (await session.exec(select(SomeModel))).all()
        assert items == []


async def test_serializable_transaction_failure_1(tmp_db_engine: AsyncEngine):
    if tmp_db_engine.dialect.name != "postgresql":
        return pytest.skip("Test requires PostgreSQL database")

    async with new_session(tmp_db_engine) as setup_session:
        # Setup: Insert initial data
        async with setup_session.begin():
            setup_session.add(SomeModel(id=uuid4(), name="initial", value=10))

    # Create two sessions
    async with (
        new_session(tmp_db_engine) as session1,
        new_session(tmp_db_engine) as session2,
    ):
        # Begin transactions in both sessions
        await session1.begin()
        await session2.begin()

        # Set serializable isolation level
        await session1.set_serializable_isolation()
        await session2.set_serializable_isolation()

        # Session 1: Read data
        item1 = (
            await session1.exec(select(SomeModel).where(SomeModel.name == "initial"))
        ).one()
        assert item1.value == 10

        # Session 2: Read the same data
        item2 = (
            await session2.exec(select(SomeModel).where(SomeModel.name == "initial"))
        ).one()
        assert item2.value == 10

        # Both sessions update the same row
        item1.value += 5
        item2.value += 3

        # Session 1: Commit should succeed
        await session1.commit()

        # Session 2: Commit should fail with serialization error
        with pytest.raises(DBAPIError, match="could not serialize access"):
            await session2.commit()
