from enpi_api.l1 import openapi_client
from enpi_api.l2.types.api_error import ApiError
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.types.task import TaskState
from enpi_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTask


class WorkflowApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_workflow_execution_task_states(self, workflow_execution_id: WorkflowExecutionId) -> list[WorkflowExecutionTask]:
        """Get workflow execution task states by ID.

        Returns:
            enpi_api.l2.types.workflow.WorkflowExecution: The workflow execution.
        """
        workflow_api_instance = openapi_client.WorkflowApi(self._inner_api_client)

        try:
            response = workflow_api_instance.get_workflow_execution_task_states(workflow_execution_id)
        except openapi_client.ApiException as e:
            raise ApiError(e)

        return [WorkflowExecutionTask.from_raw(i) for i in response.workflow_execution_task_states]

    def get_workflow_execution_state(self, workflow_execution_id: WorkflowExecutionId) -> TaskState:
        """Get workflow execution state by ID.

        Returns:
            enpi_api.l2.types.task.TaskState
        """

        workflow_api_instance = openapi_client.WorkflowApi(self._inner_api_client)

        try:
            response = workflow_api_instance.get_workflow_execution_state(workflow_execution_id)
        except openapi_client.ApiException as e:
            raise ApiError(e)

        return TaskState(response.workflow_execution_state.lower())
