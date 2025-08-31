from asyncio import Future, wait_for
from collections import defaultdict
from uuid import UUID

from planar.workflows import Workflow, WorkflowNotification
from planar.workflows.models import WorkflowStep


class WorkflowObserver:
    def __init__(self):
        # Scope notification queues and waiters by workflow_id

        self.notification_queues: defaultdict[UUID, list[WorkflowNotification]] = (
            defaultdict(list)
        )
        self.waiters: dict[UUID, Future[None]] = {}
        self.timeout = 10

    def _get_workflow_id_from_notification(
        self, notification: WorkflowNotification
    ) -> UUID:
        """Extract workflow_id from notification data"""
        if isinstance(notification.data, Workflow):
            return notification.workflow_id
        else:
            return notification.workflow_id

    def on_workflow_notification(self, notification: WorkflowNotification):
        workflow_id = UUID(str(self._get_workflow_id_from_notification(notification)))

        # Add to the appropriate workflow's queue
        self.notification_queues[workflow_id].append(notification)

        # Wake up any waiter for this workflow
        waiter = self.waiters.get(workflow_id)
        if waiter is not None:
            waiter.set_result(None)
            del self.waiters[workflow_id]

    async def wait(
        self, kind: str, workflow_id: UUID, step_id: int | None = None
    ) -> WorkflowNotification:
        workflow_id = UUID(str(workflow_id))  # ensure workflow_id is an UUID instance

        while True:
            matched = None
            queue = self.notification_queues[workflow_id]
            for i, notification in enumerate(queue):
                if notification.kind == kind:
                    # Only check step_id filter for non-Workflow notifications
                    if isinstance(notification.data, WorkflowStep):
                        if step_id is not None and notification.data.step_id != step_id:
                            continue
                    matched = i
                    break
            if matched is not None:
                notification = queue[matched]
                # Prune all previous notifications from this workflow's queue
                self.notification_queues[workflow_id] = queue[matched + 1 :]
                return notification
            # notification hasn't arrived yet, lets create a future and sleep until
            # on_workflow_notification is called
            assert workflow_id not in self.waiters, (
                f"waiter for workflow {workflow_id} should not be present"
            )
            waiter = Future()
            self.waiters[workflow_id] = waiter
            try:
                await wait_for(waiter, timeout=self.timeout)
            except TimeoutError:
                assert False, (
                    f"Timeout waiting for notification {kind} with workflow_id={workflow_id} and step_id={step_id}"
                )
