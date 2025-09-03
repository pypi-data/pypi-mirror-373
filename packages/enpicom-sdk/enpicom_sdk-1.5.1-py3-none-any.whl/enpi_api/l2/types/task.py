from enum import StrEnum
from typing import NewType

TaskId = NewType("TaskId", int)
"""The unique identifier of a task."""


class TaskState(StrEnum):
    """Current state of a task."""

    PENDING = "pending"
    WAITING = "waiting"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    CANCELLED = "cancelled"
    FAILED = "failed"
    TIMED_OUT = "timedOut"
    ERROR = "error"
    UNKNOWN = "unknown"
    OMITTED = "omitted"
    SKIPPED = "skipped"


END_STATES = {TaskState.SUCCEEDED, TaskState.CANCELLED, TaskState.FAILED, TaskState.TIMED_OUT, TaskState.ERROR, TaskState.OMITTED, TaskState.SKIPPED}
