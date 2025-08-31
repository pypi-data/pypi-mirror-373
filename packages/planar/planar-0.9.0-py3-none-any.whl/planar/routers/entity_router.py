from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import func
from sqlmodel import select

from planar.logging import get_logger
from planar.modeling.orm.query_filter_builder import build_paginated_query
from planar.object_registry import ObjectRegistry
from planar.routers.models import EntityInstance, EntityInstanceList, EntityMetadata
from planar.session import get_session

logger = get_logger(__name__)


def create_entities_router(object_registry: ObjectRegistry) -> APIRouter:
    router = APIRouter(tags=["Entities"])

    @router.get("/", response_model=list[EntityMetadata])
    async def get_entities():
        entities = object_registry.get_entities()
        session = get_session()

        result = []
        for entity in entities:
            instance_count = 0

            # Get count of instances for this entity
            count_query = select(func.count()).select_from(entity)
            instance_count = await session.scalar(count_query) or 0

            result.append(
                EntityMetadata(
                    name=entity.__name__,
                    description=entity.__doc__,
                    json_schema=entity.model_json_schema(),
                    instance_count=instance_count,
                )
            )
        return result

    @router.get("/{entity_name}/instances", response_model=EntityInstanceList)
    async def get_entity_instances(
        entity_name: str,
        skip: int = 0,
        limit: int = 100,
    ):
        """
        Get instances of a domain model entity from the database.
        Only works for entities that have a database table.
        """
        entities = object_registry.get_entities()

        # Find the entity class by name
        entity_class = next(
            (entity for entity in entities if entity.__name__ == entity_name), None
        )

        if not entity_class:
            logger.warning("entity not found", entity_name=entity_name)
            raise HTTPException(
                status_code=404, detail=f"Entity {entity_name} not found"
            )

        # Check if entity is a DB table (not an enum)
        if not hasattr(entity_class, "__tablename__"):
            logger.warning("entity is not a database table", entity_name=entity_name)
            raise HTTPException(
                status_code=400,
                detail=f"Entity {entity_name} is not stored in database",
            )

        # Fetch instances from DB
        session = get_session()
        base_query = select(entity_class)

        # Build paginated query and count query
        paginated_query, count_query = build_paginated_query(
            base_query, offset=skip, limit=limit
        )

        # Count total matching records
        total_count = await session.scalar(count_query) or 0

        # Execute query
        results = (await session.exec(paginated_query)).all()

        # Convert to EntityInstance objects
        instances = [
            EntityInstance(
                id=str(result.id), entity_name=entity_name, data=result.model_dump()
            )
            for result in results
        ]

        return EntityInstanceList(
            items=instances, total=total_count, offset=skip, limit=limit
        )

    @router.get("/{entity_name}/instances/{instance_id}", response_model=EntityInstance)
    async def get_entity_instance_by_id(entity_name: str, instance_id: UUID):
        """
        Get a specific entity instance by its ID.
        Only works for entities that have a database table.
        """
        entities = object_registry.get_entities()

        # Find the entity class by name
        entity_class = next(
            (entity for entity in entities if entity.__name__ == entity_name), None
        )

        if not entity_class:
            logger.warning(
                "entity not found when trying to get instance by id",
                entity_name=entity_name,
            )
            raise HTTPException(
                status_code=404, detail=f"Entity {entity_name} not found"
            )

        # Fetch the specific instance from DB
        session = get_session()
        result = await session.get(entity_class, instance_id)

        if not result:
            logger.warning(
                "instance with id not found for entity",
                instance_id=instance_id,
                entity_name=entity_name,
            )
            raise HTTPException(
                status_code=404,
                detail=f"Instance with ID {instance_id} not found for entity {entity_name}",
            )

        # Convert to EntityInstance object
        instance_data = result.model_dump()
        return EntityInstance(
            id=str(result.id), entity_name=entity_name, data=instance_data
        )

    return router
