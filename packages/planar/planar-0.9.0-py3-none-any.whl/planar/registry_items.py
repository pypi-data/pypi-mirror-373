"""
Registry item classes for tracking registered objects.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Type, cast

from pydantic import BaseModel, create_model

from planar.modeling.json_schema_generator import (
    generate_json_schema_for_input_parameters,
    generate_json_schema_for_output_parameters,
)
from planar.utils import snake_case_to_camel_case
from planar.workflows.decorators import WorkflowWrapper


def create_pydantic_model_for_workflow(workflow: WorkflowWrapper) -> Type[BaseModel]:
    start_params = inspect.signature(workflow.original_fn).parameters
    start_fields = cast(
        Any,
        {
            name: (
                param.annotation,
                ... if param.default == param.empty else param.default,
            )
            for name, param in start_params.items()
        },
    )

    simple_name = workflow.function_name.split(".")[-1]
    start_model_name = f"{snake_case_to_camel_case(simple_name)}StartRequest"

    return create_model(start_model_name, **start_fields)


@dataclass(eq=False)
class RegisteredWorkflow:
    """Lightweight record of a registered workflow."""

    obj: "WorkflowWrapper"
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    pydantic_model: Type[BaseModel]

    @staticmethod
    def from_workflow(workflow: "WorkflowWrapper") -> "RegisteredWorkflow":
        """Create a RegisteredWorkflow from a WorkflowWrapper."""
        return RegisteredWorkflow(
            obj=workflow,
            name=workflow.function_name,
            description=workflow.__doc__
            or "No description provided for this workflow.",
            input_schema=generate_json_schema_for_input_parameters(
                workflow.original_fn
            ),
            output_schema=generate_json_schema_for_output_parameters(
                workflow.original_fn
            ),
            pydantic_model=create_pydantic_model_for_workflow(workflow),
        )
