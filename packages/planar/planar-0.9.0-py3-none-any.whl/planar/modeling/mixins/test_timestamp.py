import asyncio
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import select

from planar.db import new_session
from planar.modeling.mixins import TimestampMixin
from planar.modeling.orm.planar_base_entity import PlanarBaseEntity
from planar.utils import utc_now


class TimestampTestModel(TimestampMixin, PlanarBaseEntity, table=True):
    """Test model that uses the TimestampMixin."""

    name: str
    value: int = 0


async def test_timestamp_fields_set_on_creation(tmp_db_engine: AsyncEngine):
    """Test that created_at and updated_at are set when a model is created."""
    # Record time before the operation
    before_creation = utc_now()

    # Create and insert model
    model_id = None
    async with new_session(tmp_db_engine) as session:
        model = TimestampTestModel(name="test_item", value=42)
        session.add(model)
        await session.commit()
        model_id = model.id

    # Record time after the operation
    after_creation = utc_now()

    # Fetch model to verify timestamps
    async with new_session(tmp_db_engine) as session:
        created_model = (
            await session.exec(
                select(TimestampTestModel).where(TimestampTestModel.id == model_id)
            )
        ).one()

    # Verify created_at is set and within the expected time range
    # and that it equals updated_at
    assert created_model.created_at is not None
    assert before_creation <= created_model.created_at <= after_creation
    assert created_model.created_at == created_model.updated_at


async def test_updated_at_reflects_changes(tmp_db_engine: AsyncEngine):
    """Test that updated_at is updated when a model is modified."""
    # Create and insert model
    model_id = None
    async with new_session(tmp_db_engine) as session:
        model = TimestampTestModel(name="test_item", value=42)
        session.add(model)
        await session.commit()
        model_id = model.id

        # Get initial created_at and updated_at values
        initial_model = (
            await session.exec(
                select(TimestampTestModel).where(TimestampTestModel.id == model_id)
            )
        ).one()
        await session.commit()
        initial_created_at = initial_model.created_at
        initial_updated_at = initial_model.updated_at

    # Wait a moment to ensure timestamp will be different
    await asyncio.sleep(0.01)

    # Record time before update
    before_update = utc_now()

    # Update the model
    async with new_session(tmp_db_engine) as session:
        model_to_update = (
            await session.exec(
                select(TimestampTestModel).where(TimestampTestModel.id == model_id)
            )
        ).one()
        model_to_update.value = 99
        await session.commit()

    # Record time after update
    after_update = utc_now()

    # Verify the timestamps
    async with new_session(tmp_db_engine) as session:
        updated_model = (
            await session.exec(
                select(TimestampTestModel).where(TimestampTestModel.id == model_id)
            )
        ).one()
        await session.commit()

        # created_at should not change
        assert updated_model.created_at == initial_created_at

        # updated_at should be newer than before
        assert updated_model.updated_at is not None
        assert initial_updated_at is not None
        assert updated_model.updated_at > initial_updated_at
        assert before_update <= updated_model.updated_at <= after_update


async def test_timestamp_init_with_explicit_values():
    """Test initializing a model with explicit timestamp values."""
    # Create a specific timestamp
    now = utc_now()
    past = now - timedelta(days=1)

    # Initialize model with explicit timestamps
    model = TimestampTestModel(
        name="test_explicit_timestamps",
        value=200,
        created_at=past,
        updated_at=now,
    )

    # Verify timestamps match what we provided
    assert model.created_at == past
    assert model.updated_at == now

    # Initialize model with only created_at
    model2 = TimestampTestModel(
        name="test_partial_timestamps", value=300, created_at=past
    )

    # Verify updated_at equals created_at when only created_at is provided
    assert model2.created_at == past
    assert model2.updated_at == past
