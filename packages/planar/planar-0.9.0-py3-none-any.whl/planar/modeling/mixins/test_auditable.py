import pytest
from sqlmodel import Field, SQLModel

from planar.db import PlanarSession, new_session
from planar.modeling.mixins.auditable import AuditableMixin
from planar.security.auth_context import (
    Principal,
    as_principal,
    get_current_principal,
)

TEST_PRINCIPAL = Principal(
    sub="test_user",
    iss="test",
    exp=1000,
    iat=1000,
    sid="test",
    jti="test",
    org_id="test",
    org_name="test",
    user_first_name="test",
    user_last_name="test",
    user_email="test@test.com",
    role="test",
    permissions=["test"],
    extra_claims={"test": "test"},
)


class TestAuditableModel(AuditableMixin, SQLModel, table=True):
    """Test model using AuditableMixin."""

    __test__ = False

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field()


@pytest.fixture
async def session(mem_db_engine):
    """Create a database session."""

    async with new_session(mem_db_engine) as session:
        await (await session.connection()).run_sync(SQLModel.metadata.create_all)
        yield session


def test_auditable_mixin_has_audit_fields():
    """Test that AuditableMixin provides default audit fields."""
    model = TestAuditableModel(name="test")

    assert hasattr(model, "created_by")
    assert hasattr(model, "updated_by")
    assert model.created_by == "system"
    assert model.updated_by == "system"


async def test_auditable_mixin_sets_values_on_insert(session: PlanarSession):
    """Test that audit fields are set from SecurityContext on insert."""
    with as_principal(TEST_PRINCIPAL):
        model = TestAuditableModel(name="test_insert")
        session.add(model)
        await session.commit()

        # Refresh to get the updated values
        await session.refresh(model)

        assert model.created_by == "test@test.com"
        assert model.updated_by == "test@test.com"


async def test_auditable_mixin_sets_updated_by_on_update(session: PlanarSession):
    """Test that updated_by is set from SecurityContext on update."""
    # First insert with initial user
    with as_principal(TEST_PRINCIPAL):
        model = TestAuditableModel(name="test_update")
        session.add(model)
        await session.commit()
        await session.refresh(model)

        assert model.created_by == "test@test.com"
        assert model.updated_by == "test@test.com"

    # Now update with different user
    updating_principal = TEST_PRINCIPAL.model_copy(
        update={"user_email": "updating@test.com"}
    )
    with as_principal(updating_principal):
        assert get_current_principal() == updating_principal
        model.name = "updated_name"
        session.add(model)
        await session.commit()
        await session.refresh(model)

        # created_by should remain the same, updated_by should change
        assert model.created_by == "test@test.com"
        assert model.updated_by == "updating@test.com"
