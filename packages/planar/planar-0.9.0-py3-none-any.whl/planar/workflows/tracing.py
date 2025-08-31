import asyncio
import inspect
import os
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from contextvars import ContextVar
from datetime import datetime
from typing import TypeAlias
from uuid import UUID

from planar.logging import get_logger

TraceArg: TypeAlias = UUID | datetime | str | int | float | bool | None


class Tracer(ABC):
    @abstractmethod
    async def trace(
        self,
        module_name: str,
        function_name: str,
        message: str,
        task_name: str,
        pid: int,
        kwargs: dict[str, TraceArg],
    ) -> None: ...

    @classmethod
    def format(
        cls,
        module_name: str,
        function_name: str,
        task_name: str,
        pid: int,
        message: str,
        kwargs: dict[str, TraceArg],
    ) -> str:
        return " - ".join(
            [
                f"{module_name}.{function_name}",
                message,
                " ".join(f"{k}={v}" for k, v in kwargs.items()),
                f"{task_name} PID={pid}",
            ]
        )


class LoggingTracer(Tracer):
    async def trace(
        self,
        module_name: str,
        function_name: str,
        message: str,
        task_name: str,
        pid: int,
        kwargs: dict[str, TraceArg],
    ):
        get_logger(module_name).debug(
            self.format(module_name, function_name, task_name, pid, message, kwargs)
        )


def __get_trace_caller():
    frame = inspect.currentframe()
    try:
        assert frame
        parent_frame = frame.f_back
        assert parent_frame
        assert parent_frame.f_code.co_name == "trace"
        # Get the frame of the caller (2 level ups from current frame)
        caller_frame = parent_frame.f_back
        assert caller_frame
        # Get the function name from the caller's frame
        module_name = caller_frame.f_globals["__name__"]
        return str(module_name), caller_frame.f_code.co_qualname
    finally:
        # Always delete the frame reference to prevent reference cycles
        del frame


__PID = os.getpid()


async def trace(message: str, **kwargs: TraceArg) -> None:
    tracer = tracer_var.get(None)
    if not tracer:
        return
    # Get useful information about the caller and forward it to the tracer
    module_name, func_name = __get_trace_caller()
    current_task = asyncio.current_task()
    assert current_task
    await tracer.trace(
        module_name, func_name, message, current_task.get_name(), __PID, kwargs
    )


tracer_var: ContextVar[Tracer] = ContextVar("tracer")


@asynccontextmanager
async def tracer_context(tracer: Tracer):
    token = tracer_var.set(tracer)
    try:
        yield
    finally:
        tracer_var.reset(token)
