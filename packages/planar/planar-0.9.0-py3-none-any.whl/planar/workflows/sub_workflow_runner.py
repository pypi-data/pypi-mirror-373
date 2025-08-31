# This module contains a code for running workflows and steps as background
# tasks.
# This functionality is very complex and not well tested, so it is going to be
# disabled for now. In the future if there's demand for it, we can enable it
# again.
# For reference, this is the commit where it was enabled:
# 8c6b7decbdfc01072b5a0be66597690a487455d5
from asyncio import Future, create_task
from dataclasses import dataclass
from typing import Any, Coroutine, Mapping, Sequence, cast
from uuid import UUID

from planar.session import get_engine, session_context
from planar.task_local import TaskLocal
from planar.utils import P, R, T, U
from planar.workflows.context import (
    ExecutionContext,
    get_context,
    in_context,
    set_context,
)
from planar.workflows.wrappers import StepWrapper, WorkflowWrapper


@dataclass(kw_only=True)
class SubWorkflowCall:
    wrapper: WorkflowWrapper
    args: Sequence[Any]
    kwargs: Mapping[str, Any]
    started: Future[UUID]


# When a workflow is running, it will may call steps and other workflows. This
# class encapsulates the logic for handling the various ways in which this can
# happen.

# The simplest case is when steps/workflows are called using `await` directly
# in the current task (when "in_context").


# For workflows this means we'll start the workflow as a step (every workflow has an
# auto generated "start step"), which makes the operation durable. Additionally
# we call the "wait_for_completion" helper, which waits for the workflow to
# complete (up to a timeout) and returns the result.
#
# For steps it is even simpler after all, calling steps is the most common thing that
# can be done in a workflow.
#
# Things start to get more complicated when workflows or steps are called using
# `asyncio.create_task`, which means it will run in a separate task without
# blocking the current one.
#
# A lot of the logic in SubWorkflowRunner is about dealing with multiple
# background workflows/steps starting at the same time. To make these
# operations durable, we must do some magic to force the concurrent workflows
# to start in the order they were called.
#
# The initial work is done by the "run" method, which cannot be an async
# function since it must be able to access the current workflow context. If we
# used an async function, it would only start executing when the new task
# started. OTOH we can only know if a step/workflow was called in a separate task
# in an async function (the "context forwarder"). So this is what we do:
#
#   - in the "run" method, we collect the all information about the calls in a list,
#     (pending_sub_workflow_calls) withou actually calling anything, and then we call
#     the appropriate context forwarder for steps/worfklows.
#   - in the workflow context forwarder, if we were called in a separate task we
#     invoke the "start_sub_workflow" function, which will search for the current
#     workflow start function in the pending list and invoke the workflow's "waiter",
#     an async function which will wait for a signal that the workflow has started
#     (signal passed via a future).
#   - after the last workflow is discovered, we invoke a "starter" task that
#     will start all workflows in the correct order, signaling futures associated
#     with the workflow
#
# The above magic is what ensures that child concurrent workflows will start in a
# predictable order, and will be durable against restarts.
#
# For steps, the only thing that makes sense is to run it in a separate
# workflow, or else there would be no ordering of completion, and that's why
# every step has an "auto workflow", thus entering in the same path as
# concurrent subworkflows described above.
class SubWorkflowRunner:
    def __init__(self):
        self._pending_sub_workflow_calls: list[SubWorkflowCall] = []

    def run(
        self,
        wrapper: WorkflowWrapper[P, T, U, R] | StepWrapper[P, T, U, R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Coroutine[T, U, R]:
        async def starter(ctx: ExecutionContext):
            # Main starter task that will call the start steps in the order
            # they were called
            set_context(ctx)
            sub_workflow_calls = self._pending_sub_workflow_calls[:]
            self._pending_sub_workflow_calls.clear()
            async with session_context(get_engine()):
                for sub_workflow_call in sub_workflow_calls:
                    args = sub_workflow_call.args
                    kwargs = sub_workflow_call.kwargs
                    start_step = sub_workflow_call.wrapper.start_step
                    workflow_id = await start_step(*args, **kwargs)
                    sub_workflow_call.started.set_result(workflow_id)

        async def waiter(future: Future[UUID], wf_wrapper: WorkflowWrapper[P, T, U, R]):
            # only call wait_for_completion after receiving the workflow_id
            # from the future
            workflow_id = await future
            completion_coro = wf_wrapper.wait_for_completion(workflow_id)
            return await cast(Coroutine[T, U, R], completion_coro)

        def start_sub_workflow(wf_wrapper: WorkflowWrapper[P, T, U, R]):
            ctx = get_context()

            # find the matching call instance
            future = None
            index = 0
            for index, sub_workflow_call in enumerate(self._pending_sub_workflow_calls):
                if sub_workflow_call.wrapper == wf_wrapper:
                    future = sub_workflow_call.started
                    break

            if index == len(self._pending_sub_workflow_calls) - 1:
                # Last subworkflow. Run the starter task that will start all
                # workflows in the correct order
                create_task(starter(ctx))

            assert future
            return waiter(future, wf_wrapper)

        async def workflow_context_forwarder(
            parent_execution_context: ExecutionContext,
            wf_wrapper: WorkflowWrapper[P, T, U, R],
        ):
            if not in_context():
                # invoke "start_sub_workflow" after forwarding the parent context
                set_context(parent_execution_context)
                return await cast(Coroutine[T, U, R], start_sub_workflow(wf_wrapper))

            # Simple case, no need to start any starter task.
            # Clear pending calls and invoke the start step directly.
            assert len(self._pending_sub_workflow_calls) == 1
            self._pending_sub_workflow_calls.clear()
            workflow_id = await wf_wrapper.start_step(*args, **kwargs)
            # Wait for completion
            completion_coro = wf_wrapper.wait_for_completion(workflow_id)
            return await cast(Coroutine[T, U, R], completion_coro)

        async def step_context_forwarder(
            parent_execution_context: ExecutionContext,
            step_wrapper: StepWrapper,
        ):
            if not in_context():
                # Invoke the workflow context forwarder, passing in the auto workflow
                return await workflow_context_forwarder(
                    parent_execution_context, step_wrapper.auto_workflow
                )
            # Simple case. Clear the pending calls and invoke the step
            # wrapper directly.
            assert len(self._pending_sub_workflow_calls) == 1
            self._pending_sub_workflow_calls.clear()
            return await step_wrapper.wrapper(*args, **kwargs)

        # add the workflow wrapper, along with args and a future to the pending list
        self._pending_sub_workflow_calls.append(
            SubWorkflowCall(
                wrapper=wrapper.auto_workflow
                if isinstance(wrapper, StepWrapper)
                else wrapper,
                started=Future(),
                args=args,
                kwargs=kwargs,
            )
        )

        # invoke the correct context forwarder
        if isinstance(wrapper, StepWrapper):
            return step_context_forwarder(get_context(), wrapper)
        else:
            return workflow_context_forwarder(get_context(), wrapper)


data: TaskLocal[SubWorkflowRunner] = TaskLocal()


def get_sub_workflow_runner() -> SubWorkflowRunner:
    if not data.is_set():
        data.set(SubWorkflowRunner())
    return data.get()
