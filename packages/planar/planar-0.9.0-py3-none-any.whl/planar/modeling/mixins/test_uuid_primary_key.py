from uuid import UUID

from sqlmodel import Field

from planar.db import PlanarSession
from planar.modeling.mixins.uuid_primary_key import UUIDPrimaryKeyMixin
from planar.modeling.orm.planar_base_entity import PlanarBaseEntity


class UUIDModelTest(PlanarBaseEntity, UUIDPrimaryKeyMixin, table=True):
    """Test model using UUIDPrimaryKeyMixin."""

    name: str = Field()


def test_uuid_primary_key_mixin_creates_uuid_id():
    """Test that UUIDPrimaryKeyMixin provides a UUID id field."""
    model = UUIDModelTest(name="test")

    assert hasattr(model, "id")
    assert isinstance(model.id, UUID)
    assert model.id is not None


def test_uuid_primary_key_mixin_allows_custom_id():
    """Test that a custom UUID can be provided."""
    custom_uuid = UUID("12345678-1234-5678-1234-123456789abc")
    model = UUIDModelTest(id=custom_uuid, name="test")

    assert model.id == custom_uuid


async def test_uuid_primary_key_mixin_is_primary_key(session: PlanarSession):
    """Test that the id field works as a primary key."""
    model1 = UUIDModelTest(name="test1")
    model2 = UUIDModelTest(name="test2")

    session.add(model1)
    session.add(model2)
    await session.commit()

    # Both should have different IDs
    assert model1.id != model2.id

    # Both should be retrievable by their IDs
    retrieved1 = await session.get(UUIDModelTest, model1.id)
    retrieved2 = await session.get(UUIDModelTest, model2.id)

    assert retrieved1 is not None
    assert retrieved1.name == "test1"
    assert retrieved2 is not None
    assert retrieved2.name == "test2"
