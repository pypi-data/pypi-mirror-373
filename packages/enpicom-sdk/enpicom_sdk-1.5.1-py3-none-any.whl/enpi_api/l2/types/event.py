from datetime import datetime

from pydantic import BaseModel

from enpi_api.l2.types.organization import OrganizationId
from enpi_api.l2.types.user import UserId
from enpi_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId


class WorkflowExecutionPayload(BaseModel):
    """The payload of a WorkflowExecutionEvent."""

    id: WorkflowExecutionId
    """The ID of the workflow execution."""
    state: str
    """The state of the workflow execution."""
    archived: bool
    """Whether the workflow execution is archived."""


class WorkflowExecutionTaskPayload(BaseModel):
    """The payload of a WorkflowExecutionTaskEvent."""

    id: WorkflowExecutionTaskId
    """The ID of the workflow execution task."""
    workflow_execution_id: WorkflowExecutionId
    """The ID of the workflow execution."""
    task_template_name: str
    """The name of the job template."""
    state: str
    """The state of the workflow execution."""


class Event(BaseModel):
    """A single event body representing a single action that has happened in the Platform."""

    timestamp: datetime
    """The timestamp when the event was fired."""
    organization_id: OrganizationId
    """The organization that the event belongs to."""
    user_id: UserId
    """The user that the event belongs to, if any."""
    category: str
    """The category of the event."""
    action: str
    """The action that was performed."""
    payload: dict[str, int | float | bool | str | None] | WorkflowExecutionTaskPayload | WorkflowExecutionPayload
    """The payload of the event.

    The contents of the payload are specific to the event category and action, and may contain more detailed information
    about the event that occurred.
    """
