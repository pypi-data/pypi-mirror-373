from datetime import datetime
from typing import Any, Callable

from sqlmodel import Field, SQLModel

from planar.utils import utc_now


def timestamp_column(
    index: bool = False,
    nullable: bool = False,
    onupdate: Callable[[], datetime] | bool | None = None,
    default: Callable[[], datetime] | None = utc_now,
):
    if onupdate is True:
        onupdate = utc_now
    return Field(
        default_factory=default,
        nullable=nullable,
        index=index,
        sa_column_kwargs={"onupdate": onupdate},
    )


class TimestampMixin(SQLModel, table=False):
    """
    Mixin that adds created_at and updated_at fields to a model.

    This standardizes timestamp handling across all internal models.

    Attributes:
        created_at: Timestamp when the record was created
        updated_at: Timestamp that updates whenever the record is modified
    """

    __abstract__ = True

    created_at: datetime = timestamp_column()
    updated_at: datetime = timestamp_column(onupdate=utc_now)

    def __init__(self, **kwargs: Any):
        """
        Initializes the TimestampMixin.
        Ensures that `updated_at` is the same as `created_at` if `updated_at`
        is not explicitly provided during instantiation.
        """
        super().__init__(**kwargs)
        # If 'updated_at' was not passed during construction,
        # set it to the value of 'created_at'.
        # 'created_at' itself would have been set by super().__init__()
        # either from kwargs or its default_factory.
        if "updated_at" not in kwargs and self.created_at is not None:
            self.updated_at = self.created_at
