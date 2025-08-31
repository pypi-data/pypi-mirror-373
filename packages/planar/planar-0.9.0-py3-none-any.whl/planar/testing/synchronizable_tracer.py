import asyncio
from dataclasses import dataclass
from typing import Any

from planar.workflows.tracing import LoggingTracer, Tracer


@dataclass(kw_only=True, frozen=True)
class TraceSpec:
    module_name: str | None = None
    function_name: str | None = None
    message: str | None = None
    kwargs: dict[str, Any] | None = None


def matches(
    spec: TraceSpec,
    module_name: str,
    function_name: str,
    message: str,
    kwargs: dict[str, Any],
) -> bool:
    if spec.module_name is not None and module_name != spec.module_name:
        return False
    if spec.function_name is not None and function_name != spec.function_name:
        return False
    if spec.message is not None and message != spec.message:
        return False
    if spec.kwargs is not None:
        for key, value in spec.kwargs.items():
            if key in kwargs and kwargs[key] != value:
                return False
    return True


class JoinTask:
    def __init__(self, task: asyncio.Task, signal: asyncio.Future):
        self.__task = task
        self.__signal = signal

    def start(self):
        if not self.__signal.done():
            self.__signal.set_result(None)
        return self.__task


class TraceController:
    def __init__(self, watcher: asyncio.Future, spec: TraceSpec):
        self.spec = spec
        self.watcher = watcher
        self.join_task: JoinTask | None = None
        self.__resume_trace = None
        self.__resumed = False
        self.__auto_resume = False

    async def wait(
        self, auto_resume: bool = True, timeout: float = 10, raise_timeout: bool = True
    ):
        try:
            self.__resume_trace = await asyncio.wait_for(self.watcher, timeout=timeout)
            if auto_resume or self.__auto_resume:
                self.resume()
        except asyncio.TimeoutError:
            formatted_trace = Tracer.format(
                module_name=self.spec.module_name or "(any)",
                function_name=self.spec.function_name or "(any)",
                task_name="(any)",
                pid=0,
                message=self.spec.message or "(any)",
                kwargs=self.spec.kwargs or {},
            )
            if raise_timeout:
                raise TimeoutError(f"timeout waiting for trace: {formatted_trace}")

    def resume(self):
        if self.__resumed:
            raise ValueError("resume called multiple times")
        if self.__resume_trace is None:
            self.__auto_resume = True
        else:
            self.__resume_trace.set_result(None)
            self.__resumed = True


class SynchronizableTracer(LoggingTracer):
    def __init__(self):
        self.timeout = 5
        self.races_detected = 0
        self.__controllers: list[TraceController] = []

    def instrument(self, spec: TraceSpec):
        future = asyncio.Future()
        controller = TraceController(future, spec)
        self.__controllers.append(controller)
        return controller

    def join(self, *trace_specs: TraceSpec):
        async def join(signal: asyncio.Future, controllers: list[TraceController]):
            await signal
            tasks = [
                asyncio.create_task(
                    controller.wait(
                        auto_resume=False, timeout=self.timeout * 2, raise_timeout=False
                    )
                )
                for controller in controllers
            ]
            done, _ = await asyncio.wait(tasks, timeout=self.timeout)
            for controller in controllers:
                controller.resume()
            if len(done) == len(controllers):
                self.races_detected += 1

        controllers = [self.instrument(spec) for spec in trace_specs]
        signal = asyncio.Future()
        task = JoinTask(asyncio.create_task(join(signal, controllers)), signal)
        for controller in controllers:
            controller.join_task = task

    async def trace(
        self,
        module_name: str,
        function_name: str,
        message: str,
        task_name: str,
        pid: int,
        kwargs: dict[str, Any],
    ):
        i = 0
        futures = []
        while i < len(self.__controllers):
            controller = self.__controllers[i]
            if not matches(
                controller.spec, module_name, function_name, message, kwargs
            ):
                i += 1
                continue
            self.__controllers.pop(i)
            future = asyncio.Future()
            try:
                controller.watcher.set_result(future)
            except asyncio.InvalidStateError:
                pass
            if controller.join_task:
                future = controller.join_task.start()
            futures.append(future)

        if futures:
            await asyncio.wait(futures, return_when=asyncio.ALL_COMPLETED)

        return await super().trace(
            module_name, function_name, message, task_name, pid, kwargs
        )
