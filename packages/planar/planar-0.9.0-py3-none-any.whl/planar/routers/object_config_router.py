"""
Router for object configuration operations.

This module contains endpoints for managing object configurations across
different object types (agents, rules, etc.).
"""

from typing import Generic, TypeVar, cast
from uuid import UUID

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from planar.ai.agent_utils import agent_configuration
from planar.logging import get_logger
from planar.object_config import (
    DEFAULT_UUID,
    ConfigNotFoundError,
    ConfigurableObjectType,
    ObjectConfigurationBase,
)
from planar.object_config.object_config import ConfigValidationError
from planar.object_registry import ObjectRegistry
from planar.rules.rule_configuration import rule_configuration

T = TypeVar("T", bound=BaseModel)

logger = get_logger(__name__)


class PromoteConfigRequest(BaseModel):
    """Request model for promoting a configuration."""

    object_type: ConfigurableObjectType
    config_id: UUID
    object_name: str


class ObjectConfigurationResponse(BaseModel, Generic[T]):
    """Response model for object configuration endpoints that includes schema warnings."""

    configs: list[T]


def create_object_config_router(object_registry: ObjectRegistry) -> APIRouter:
    """Create the object configuration router with all endpoints."""
    router = APIRouter(tags=["Object Configuration"])

    @router.post("/promote", response_model=ObjectConfigurationResponse)
    async def promote_config(request: PromoteConfigRequest = Body(...)):
        """Promote a specific configuration to be the active one.

        Use config_id '00000000-0000-0000-0000-000000000000' to revert to default implementation.
        Supports both rule and agent configurations.
        """
        # Handle special case for default UUID (all zeros)
        entity = None
        if request.object_type == ConfigurableObjectType.RULE:
            # Validate that the rule exists
            rules = object_registry.get_rules()
            entity = next(
                (d for d in rules if d.name == request.object_name),
                None,
            )
            if not entity:
                raise HTTPException(status_code=404, detail="Rule not found")

        if request.object_type == ConfigurableObjectType.AGENT:
            # Validate that the agent exists
            agents = object_registry.get_agents()
            entity = next(
                (a for a in agents if a.name == request.object_name),
                None,
            )
            if not entity:
                raise HTTPException(status_code=404, detail="Agent not found")

        config_manager = (
            rule_configuration
            if request.object_type == ConfigurableObjectType.RULE
            else agent_configuration
        )

        try:
            if request.config_id == DEFAULT_UUID:
                logger.info(
                    "reverting to default configuration",
                    object_type=request.object_type,
                    object_name=request.object_name,
                )
                await config_manager.promote_config(
                    request.config_id, object_name=request.object_name
                )
            else:
                logger.info(
                    "promoting configuration",
                    config_id=request.config_id,
                    object_type=request.object_type,
                    object_name=request.object_name,
                )
                await config_manager.promote_config(request.config_id)
        except ConfigNotFoundError as e:
            logger.exception("configuration not found during promotion")
            raise HTTPException(
                status_code=404,
                detail=f"Configuration with ID {e.invalid_id} and object_type {e.object_type} not found",
            )
        except ConfigValidationError as e:
            logger.exception("configuration validation failed during promotion")
            raise HTTPException(
                status_code=400,
                detail=e.to_api_response().model_dump(mode="json", by_alias=True),
            )

        if entity is None:
            # This case should ideally be caught by earlier checks
            logger.warning(
                "object not found after validation for promotion",
                object_type=request.object_type,
                object_name=request.object_name,
            )
            raise HTTPException(status_code=404, detail="Object not found")

        configs_list = await config_manager.read_configs_with_default(
            request.object_name,
            entity.to_config(),  # type: ignore
        )

        return ObjectConfigurationResponse(
            configs=cast(list[ObjectConfigurationBase], configs_list),
        )

    return router
