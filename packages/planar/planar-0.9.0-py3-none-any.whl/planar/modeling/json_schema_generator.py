import inspect
from typing import Any, Callable, Optional, get_args, get_origin, get_type_hints

from pydantic import create_model

from planar.logging import get_logger
from planar.modeling.field_helpers import JsonSchema

logger = get_logger(__name__)


def generate_json_schema_for_input_parameters(func: Callable[..., Any]) -> JsonSchema:
    """Generate a Pydantic model from a function's parameters and return it as JSON schema."""
    logger.debug(
        "generating input json schema for function", function_name=func.__name__
    )
    class_name = "DynamicInputModel"

    sig = inspect.signature(func)
    type_hints = get_type_hints(func)

    fields = {}
    for param_name, param in sig.parameters.items():
        # Skip self/cls for methods
        if param_name in ("self", "cls") and param.kind == param.POSITIONAL_OR_KEYWORD:
            continue

        param_type = type_hints.get(param_name, Any)

        is_optional = False
        if get_origin(param_type) is Optional:
            param_type = get_args(param_type)[0]
            is_optional = True

        if param.default is not param.empty:
            default = param.default
        elif is_optional:
            default = None
        else:
            default = ...  # Required field with no default

        fields[param_name] = (param_type, default)

    logger.debug(
        "fields for input model",
        function_name=func.__name__,
        fields=list(fields.keys()),
    )
    model_class = create_model(class_name, **fields)
    schema = model_class.model_json_schema()
    logger.debug(
        "generated input schema",
        function_name=func.__name__,
        title=schema.get("title", class_name),
    )
    return schema


def generate_json_schema_for_output_parameters(func: Callable[..., Any]) -> JsonSchema:
    """Generate a Pydantic model from a function's output parameters and return it as JSON schema."""
    logger.debug(
        "generating output json schema for function", function_name=func.__name__
    )
    class_name = "DynamicOutputModel"

    type_hints = get_type_hints(func)
    return_type = type_hints.get("return", Any)

    is_optional = False
    if get_origin(return_type) is Optional:
        return_type = get_args(return_type)[0]
        is_optional = True

    if is_optional:
        default = None
    else:
        default = ...  # Required field with no default

    fields = {}
    fields["output_type"] = (return_type, default)

    logger.debug(
        "field for output model",
        function_name=func.__name__,
        fields=list(fields.keys()),
    )
    model_class = create_model(class_name, **fields)
    schema = model_class.model_json_schema()
    logger.debug(
        "generated output schema",
        function_name=func.__name__,
        title=schema.get("title", class_name),
    )
    return schema
