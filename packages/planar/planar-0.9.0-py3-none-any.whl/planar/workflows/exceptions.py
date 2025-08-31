import builtins
from typing import Any


class StepError(Exception):
    def __init__(self, type: str, message: str):
        self.type = type
        self.original_message = message
        super().__init__(f"{type}: {message}")


class WorkflowError(StepError):
    pass


class LockResourceFailed(Exception):
    pass


class NonDeterministicStepCallError(Exception):
    """Raised when a step call is not deterministic compared to previous executions."""

    pass


def try_restore_exception(exception: dict[str, Any]) -> Exception:
    exc_type = exception["type"]
    exc_message = exception["message"]
    # Try to get the exception class from the builtins module
    exc_class = getattr(builtins, exc_type, None)
    if isinstance(exc_class, type) and issubclass(exc_class, Exception):
        return exc_class(exc_message)
    # Fallback to a custom exception if not found
    return StepError(exc_type, exc_message)
