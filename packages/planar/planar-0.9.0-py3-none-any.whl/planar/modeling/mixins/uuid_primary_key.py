from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UUIDPrimaryKeyMixin(SQLModel, table=False):
    """
    Mixin that provides a UUID primary key field.

    This standardizes primary key handling across all models that need
    a UUID-based primary key.

    Attributes:
        id: UUID primary key field with automatic generation
    """

    __abstract__ = True

    id: UUID = Field(default_factory=uuid4, primary_key=True)
