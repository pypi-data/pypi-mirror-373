from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, SQLModel

from planar.logging import get_logger
from planar.security.auth_context import get_current_principal

logger = get_logger("orm.AuditableMixin")

SYSTEM_USER = "system"


class AuditableMixin(SQLModel, table=False):
    """
    Mixin that provides audit trail fields for tracking who created and updated records.

    This standardizes audit trail handling across all models that need to track
    user actions.

    Attributes:
        created_by: User who created the record
        updated_by: User who last updated the record
    """

    __abstract__ = True

    created_by: str = Field(default=SYSTEM_USER)
    updated_by: str = Field(default=SYSTEM_USER)


@event.listens_for(AuditableMixin, "before_insert", propagate=True)
def set_auditable_values(
    mapper: Mapper, connection: Connection, target: AuditableMixin
) -> None:
    """Set created_by, updated_by before insert."""
    principal = get_current_principal()
    email = principal.user_email if principal else None
    user_str: str = email or SYSTEM_USER
    target.created_by = user_str
    target.updated_by = user_str


@event.listens_for(AuditableMixin, "before_update", propagate=True)
def update_auditable_values(
    mapper: Mapper, connection: Connection, target: AuditableMixin
) -> None:
    """Set updated_by before update."""
    principal = get_current_principal()
    email = principal.user_email if principal else None
    user_str: str = email or SYSTEM_USER
    target.updated_by = user_str
