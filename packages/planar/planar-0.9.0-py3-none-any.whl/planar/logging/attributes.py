import asyncio
import logging
import os
import threading

from planar.workflows.context import get_context, in_context

from .context import get_context_metadata

pid = os.getpid()


def _in_event_loop_task() -> bool:
    """
    Checks if the current thread is the main thread and an asyncio event loop is running.
    """
    try:
        return (
            threading.main_thread() == threading.current_thread()
            and asyncio.get_running_loop() is not None
        )
    except RuntimeError:
        return False


class ExtraAttributesFilter(logging.Filter):
    """
    A logging filter that adds extra contextual attributes to log records.

    Attributes added:
    - pid: The process ID.
    - workflow_id: The ID of the current workflow, if in a workflow context.
    - step_id: The ID of the current step, if in a workflow context.
    - task_name: The name of the current asyncio task.
    - Other attributes from the logging context.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Adds extra attributes to the log record.
        """
        setattr(record, "pid", pid)

        context_metadata = get_context_metadata()
        for key, value in context_metadata.items():
            setattr(record, key, value)

        if _in_event_loop_task():
            if in_context():
                ctx = get_context()
                setattr(record, "workflow_id", str(ctx.workflow_id))
                setattr(record, "step_id", ctx.current_step_id)

        return True
