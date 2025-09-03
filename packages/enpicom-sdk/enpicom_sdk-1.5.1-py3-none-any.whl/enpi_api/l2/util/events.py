from loguru import logger

from enpi_api.l2.types.event import Event
from enpi_api.l2.types.task import TaskId, TaskState


def job_is_finished(event: Event, task_id: TaskId) -> bool:
    if event.payload:
        running_job_id = dict(event.payload).get("job_id")
        state = str(dict(event.payload).get("state")).lower()
        if running_job_id == task_id and (state == TaskState.SUCCEEDED or state == TaskState.FAILED):
            logger.info(f"Job {task_id} finished with state: {state}")
            return True
    return False
