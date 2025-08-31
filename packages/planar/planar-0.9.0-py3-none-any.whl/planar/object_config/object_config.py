"""
This module contains the ObjectConfiguration class, which is used to store and manage
the configuration of objects in the database.

"Object" is used to refer to agents, entities, rules, etc

See ConfigurableObjectType for the different types of objects that can be configured.

When a config is written for a particular object (uniquely identified by object_name and object_type),
this config will be used during workflow execution to drive the behaviour of that boject.

If no persisted config exists, then the workflow will fallback to the in-memory implementation
of that object as specified by the user in the planar sdk.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Generic, Sequence, Type, TypeVar, cast
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import col, select, update

from planar.logging import get_logger
from planar.object_config.models import (
    ConfigDiagnostics,
    ConfigurableObjectType,
    ObjectConfiguration,
    ObjectConfigurationBase,
)
from planar.session import get_session

# Special case: UUID with all zeros means revert to in-memory default (set all configs inactive)
DEFAULT_UUID = UUID("00000000-0000-0000-0000-000000000000")

logger = get_logger(__name__)


T = TypeVar("T", bound="BaseModel")
V = TypeVar("V")


def default_validate_config(name: str, config: BaseModel) -> ConfigDiagnostics:
    return ConfigDiagnostics(is_valid=True, issues=[])


class ObjectConfigurationIO(Generic[T, V]):
    """Abstract base class for reading and writing different object configurations.

    This class provides a framework for creating concrete implementations
    that know how to deserialize configuration data using specific Pydantic models.
    """

    def __init__(
        self,
        model_class: Type[T],
        object_type: ConfigurableObjectType,
        validate_config: Callable[
            [str, T], ConfigDiagnostics
        ] = default_validate_config,
    ):
        """Initialize the reader with a Pydantic model class.

        Args:
            model_class: The Pydantic model class used for deserialization
            object_type: The type of object this configuration is for
        """
        self.model_class = model_class
        self.object_type = object_type
        self.validate_config = validate_config

    async def _read_configs(
        self, object_name: str, limit: int | None = 20
    ) -> Sequence[ObjectConfiguration[T]]:
        """Read all configurations from the database for a object with schema validation warnings.

        Intended for internal use only since the public API requires a default (in-memory) configuration

        Args:
            object_name: The name of the object to read configurations for
            limit: The maximum number of configurations to read

        Returns:
            A ConfigurationResult containing all configurations ordered by version (descending) and any schema warnings
        """
        session = get_session()

        async with session.begin_read():
            # Query for all versions of the object configuration, ordered by version descending
            statement = (
                select(ObjectConfiguration)
                .where(ObjectConfiguration.object_name == object_name)
                .where(ObjectConfiguration.object_type == self.object_type)
                .order_by(col(ObjectConfiguration.version).desc())
                .limit(limit)
            )

            cfgs = (await session.exec(statement)).all()

            for cfg in cfgs:
                cfg.data = self.model_class.model_validate(cfg.data)

            logger.debug(
                f"Read {len(cfgs)} configurations for object '{object_name}' of type '{self.object_type}'."
            )

            return cfgs

    async def read_configs_with_default(
        self, object_name: str, default_value: T
    ) -> list[ObjectConfigurationBase[T]]:
        """Read all configurations for a object with a default configuration.

        Args:
            object_name: The name of the object for which to read configurations
            default_value: The default configuration to use if no configurations are found

        Returns:
            A ConfigurationResult containing all configurations ordered by version (descending)
        """
        logger.debug(
            "reading configs with default for object",
            object_name=object_name,
            object_type=self.object_type,
        )

        config_list = await self._read_configs(object_name)

        default_config_active = all(not config.active for config in config_list)
        logger.debug(
            "default config active status",
            object_name=object_name,
            is_active=default_config_active,
        )

        default_config = ObjectConfigurationBase[T].model_validate(
            {
                "id": DEFAULT_UUID,
                "object_type": self.object_type,
                "object_name": object_name,
                "version": 0,
                "active": default_config_active,
                "created_at": datetime.now(timezone.utc),
                "data": default_value,
            }
        )

        validated_configs: list[ObjectConfigurationBase[T]] = []

        for config in config_list:
            validated_configs.append(
                ObjectConfigurationBase[T].model_validate(
                    {
                        "id": config.id,
                        "object_name": config.object_name,
                        "object_type": config.object_type,
                        "created_at": config.created_at,
                        "version": config.version,
                        "data": self.model_class.model_validate(config.data),
                        "active": config.active,
                    }
                )
            )

        validated_configs.append(default_config)

        return validated_configs

    async def write_config(self, object_name: str, config: T) -> ObjectConfiguration:
        """Write the configuration to a ObjectConfiguration.

        Args:
            object_name: The name of the object to write configuration for
            config: The Pydantic model instance to write

        Returns:
            A ConfigurationResult containing the written configuration
        """
        logger.debug(
            "writing config for object",
            object_name=object_name,
            object_type=self.object_type,
        )
        session = get_session()

        async with session.begin():
            existing_configs = await self._read_configs(object_name, limit=1)

            if not existing_configs:
                version = 1
            else:
                # Get the highest version number and increment it
                version = existing_configs[0].version + 1

            logger.debug(
                "new configuration version",
                object_name=object_name,
                version=version,
            )

            result = self.validate_config(object_name, config)

            if not result.is_valid:
                raise ConfigValidationError(object_name, self.object_type, result)

            # The JSON codec will handle converting the BaseModel to JSON string
            object_config = ObjectConfiguration(
                object_name=object_name,
                object_type=self.object_type,
                data=config,  # type: ignore[arg-type]
                version=version,
            )

            session.add(object_config)
            logger.info(
                "configuration written to database",
                version=version,
                object_name=object_name,
                config_id=object_config.id,
            )
            return object_config

    async def promote_config(
        self, config_id: UUID, object_name: str | None = None
    ) -> None:
        """Promote a specific configuration to be the active one.

        Args:
            config_id: The UUID of the configuration to promote.
                      Use UUID('00000000-0000-0000-0000-000000000000') to revert to default implementation.
            object_name: Required when using the default UUID to specify which object to revert

        Returns:
            A ConfigurationResult containing all configurations for the object

        Raises:
            ConfigNotFoundError: If the configuration is not found
        """
        logger.debug(
            "promoting config",
            config_id=config_id,
            object_name=object_name,
            object_type=self.object_type,
        )
        session = get_session()
        async with session.begin():
            # Edge case: revert to default in-memory configuration by setting all configs to inactive
            if config_id == DEFAULT_UUID:
                if not object_name:
                    raise ValueError(
                        "object_name is required when reverting to default configuration"
                    )
                logger.info(
                    "reverting object to default configuration",
                    object_name=object_name,
                    object_type=self.object_type,
                )
                update_query = (
                    update(ObjectConfiguration)
                    .where(col(ObjectConfiguration.object_name) == object_name)
                    .where(col(ObjectConfiguration.object_type) == self.object_type)
                    .values(active=False)
                )

                await session.exec(cast(Any, update_query))
                return

            # First, find the configuration to promote
            target_config = (
                await session.exec(
                    select(ObjectConfiguration)
                    .where(ObjectConfiguration.id == config_id)
                    .where(ObjectConfiguration.object_type == self.object_type)
                )
            ).first()

            if not target_config:
                logger.warning(
                    "config id not found during promotion",
                    config_id=config_id,
                    object_type=self.object_type,
                )
                raise ConfigNotFoundError(config_id, self.object_type)

            logger.info(
                "found target config to promote",
                version=target_config.version,
                object_name=target_config.object_name,
            )

            config_data = self.model_class.model_validate(target_config.data)
            result = self.validate_config(target_config.object_name, config_data)

            if not result.is_valid:
                raise ConfigValidationError(
                    target_config.object_name, self.object_type, result
                )

            # Set all configurations for this object to inactive
            all_configs = (
                await session.exec(
                    select(ObjectConfiguration)
                    .where(ObjectConfiguration.object_name == target_config.object_name)
                    .where(ObjectConfiguration.object_type == self.object_type)
                )
            ).all()

            for config_item in all_configs:
                config_item.active = False

            # Set the target configuration to active
            target_config.active = True
            logger.info(
                "config is now active",
                version=target_config.version,
                object_name=target_config.object_name,
            )

            # Add all modified configs to the session
            for config_item in (
                all_configs
            ):  # Ensure target_config is also added if it was part of all_configs
                session.add(config_item)

            # Explicitly add target_config if it wasn't part of all_configs (should not happen with current logic)
            # or if it was modified and needs to be re-added.
            if (
                target_config not in all_configs
            ):  # Should not be true if logic is correct
                session.add(target_config)

            return


class ConfigValidationErrorResponse(BaseModel):
    """Response model for configuration validation errors."""

    error: str
    object_name: str
    object_type: str
    diagnostics: ConfigDiagnostics


class ConfigValidationError(Exception):
    """Raised when object configuration validation fails."""

    def __init__(
        self,
        object_name: str,
        object_type: ConfigurableObjectType,
        diagnostics: ConfigDiagnostics,
    ):
        self.object_name = object_name
        self.object_type = object_type
        self.diagnostics = diagnostics

        super().__init__(f"Validation failed for {object_type} '{object_name}'")

    def to_api_response(self) -> ConfigValidationErrorResponse:
        """Convert ValidationError to a JSON-serializable dictionary for API responses."""
        return ConfigValidationErrorResponse(
            error="ValidationError",
            object_name=self.object_name,
            object_type=self.object_type.value,
            diagnostics=self.diagnostics,
        )


class ConfigNotFoundError(Exception):
    """Raised when a configuration with the specified ID is not found."""

    def __init__(self, invalid_id, object_type):
        self.invalid_id = invalid_id
        self.object_type = object_type
        super().__init__(
            f"Configuration with ID {invalid_id} and object_type {object_type} not found"
        )
