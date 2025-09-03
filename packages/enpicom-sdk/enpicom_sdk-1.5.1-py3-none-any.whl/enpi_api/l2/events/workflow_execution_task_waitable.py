from threading import Lock
from time import sleep
from typing import Any, Callable, Generic, Optional, TypeVar

from enpi_api.l2.client.api.workflow_api import WorkflowApi
from enpi_api.l2.events.space_event_listener import SpaceEventListener
from enpi_api.l2.types.event import Event, WorkflowExecutionTaskPayload
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.types.task import END_STATES, TaskState
from enpi_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName
from enpi_api.l2.util.client import get_client
from loguru import logger
from pydantic import ValidationError

T = TypeVar("T")


class WorkflowExecutionTaskWaitManager:
    _instance = None
    _lock = Lock()
    _initialized: bool

    def __new__(cls) -> "WorkflowExecutionTaskWaitManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(WorkflowExecutionTaskWaitManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self.waitables: list["WorkflowExecutionTaskWaitable[Any]"] = []  # type: ignore[misc]
            self.listener = SpaceEventListener(on_event=self._on_event)
            self._running = False
            self._initialized = True

    def start_waiting(self) -> None:
        if not self._running:
            self._running = True
            self.listener.start_listening()
            self._wait_loop()

    def _wait_loop(self) -> None:
        i = 0
        while self.waitables:
            # Log every 10 seconds
            if i % 10 == 0:
                logger.info(f"Waiting for {len(self.waitables)} workflow execution task(s) to finish...")
            sleep(1)
            i += 1
        self._running = False
        self.listener.stop_listening()

    def register_waitable(self, waitable: "WorkflowExecutionTaskWaitable[T]") -> None:
        self.waitables.append(waitable)

    def _on_event(self, topic: str, event: Event) -> None:
        try:
            payload = WorkflowExecutionTaskPayload.model_validate(event.payload)
        except ValidationError:
            return

        self.waitables = [w for w in self.waitables if w.on_event(payload)]
        logger.info(f"Waiting for {len(self.waitables)} workflow execution task(s) to finish...")


class WorkflowExecutionTaskWaitable(Generic[T]):
    def __init__(
        self,
        workflow_execution_id: WorkflowExecutionId,
        task_template_name: WorkflowTaskTemplateName,
        on_complete: Optional[Callable[[WorkflowExecutionTaskId, TaskState], T]] | None = None,
    ) -> None:
        self.workflow_execution_id = workflow_execution_id
        self.task_template_name = task_template_name
        self.on_complete = on_complete

        self.waiting_for_workflow_execution_task = self.needs_to_wait_after_init()
        self.result: T | None = None

        if self.waiting_for_workflow_execution_task:
            self.manager = WorkflowExecutionTaskWaitManager()

    def on_event(self, payload: WorkflowExecutionTaskPayload) -> bool:
        if (
            payload.task_template_name == self.task_template_name
            and payload.workflow_execution_id == self.workflow_execution_id
            and (payload.state.lower() in END_STATES)
        ):
            logger.info(f"Workflow execution {self.workflow_execution_id} finished with state: {payload.state}")
            if self.on_complete:
                try:
                    self.result = self.on_complete(payload.id, TaskState(payload.state.lower()))
                except Exception as e:
                    # It should not re-raise to avoid waitables never stopping to wait
                    logger.error(f"Error in on_complete callback: {e}")

            self.waiting_for_workflow_execution_task = False

        return self.waiting_for_workflow_execution_task

    def needs_to_wait_after_init(self) -> bool:
        # First, poll the api once and make sure the workflow execution isn't already finished
        workflow_api = WorkflowApi(get_client(), log_level=LogLevel.Info)
        workflow_execution_task_states = workflow_api.get_workflow_execution_task_states(self.workflow_execution_id)
        for item in workflow_execution_task_states:
            if item.task_template_name == self.task_template_name and item.state in END_STATES:
                logger.info(f"Workflow execution task {item.task_template_name} finished with state: {item.state}")
                if self.on_complete:
                    self.result = self.on_complete(item.task_id, item.state)
                return False

        return True

    def wait(self) -> None:
        self.waiting_for_workflow_execution_task = self.needs_to_wait_after_init()
        if self.waiting_for_workflow_execution_task:
            self.manager.register_waitable(self)
            self.manager.start_waiting()

    def wait_and_return_result(self) -> T:
        self.wait()
        assert self.result is not None
        return self.result

    def check_execution_state(self) -> TaskState:
        workflow_api = WorkflowApi(get_client(), log_level=LogLevel.Info)
        return workflow_api.get_workflow_execution_state(self.workflow_execution_id)
