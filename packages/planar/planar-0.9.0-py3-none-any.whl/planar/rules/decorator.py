from __future__ import annotations

import inspect
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Coroutine, Type, TypeVar, cast
from uuid import UUID

from pydantic import BaseModel

from planar.logging import get_logger
from planar.rules.models import Rule
from planar.rules.rule_configuration import rule_configuration
from planar.rules.runner import EvaluateResponse, evaluate_rule
from planar.workflows.decorators import step
from planar.workflows.models import StepType

logger = get_logger(__name__)

RULE_REGISTRY = {}

# Define type variables for input and output BaseModel types
T = TypeVar("T", bound=BaseModel)
U = TypeVar("U", bound=BaseModel)


def serialize_for_rule_evaluation(obj: Any) -> Any:
    """
    Custom serializer that converts Pydantic model_dump() to a format that can be
    interpreted by the rule engine.
    """
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        # Zen rule engine throws an error if the datetime does not include timezone
        # ie. `"2025-05-27T00:21:44.802433" is not a "date-time"`
        return obj.isoformat() + "Z" if obj.tzinfo is None else obj.isoformat()
    elif isinstance(obj, dict):
        return {key: serialize_for_rule_evaluation(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_rule_evaluation(item) for item in obj]
    else:
        return obj


#### Decorator
def rule(*, description: str):
    def _get_input_and_return_types(
        func: Callable,
    ) -> tuple[Type[BaseModel], Type[BaseModel]]:
        """
        Validates that a rule method has proper type annotations.
        Returns a tuple of (input_type, return_type).
        """

        # Get function parameters using inspect module
        signature = inspect.signature(func)
        params = list(signature.parameters.keys())

        if len(params) != 1 or "self" in params:
            err_msg = (
                "@rule method must have exactly one input argument (and cannot be self)"
            )
            logger.warning(
                "rule definition error", function_name=func.__name__, error=err_msg
            )
            raise ValueError(err_msg)

        # Check for missing annotations using signature
        missing_annotations = [
            p
            for p in params
            if signature.parameters[p].annotation == inspect.Parameter.empty
        ]
        if missing_annotations:
            err_msg = (
                f"Missing annotations for parameters: {', '.join(missing_annotations)}"
            )
            logger.warning(
                "rule definition error", function_name=func.__name__, error=err_msg
            )
            raise ValueError(err_msg)

        if signature.return_annotation == inspect.Signature.empty:
            err_msg = "@rule method must have a return type annotation"
            logger.warning(
                "rule definition error", function_name=func.__name__, error=err_msg
            )
            raise ValueError(err_msg)

        param_name = params[0]
        input_type = signature.parameters[param_name].annotation
        return_type = signature.return_annotation

        # Ensure both input and return types are pydantic BaseModels
        if not issubclass(input_type, BaseModel):
            err_msg = f"Input type {input_type.__name__} must be a pydantic BaseModel"
            logger.warning(
                "rule definition error", function_name=func.__name__, error=err_msg
            )
            raise ValueError(err_msg)
        if not issubclass(return_type, BaseModel):
            err_msg = f"Return type {return_type.__name__} must be a pydantic BaseModel"
            logger.warning(
                "rule definition error", function_name=func.__name__, error=err_msg
            )
            raise ValueError(err_msg)

        return input_type, return_type

    def decorator(func: Callable[[T], U]) -> Callable[[T], Coroutine[Any, Any, U]]:
        input_type, return_type = _get_input_and_return_types(func)

        rule = Rule(
            name=func.__name__,
            description=description,
            input=input_type,
            output=return_type,
        )

        RULE_REGISTRY[func.__name__] = rule
        logger.debug("registered rule", rule_name=func.__name__)

        @step(step_type=StepType.RULE)
        @wraps(func)
        async def wrapper(input: T) -> U:
            logger.debug(
                "executing rule", rule_name=func.__name__, input_type=type(input)
            )
            # Look up any existing decision override for this function name
            override_result = await rule_configuration.read_configs_with_default(
                func.__name__, rule.to_config()
            )

            active_config = next(
                (config for config in override_result if config.active), None
            )

            if not active_config:
                raise ValueError(
                    f"No active configuration found for rule {func.__name__}"
                )

            logger.debug(
                "active config for rule",
                rule_name=func.__name__,
                version=active_config.version,
            )

            if active_config.version == 0:
                logger.info(
                    "using default python implementation for rule",
                    rule_name=func.__name__,
                )
                # default implementation
                return func(input)
            else:
                logger.info(
                    "using jdm override for rule",
                    version=active_config.version,
                    rule_name=func.__name__,
                )
                serialized_input = serialize_for_rule_evaluation(input.model_dump())
                evaluation_response = evaluate_rule(
                    active_config.data.jdm, serialized_input
                )
                if isinstance(evaluation_response, EvaluateResponse):
                    result_model = return_type.model_validate(
                        evaluation_response.result
                    )
                    return cast(U, result_model)
                else:
                    logger.warning(
                        "rule evaluation error",
                        rule_name=func.__name__,
                        message=evaluation_response.message,
                    )
                    raise Exception(evaluation_response.message)

        wrapper.__rule__ = rule  # type: ignore

        return wrapper

    return decorator
