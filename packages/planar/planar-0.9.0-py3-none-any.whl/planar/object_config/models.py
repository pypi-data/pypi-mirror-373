from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import VARCHAR, UniqueConstraint
from sqlalchemy.sql.type_api import TypeDecorator
from sqlmodel import Column
from sqlmodel import Field as SQLField

from planar.db import PlanarInternalBase
from planar.modeling.mixins.timestamp import timestamp_column

T = TypeVar("T", bound="BaseModel")
V = TypeVar("V")


class ConfigurableObjectType(str, Enum):
    RULE = "rule"
    AGENT = "agent"


class JSONEncodedDict(TypeDecorator):
    """Create a SQLAlchemy type that converts BaseModel to JSON string on write and to dict on read."""

    impl = VARCHAR
    cache_ok = True  # Required for SQLAlchemy caching mechanism

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        if isinstance(value, BaseModel):
            return value.model_dump_json(by_alias=True)

        raise ValueError(f"Invalid type: {type(value)}")

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return json.loads(value)


class DiffErrorCode(Enum):
    """Error codes for dictionary comparison diagnostics."""

    MISSING_FIELD = "MISSING_FIELD"
    VALUE_MISMATCH = "VALUE_MISMATCH"
    EXTRA_FIELD = "EXTRA_FIELD"
    CONFIG_MODEL_CHANGED = "CONFIG_MODEL_CHANGED"


class ConfigDiagnosticIssue(BaseModel):
    """Represents a single diagnostic issue found during dictionary comparison."""

    error_code: DiffErrorCode
    field_path: str
    message: str
    reference_value: Any | None = None
    current_value: Any | None = None
    for_object: str


class ConfigDiagnostics(BaseModel, Generic[T]):
    is_valid: bool
    suggested_fix: T | None = None
    issues: list[ConfigDiagnosticIssue]


class ObjectConfigurationBase(BaseModel, Generic[T]):
    """Base Pydantic model for object configurations without SQLModel dependencies.

    This class mirrors the fields in ObjectConfiguration but can be used for
    serialization in FastAPI routes and other places where SQLModel references
    should be avoided.
    """

    id: UUID
    object_name: str
    object_type: ConfigurableObjectType
    created_at: datetime
    version: int
    data: T
    active: bool


class ObjectConfiguration(PlanarInternalBase, Generic[T], table=True):
    __table_args__ = (
        UniqueConstraint(
            "object_name",
            "object_type",
            "version",
            name="uq_object_config_name_type_version",
        ),
    )

    __tablename__ = "object_configuration"  # type: ignore

    id: UUID = SQLField(default_factory=uuid4, primary_key=True)

    object_name: str = SQLField(index=True)
    object_type: ConfigurableObjectType = SQLField(index=True)
    created_at: datetime = timestamp_column()

    version: int = SQLField(default=1)

    data: T = SQLField(sa_column=Column(JSONEncodedDict))

    active: bool = SQLField(default=False)
