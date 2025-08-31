from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel, Field
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from planar.human.human import (
    Human,
    HumanTask,
    HumanTaskStatus,
    Timeout,
    complete_human_task,
)
from planar.workflows import suspend
from planar.workflows.decorators import workflow
from planar.workflows.execution import execute
from planar.workflows.models import StepType, Workflow, WorkflowStatus, WorkflowStep
from planar.workflows.step_core import Suspend


# Test data models
class ExpenseRequest(BaseModel):
    """An expense request submitted by an employee."""

    request_id: str = Field(description="Unique identifier for the request")
    amount: float = Field(description="Amount requested in dollars")
    requester: str = Field(description="Name of the person requesting")
    department: str = Field(description="Department the requester belongs to")
    purpose: str = Field(description="Purpose of the expense")


class ExpenseDecision(BaseModel):
    """A decision made by a human approver on an expense request."""

    approved: bool = Field(description="Whether the expense is approved")
    approved_amount: float = Field(
        description="Amount approved (may be less than requested)"
    )
    notes: str = Field(description="Explanation for decision", default="")


class HumanResponse(BaseModel):
    response: str = Field(description="A message from the human")


@pytest.fixture
def expense_approval():
    """Returns a Human task definition for expense approval testing."""
    return Human(
        name="expense_approval",
        title="Expense Approval",
        description="Review expense request and approve, adjust, or reject",
        input_type=ExpenseRequest,
        output_type=ExpenseDecision,
        timeout=Timeout(timedelta(hours=24)),
    )


@pytest.fixture
def expense_approval_no_input():
    """Returns a Human task definition for expense approval testing."""
    return Human(
        name="expense_approval_no_input",
        title="Expense Approval (No Input)",
        description="Review expense request and approve, adjust, or reject",
        output_type=ExpenseDecision,
        timeout=Timeout(timedelta(hours=24)),
    )


# Create a fixture for sample expense request data
@pytest.fixture
def expense_request_data():
    """Returns sample expense request data for testing."""
    return {
        "request_id": "EXP-123",
        "amount": 750.00,
        "requester": "Jane Smith",
        "department": "Engineering",
        "purpose": "Conference travel expenses",
    }


async def test_human_initialization():
    """Test that the Human class initializes with correct parameters."""
    human = Human(
        name="test_human",
        title="Test Human Task",
        output_type=ExpenseDecision,
        description="Test description",
        input_type=ExpenseRequest,
        timeout=Timeout(timedelta(hours=1)),
    )

    # Verify initialization
    assert human.name == "test_human"
    assert human.title == "Test Human Task"
    assert human.description == "Test description"
    assert human.input_type == ExpenseRequest
    assert human.output_type == ExpenseDecision
    assert human.timeout is not None
    assert human.timeout.get_seconds() == 3600  # 1 hour in seconds


async def test_human_initialization_validation():
    """Test that the Human class validates output_type is a Pydantic model."""
    with pytest.raises(ValueError, match="output_type must be a Pydantic model"):
        Human(
            name="test_human",
            title="Test Human Task",
            # Invalid: not a Pydantic model
            output_type=str,  # type: ignore
        )


async def test_human_initialization_validation_no_input(session: AsyncSession):
    human_no_input = Human(
        name="test_human",
        title="Test Human Task",
        output_type=HumanResponse,
    )

    @workflow()
    async def expense_workflow():
        result = await human_no_input(message="Hello, world!")
        return result.output.response

    wf = await expense_workflow.start()
    result = await execute(wf)
    assert isinstance(result, Suspend)

    steps = (
        await session.exec(select(WorkflowStep).order_by(col(WorkflowStep.step_id)))
    ).all()
    assert len(steps) == 3
    assert "Create Human Task" in [s.display_name for s in steps]
    assert "Wait for event" in [s.display_name for s in steps]

    assert StepType.HUMAN_IN_THE_LOOP in [s.step_type for s in steps]
    assert steps[0].args == [None, "Hello, world!", None]

    # Get HumanTask from database
    human_task = (await session.exec(select(HumanTask))).one()
    assert human_task is not None
    assert human_task.name == "test_human"
    assert human_task.title == "Test Human Task"
    assert human_task.output_schema == HumanResponse.model_json_schema()
    assert human_task.input_schema is None
    assert human_task.message == "Hello, world!"

    await complete_human_task(human_task.id, {"response": "Approved"})
    result = await execute(wf)
    assert result == "Approved"


async def test_human_basic_workflow(
    session: AsyncSession, expense_approval, expense_request_data
):
    """Test that a Human step can be used in a workflow with input data."""

    @workflow()
    async def expense_workflow(request_data: dict):
        request = ExpenseRequest(**request_data)
        result = await expense_approval(request)
        # Add a suspend to ensure the workflow correctly
        # deserializes the result of human task on subsequent executions
        await suspend(interval=timedelta(seconds=0))
        return {
            "request_id": request.request_id,
            "approved": result.output.approved,
            "amount": result.output.approved_amount,
            "notes": result.output.notes,
        }

    # Start the workflow and run until it suspends
    wf = await expense_workflow.start(expense_request_data)
    result = await execute(wf)
    assert isinstance(result, Suspend)

    # Query workflows and steps from the database
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf is not None
    assert updated_wf.status == WorkflowStatus.PENDING
    assert updated_wf.waiting_for_event is not None
    assert "human_task_completed:" in updated_wf.waiting_for_event

    steps = (
        await session.exec(select(WorkflowStep).order_by(col(WorkflowStep.step_id)))
    ).all()
    assert len(steps) == 4
    assert "expense_approval" in [s.display_name for s in steps]

    # Get HumanTask from database and verify fields
    human_task = (await session.exec(select(HumanTask))).one()
    assert human_task is not None
    assert human_task.name == "expense_approval"
    assert human_task.title == "Expense Approval"
    assert human_task.workflow_id == wf.id
    assert human_task.status == HumanTaskStatus.PENDING
    assert human_task.input_schema == ExpenseRequest.model_json_schema()
    assert human_task.input_data is not None
    assert human_task.input_data["request_id"] == "EXP-123"
    assert human_task.input_data["amount"] == 750.00
    assert human_task.message is None
    assert human_task.output_schema == ExpenseDecision.model_json_schema()
    assert human_task.output_data is None

    # Complete the human task
    output_data = {
        "approved": True,
        "approved_amount": 700.00,
        "notes": "Approved with reduced amount",
    }
    await complete_human_task(human_task.id, output_data, completed_by="test_user")

    # Check the human task was updated correctly
    await session.refresh(human_task)
    assert human_task.status == HumanTaskStatus.COMPLETED
    assert human_task.output_data == output_data
    assert human_task.completed_by == "test_user"
    assert human_task.completed_at is not None

    # Resume and complete the workflow
    result = await execute(wf)
    assert isinstance(result, Suspend)
    result = await execute(wf)

    # Verify workflow completed successfully with expected result
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf is not None
    assert updated_wf.status == WorkflowStatus.SUCCEEDED
    expected_result = {
        "request_id": expense_request_data["request_id"],
        "approved": output_data["approved"],
        "amount": output_data["approved_amount"],
        "notes": output_data["notes"],
    }
    assert updated_wf.result == expected_result


async def test_human_task_completion_validation(session: AsyncSession):
    """Test validation when completing a human task."""

    workflow = Workflow(
        function_name="test_workflow",
        status=WorkflowStatus.PENDING,
        args=[],
        kwargs={},
    )
    session.add(workflow)
    await session.commit()
    # Create a human task
    task = HumanTask(
        id=uuid4(),
        name="test_task",
        title="Test Task",
        workflow_id=workflow.id,
        workflow_name="test_workflow",
        output_schema=ExpenseDecision.model_json_schema(),
        status=HumanTaskStatus.PENDING,
    )

    session.add(task)
    await session.commit()
    task_id = task.id

    # Test completing a non-existent task
    with pytest.raises(ValueError, match="not found"):
        await complete_human_task(UUID("00000000-0000-0000-0000-000000000000"), {})

    # Test completing a task that's not in pending state
    task.status = HumanTaskStatus.CANCELLED
    session.add(task)
    await session.commit()

    with pytest.raises(ValueError, match="not pending"):
        await complete_human_task(task_id, {})

    # Reset to pending for the next test
    task.status = HumanTaskStatus.PENDING
    session.add(task)
    await session.commit()

    # Mock emit_event for normal completion test
    with patch("planar.workflows.events.emit_event", AsyncMock()):
        # Complete with valid data
        output_data = {
            "approved": True,
            "approved_amount": 150.00,
            "notes": "Approved",
        }

        await complete_human_task(task_id, output_data)

        # Verify task state
        await session.refresh(task)
        assert task.status == HumanTaskStatus.COMPLETED
        assert task.output_data == output_data


async def test_timeout_class():
    """Test the Timeout helper class functionality."""
    # Test with various durations
    one_hour = Timeout(timedelta(hours=1))
    assert one_hour.get_seconds() == 3600
    assert one_hour.get_timedelta() == timedelta(hours=1)

    five_minutes = Timeout(timedelta(minutes=5))
    assert five_minutes.get_seconds() == 300
    assert five_minutes.get_timedelta() == timedelta(minutes=5)


async def test_human_task_with_suggested_data(session: AsyncSession):
    """Test that a Human step can be used with suggested_data."""
    human_with_suggestions = Human(
        name="test_human_suggestions",
        title="Test Human Task with Suggestions",
        output_type=ExpenseDecision,
    )

    @workflow()
    async def expense_workflow():
        result = await human_with_suggestions(
            message="Please review the expense",
            suggested_data=ExpenseDecision(
                approved=True,
                approved_amount=500.0,
                notes="Pre-approved amount",
            ),
        )
        return result.output.notes

    wf = await expense_workflow.start()
    result = await execute(wf)
    assert isinstance(result, Suspend)

    # Get HumanTask from database and verify suggested_data is stored
    human_task = (await session.exec(select(HumanTask))).one()
    assert human_task is not None
    assert human_task.name == "test_human_suggestions"
    assert human_task.suggested_data is not None
    assert human_task.suggested_data["approved"] is True
    assert human_task.suggested_data["approved_amount"] == 500.0
    assert human_task.suggested_data["notes"] == "Pre-approved amount"

    # Complete the human task
    await complete_human_task(
        human_task.id,
        {"approved": False, "approved_amount": 0.0, "notes": "Rejected after review"},
    )

    result = await execute(wf)
    assert result == "Rejected after review"


async def test_deadline_calculation():
    """Test that deadlines are calculated correctly based on timeout."""
    # Create a human task with a deadline
    with patch("planar.human.human.utc_now") as mock_datetime:
        # Mock the current time
        now = datetime(2025, 1, 1, 12, 0, 0)
        mock_datetime.return_value = now

        # Calculate deadlines with different timeouts
        one_hour_timeout = Human(
            name="one_hour",
            title="One Hour Timeout",
            output_type=ExpenseDecision,
            timeout=Timeout(timedelta(hours=1)),
        )

        deadline = one_hour_timeout._calculate_deadline()
        assert deadline == datetime(2025, 1, 1, 13, 0, 0)

        # Test with no timeout
        no_timeout = Human(
            name="no_timeout",
            title="No Timeout",
            output_type=ExpenseDecision,
        )

        assert no_timeout._calculate_deadline() is None
