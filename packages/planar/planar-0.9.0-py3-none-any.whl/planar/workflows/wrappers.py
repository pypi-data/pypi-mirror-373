from dataclasses import dataclass
from typing import Callable, Coroutine, Generic
from uuid import UUID

from planar.utils import P, R, T, U
from planar.workflows.models import Workflow


@dataclass(kw_only=True)
class Wrapper(Generic[P, T, U, R]):
    original_fn: Callable[P, Coroutine[T, U, R]]
    wrapped_fn: Callable[P, Coroutine[T, U, R]]
    __doc__: str | None

    def __post_init__(self):
        self.__doc__ = self.original_fn.__doc__

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Coroutine[T, U, R]:
        return self.wrapped_fn(*args, **kwargs)

    @property
    def name(self):
        return self.wrapped_fn.__name__

    @property
    def __name__(self):
        return self.original_fn.__name__


@dataclass(kw_only=True)
class WorkflowWrapper(Wrapper[P, T, U, R]):
    function_name: str
    start: Callable[P, Coroutine[T, U, Workflow]]
    start_step: Callable[P, Coroutine[T, U, UUID]]
    wait_for_completion: Callable[[UUID], Coroutine[T, U, R]]


@dataclass(kw_only=True)
class StepWrapper(Wrapper[P, T, U, R]):
    wrapper: Callable[P, Coroutine[T, U, R]]
    auto_workflow: WorkflowWrapper[P, T, U, R]
