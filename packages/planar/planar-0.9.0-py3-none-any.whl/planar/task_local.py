import asyncio
from typing import Generic, TypeVar
from weakref import WeakKeyDictionary

T = TypeVar("T")


class TaskLocal(Generic[T]):
    def __init__(self):
        self._data = WeakKeyDictionary()

    def set(self, context: T):
        current_task = asyncio.current_task()
        if not current_task:
            raise RuntimeError("No current task")
        self._data[current_task] = context

    def get(self) -> T:
        current_task = asyncio.current_task()
        if not current_task:
            raise RuntimeError("No current task")
        context = self._data.get(current_task)
        if context is None:
            raise RuntimeError("No execution context")
        return context

    def clear(self):
        current_task = asyncio.current_task()
        if not current_task:
            raise RuntimeError("No current task")
        del self._data[current_task]

    def is_set(self) -> bool:
        current_task = asyncio.current_task()
        if not current_task:
            raise RuntimeError("No current task")
        return self._data.get(current_task) is not None
