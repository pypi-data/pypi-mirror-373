"""
Helper functions for field definitions and schema customization.
"""

from dataclasses import dataclass
from typing import Annotated, Any, Type

from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from planar.modeling.orm import PlanarBaseEntity


class JsonSchemaJson:
    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"$ref": "https://json-schema.org/draft/2020-12/schema"}


JsonSchema = Annotated[dict[str, Any], JsonSchemaJson]


@dataclass
class EntityField:
    entity: Type[PlanarBaseEntity]
    description: str | None = None
    display_field: str | None = None
    """
    Create a field that references an entity, with metadata for UI rendering.

    Args:
        entity: The entity class this field references
        display_field: Field to display in dropdowns (defaults to best guess)
        description: Field description

    Use this by annotating a field with:
    Annotated[str, EntityField(entity=MyEntity)]
    """

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema["description"] = self.description
        display_field = self.display_field
        if display_field is None:
            for field_name in ["name", "title", "username", "label", "display_name"]:
                if hasattr(self.entity, field_name):
                    display_field = field_name
                    break
        json_schema["x-planar-presentation"] = {
            "inputType": "entity-select",
            "entity": self.entity.__name__,
            "displayField": display_field,
        }
        return json_schema.copy()
