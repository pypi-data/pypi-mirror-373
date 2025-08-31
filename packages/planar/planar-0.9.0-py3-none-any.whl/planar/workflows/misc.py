from typing import Any, Callable


def func_full_name(func: Callable[..., Any]) -> str:
    return f"{func.__module__}.{func.__qualname__}"
