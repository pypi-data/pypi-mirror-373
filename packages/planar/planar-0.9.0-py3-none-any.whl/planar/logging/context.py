from contextvars import ContextVar
from typing import Any

context_metadata: ContextVar[dict[str, Any]] = ContextVar("context_metadata")


def set_context_metadata(key: str, value: Any):
    if not context_metadata.get(False):
        context_metadata.set({})
    context_metadata.get()[key] = value


def get_context_metadata() -> dict[str, Any]:
    return context_metadata.get({})
