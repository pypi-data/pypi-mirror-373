"""
NOTE: The naming of this module and its functions is not entirely accurate. The actual
serialization to/from JSON is handled by SQLAlchemy. This module is responsible for
converting Python objects (like Pydantic models, custom classes, and primitive types)
to/from types that are JSON-serializable, so they can be properly stored and retrieved
from the database.
"""

import inspect
import uuid
from dataclasses import fields, is_dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from types import UnionType
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from pydantic import BaseModel

from planar.logging import get_logger

logger = get_logger(__name__)

# Type variable for pydantic models
ModelT = TypeVar("ModelT", bound=BaseModel)


def is_pydantic_model(obj_type: Any) -> bool:
    """Check if a type is a pydantic model."""
    return inspect.isclass(obj_type) and issubclass(obj_type, BaseModel)


# Custom serialization for primitives without a Pydantic wrapper
def serialize_primitive(value: Any) -> Any:
    """Convert a primitive type into a JSON-serializable form."""
    if isinstance(value, (bool, int, float)):
        return value
    elif isinstance(value, Decimal):
        # Preserve precision by converting to a string
        return str(value)
    elif isinstance(value, uuid.UUID):
        return str(value)
    elif isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, timedelta):
        # Represent timedelta as a dict
        return {
            "days": value.days,
            "seconds": value.seconds,
            "microseconds": value.microseconds,
        }
    else:
        return value


def deserialize_primitive(value: Any, type_hint: Type) -> Any:
    """Convert a JSON-serializable representation back to a primitive type."""
    if type_hint is bool:
        return bool(value)
    elif type_hint is int:
        return int(value)
    elif type_hint is float:
        return float(value)
    elif type_hint is Decimal:
        return Decimal(value)
    elif type_hint is uuid.UUID:
        return uuid.UUID(value)
    elif type_hint is datetime:
        return datetime.fromisoformat(value)
    elif type_hint is date:
        return date.fromisoformat(value)
    elif type_hint is timedelta:
        if isinstance(value, dict) and all(
            k in value for k in ("days", "seconds", "microseconds")
        ):
            return timedelta(**value)
        elif isinstance(value, (int, float)):
            return timedelta(seconds=value)
        else:
            raise ValueError(f"Cannot deserialize {value} as timedelta")
    else:
        return value


def serialize_value(value: Any) -> Any:
    """
    Serialize a value based on its runtime type.

    - If it's a Pydantic model, call model_dump(mode="json").
    - For supported primitives, use the custom serializer.
    - Otherwise, return the value as is.
    """
    if value is None:
        return None

    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")

    if isinstance(value, type(BaseModel)):
        return cast(BaseModel, value).model_json_schema()

    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: serialize_value(getattr(value, f.name)) for f in fields(value)}

    # Handle lists
    if isinstance(value, list):
        return [serialize_value(v) for v in value]

    if isinstance(
        value, (bool, int, float, Decimal, uuid.UUID, datetime, timedelta, date)
    ):
        return serialize_primitive(value)

    return value


def deserialize_value(
    value: Any,
    type_hint: Type | UnionType | None = None,
) -> Any:
    """
    Deserialize a value based on the provided type hint.

    - If the type hint is a Union, try each candidate.
    - If it's a Pydantic model, use model_validate().
    - For supported primitives, use the custom deserializer.
    - Otherwise, return the value as is.
    """
    if value is None or type_hint is None:
        return value

    # Handle Union types by trying each candidate.
    origin = get_origin(type_hint)
    if origin is Union or origin is UnionType:
        for candidate in get_args(type_hint):
            if candidate is type(None):
                continue
            try:
                return deserialize_value(value, candidate)
            except Exception:
                continue
        raise ValueError(f"Could not deserialize {value} into any type in {type_hint}")

    if origin is list:
        inner_type = get_args(type_hint)[0]
        deserialized_list = []
        for item in value:
            deserialized_list.append(deserialize_value(item, inner_type))
        return deserialized_list

    # Handle Type[T] (i.e., type hints like type[Person])
    if origin is type:
        inner_type = get_args(type_hint)[0]
        if inspect.isclass(inner_type) and issubclass(inner_type, BaseModel):
            if (
                "title" not in value
                or value["title"] != inner_type.__name__
                or "type" not in value
                or value["type"] != "object"
            ):
                raise ValueError(f"Invalid type hint {type_hint} for {value}")
            # Techincally, no deserialization is needed since the type hint is already the
            # Pydantic class we need.
            # To be more strict we could check inner_type.model_json_schema() == value,
            # but that would not allow backwards compatibility in Pydantic model changes.
            return inner_type

    if is_pydantic_model(type_hint):
        return cast(BaseModel, type_hint).model_validate(value)

    if inspect.isclass(type_hint) and is_dataclass(type_hint):
        kwargs = {}
        if isinstance(value, dict):
            for f in fields(type_hint):
                kwargs[f.name] = deserialize_value(
                    value.get(f.name), cast(Type | UnionType | None, f.type)
                )
        return type_hint(**kwargs)

    # Check if type_hint is a plain type before passing to deserialize_primitive
    if isinstance(type_hint, type) and type_hint in (
        bool,
        int,
        float,
        Decimal,
        uuid.UUID,
        datetime,
        timedelta,
    ):
        return deserialize_primitive(value, type_hint)

    return value


def serialize_args(
    func: Callable, args: Sequence[Any], kwargs: Dict[str, Any]
) -> tuple[List[Any], Dict[str, Any]]:
    """
    Serialize function arguments based solely on their runtime values.
    """
    serialized_args = [serialize_value(arg) for arg in (args or [])]
    serialized_kwargs = {
        key: serialize_value(val) for key, val in (kwargs or {}).items()
    }

    return serialized_args, serialized_kwargs


def deserialize_args(
    func: Callable, args: List[Any], kwargs: Dict[str, Any]
) -> tuple[List[Any], Dict[str, Any]]:
    """
    Deserialize function arguments using the function signature's type hints.
    """
    type_hints = get_type_hints(func)
    deserialized_args = []
    deserialized_kwargs = {}

    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())

    for i, arg in enumerate(args or []):
        if i < len(param_names):
            param_name = param_names[i]
            type_hint = type_hints.get(param_name)
            deserialized_args.append(deserialize_value(arg, type_hint))
        else:
            deserialized_args.append(arg)

    for key, val in (kwargs or {}).items():
        type_hint = type_hints.get(key)
        deserialized_kwargs[key] = deserialize_value(val, type_hint)

    return deserialized_args, deserialized_kwargs


def serialize_result(func: Callable, result: Any) -> Any:
    """
    Serialize a function result based solely on its runtime value.
    """
    if result is None:
        return None

    return serialize_value(result)


# --- Simplified Generic Type Handling Helpers ---


def _get_generic_metadata(type_hint: Any) -> Tuple[Type | None, Tuple[Any, ...] | None]:
    """Gets origin and args, handling standard typing and Pydantic generics."""
    origin = get_origin(type_hint)
    args = get_args(type_hint)
    if origin is None and hasattr(type_hint, "__pydantic_generic_metadata__"):
        metadata = getattr(type_hint, "__pydantic_generic_metadata__", {})
        origin = metadata.get("origin")
        args = metadata.get("args")
        if not (origin and args is not None):
            return None, None  # Return None if Pydantic metadata is incomplete
    return origin, args


def _infer_concrete_type_from_args(
    func: Callable,
    func_args: Sequence[Any],
    func_kwargs: Dict[str, Any],
    target_typevar: TypeVar,
) -> Type | None:
    """Infers the concrete type for a TypeVar based on function parameters (T or list[T])."""
    type_hints = get_type_hints(func)
    sig = inspect.signature(func)
    try:
        bound_args = sig.bind(*func_args, **func_kwargs)
        bound_args.apply_defaults()
    except TypeError:
        return None  # Cannot infer if binding fails

    for param_name, arg_value in bound_args.arguments.items():
        logger.info("parameter info", param_name=param_name, arg_value=arg_value)
        param_hint = type_hints.get(param_name)
        if param_hint is None or arg_value is None:
            continue

        # Direct Match: param is T
        if (
            isinstance(param_hint, TypeVar)
            and param_hint.__name__ == target_typevar.__name__
        ):
            return type(arg_value)

        # List Match: param is list[T]
        param_origin, param_args = _get_generic_metadata(param_hint)
        if (
            param_origin in (list, List)
            and param_args
            and isinstance(param_args[0], TypeVar)
            and param_args[0].__name__ == target_typevar.__name__
        ):
            if isinstance(arg_value, list) and arg_value:
                # Use type of first non-None element
                element_type = next(
                    (type(el) for el in arg_value if el is not None), None
                )
                if element_type:
                    return element_type
    return None  # TypeVar not found or could not infer type


def deserialize_result(
    func: Callable,
    result: Any,
    return_type: Type | None = None,
    args: Sequence[Any] | None = None,
    kwargs: Dict[str, Any] | None = None,
) -> Any:
    if result is None:
        return None

    args = args or []
    kwargs = kwargs or {}

    # Use explicit return_type if provided
    if return_type is not None:
        logger.debug(
            "using explicitly provided return type", return_type=str(return_type)
        )
        return deserialize_value(result, return_type)

    # Otherwise, fallback to inferring from function signature
    logger.debug("inferring return type from function signature")
    type_hints = get_type_hints(func)
    return_type_hint = type_hints.get("return")

    if return_type_hint is None:
        logger.debug(
            "no return type hint found in signature, deserializing without hint"
        )
        return deserialize_value(result, None)

    return_origin, return_args = _get_generic_metadata(return_type_hint)

    # Check if inference is needed for generics based on signature
    is_generic_base_model = (
        return_origin
        and inspect.isclass(return_origin)
        and issubclass(return_origin, BaseModel)
        and issubclass(return_origin, Generic)
    )

    # Only attempt inference if the signature hint is a Generic Pydantic model
    # with a single TypeVar argument.
    target_typevar = None
    is_list_wrapped = False
    if is_generic_base_model and return_args and len(return_args) == 1:
        type_arg = return_args[0]
        if isinstance(type_arg, TypeVar):
            target_typevar = type_arg
        else:
            arg_origin, inner_args = _get_generic_metadata(type_arg)
            if (
                arg_origin in (list, List)
                and inner_args
                and isinstance(inner_args[0], TypeVar)
            ):
                target_typevar = inner_args[0]
                is_list_wrapped = True

    if target_typevar is None:
        # Not a generic type requiring inference, or inference not possible/needed.
        logger.debug(
            "using signature return type hint directly",
            return_type_hint=str(return_type_hint),
        )
        return deserialize_value(result, return_type_hint)

    # Infer the concrete type for T
    concrete_type = _infer_concrete_type_from_args(func, args, kwargs, target_typevar)

    if not concrete_type:
        logger.warning(
            "could not infer concrete type, using original hint",
            target_typevar=str(target_typevar),
            return_type_hint=return_type_hint,
        )
        return deserialize_value(result, return_type_hint)

    # Construct the final concrete type and deserialize
    try:
        final_arg = list[concrete_type] if is_list_wrapped else concrete_type  # type: ignore
        concrete_return_type = return_origin[final_arg]  # type: ignore
        logger.debug(
            "constructed concrete return type",
            concrete_return_type=str(concrete_return_type),
        )
        return deserialize_value(result, concrete_return_type)
    except Exception:
        logger.exception(
            "error reconstructing/deserializing",
            return_origin=return_origin,
        )
        return deserialize_value(result, return_type_hint)  # Fallback
