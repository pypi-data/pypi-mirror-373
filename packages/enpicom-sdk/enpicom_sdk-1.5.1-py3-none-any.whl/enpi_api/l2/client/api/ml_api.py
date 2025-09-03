from typing import Union

from loguru import logger

from enpi_api.l1 import openapi_client
from enpi_api.l2.events.workflow_execution_task_waitable import WorkflowExecutionTaskWaitable
from enpi_api.l2.events.workflow_execution_waitable import WorkflowExecutionWaitable
from enpi_api.l2.types.api_error import ApiError, ApiErrorContext
from enpi_api.l2.types.clone import CloneId
from enpi_api.l2.types.collection import CollectionId
from enpi_api.l2.types.execution import Execution
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.types.ml import (
    MlAwsEndpointConfig,
    MlEndpoint,
    MlEndpointId,
    MlEndpointSignature,
    MlflowModelUri,
    MlInputMapItem,
    MlInvocationId,
    MlInvocationStats,
    MlOutputIntent,
    MlParamMapItem,
)
from enpi_api.l2.types.task import TaskState
from enpi_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName


class InvocationFailed(Exception):
    """Indicates that the ML invocation has failed."""

    def __init__(self, invocation_id: MlInvocationId):
        """@private"""
        super().__init__(f"ML invocation with ID `{invocation_id}` failed")


class DeploymentFailed(Exception):
    """Indicates that the ML deployment has failed."""

    def __init__(self, workflow_execution_task_id: WorkflowExecutionTaskId):
        """@private"""
        super().__init__(f"ML deployment task with ID `{workflow_execution_task_id}` failed")


class MlApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_ml_endpoints(self) -> list[MlEndpoint]:
        """Get all ML endpoints.

        Returns:
            list[enpi_api.l2.types.ml.MlEndpoint]: A list of ML endpoints.
        """

        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        try:
            return [MlEndpoint.from_raw(i) for i in ml_api_instance.get_ml_endpoints().ml_endpoints]
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def get_ml_invocation_stats(self) -> list[MlInvocationStats]:
        """Get ML invocation statistics.

        Returns:
            list[enpi_api.l2.types.ml.MlInvocationStats]: A list of ML invocation statistics.
        """
        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        try:
            stats = ml_api_instance.get_ml_invocation_stats().stats
            return [MlInvocationStats.from_raw(i) for i in stats]
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def register_ml_endpoint(
        self,
        display_name: str,
        input_mapping: list[MlInputMapItem],
        output_intents: list[MlOutputIntent],
        vendor_config: MlAwsEndpointConfig,
        signatures: list[MlEndpointSignature],
        parameter_mapping: list[MlParamMapItem] | None = None,
    ) -> MlEndpointId:
        """Register a ML endpoint.

        Args:
            display_name (str): The display name of the ML endpoint.
            input_mapping (list[MlInputMapItem]): The input mapping of the ML endpoint.
            output_intents (list[MlOutputIntent]): The output intents of the ML endpoint.
            vendor_config (MlAwsEndpointConfig): The AWS endpoint configuration of the ML endpoint.
            signatures (list[MlEndpointSignature]): The signatures of the ML endpoint.
            parameter_mapping (list[MlParamMapItem] | None): The parameter mapping of the ML endpoint.

        Returns:
            endpoint_id (str): The unique identifier of a ML endpoint.
        """

        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        try:
            parameter_mapping_items = (
                [
                    openapi_client.MlParameterMapItem.model_validate(
                        {
                            "type": pm["type"],
                            "input_key": pm["input_key"],
                            "label": pm["label"] if "label" in pm and pm["label"] is not None else None,
                            "source": "parameter",
                        }
                    )
                    for pm in parameter_mapping
                ]
                if parameter_mapping is not None
                else None
            )

            result = ml_api_instance.register_ml_endpoint(
                register_ml_endpoint_request=openapi_client.RegisterMlEndpointRequest(
                    display_name=display_name,
                    input_mapping=[openapi_client.MlInputMapItem.model_validate(i) for i in input_mapping],
                    parameter_mapping=parameter_mapping_items,
                    output_intents=[openapi_client.MlOutputIntent.from_dict(dict(i)) for i in output_intents],
                    vendor_config=openapi_client.MlAwsEndpointConfig.from_dict(
                        {**vendor_config, "region": vendor_config.get("region", "eu-west-1"), "endpoint_type": "external"}
                    ),
                    signatures=[openapi_client.MlEndpointSignature.model_validate(i) for i in signatures],
                )
            )
            return MlEndpointId(result.endpoint_id)
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def unregister_ml_endpoint(self, endpoint_id: MlEndpointId) -> None:
        """Unregister a ML endpoint.

        Args:
            endpoint_id (MlEndpointId): The unique identifier of a ML endpoint.
        """

        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        try:
            ml_api_instance.unregister_ml_endpoint(id=endpoint_id)
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def deploy_model(
        self,
        display_name: str,
        input_mapping: list[MlInputMapItem],
        output_intents: list[MlOutputIntent],
        model_uri: MlflowModelUri,
        signatures: list[MlEndpointSignature],
        parameter_mapping: list[MlParamMapItem] | None = None,
    ) -> Execution[MlEndpointId]:
        """Deploy a model from ML flow as a SageMaker model with an endpoint.

        Args:
            display_name (str): The display name of the ML endpoint.
            input_mapping (list[MlInputMapItem]): The input mapping of the ML endpoint.
            output_intents (list[MlOutputIntent]): The output intents of the ML endpoint.
            model_uri (MlFlowModelUri): The URI of a MLflow model.
            parameter_mapping (list[MlParamMapItem] | None): The parameter mapping of the ML endpoint.
        """
        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        parameter_mapping_items = (
            [
                openapi_client.MlParameterMapItem.model_validate(
                    {
                        "type": pm["type"],
                        "input_key": pm["input_key"],
                        "label": pm["label"] if "label" in pm and pm["label"] is not None else None,
                        "source": "parameter",
                    }
                )
                for pm in parameter_mapping
            ]
            if parameter_mapping is not None
            else None
        )

        payload = openapi_client.DeployModelRequest(
            display_name=display_name,
            parameter_mapping=parameter_mapping_items,
            input_mapping=[openapi_client.MlInputMapItem.model_validate(i) for i in input_mapping],
            output_intents=[openapi_client.MlOutputIntent.from_dict(dict(i)) for i in output_intents],
            model_uri=model_uri,
            signatures=[openapi_client.MlEndpointSignature.model_validate(i) for i in signatures],
        )

        with ApiErrorContext():
            deploy_model_response = ml_api_instance.deploy_model(deploy_model_request=payload)
            assert deploy_model_response.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(int(deploy_model_response.workflow_execution_id))

            def on_complete(task_id: WorkflowExecutionTaskId, task_state: TaskState) -> MlEndpointId:
                # If the task has succeeded, return the endpoint_id
                match task_state:
                    case TaskState.SUCCEEDED:
                        result = ml_api_instance.get_endpoint_by_workflow_execution_task_id(workflow_execution_task_id=task_id)
                        return MlEndpointId(result.endpoint_id)
                    case _:
                        raise DeploymentFailed(task_id)

            waitable = WorkflowExecutionTaskWaitable[MlEndpointId](
                workflow_execution_id=workflow_execution_id, task_template_name=WorkflowTaskTemplateName.ENPI_APP_ML_ENDPOINT_DEPLOY, on_complete=on_complete
            )

            return Execution(wait=waitable.wait_and_return_result, check_execution_state=waitable.check_execution_state)

    def undeploy_model(self, endpoint_id: MlEndpointId) -> None:
        """Remove a SageMaker model and endpoint.

        Args:
            endpoint_id (MlEndpointId): The unique identifier of a ML endpoint.
        """
        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        try:
            ml_api_instance.undeploy_model(id=endpoint_id)
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def invoke_endpoint(
        self,
        endpoint_id: MlEndpointId,
        clone_ids: list[CloneId] | None = None,
        collection_ids: list[CollectionId] | None = None,
        parameters: dict[str, Union[str, int, float, bool]] | None = None,
    ) -> Execution[None]:
        """Invoke a ML endpoint.

        Args:
            endpoint_id (MlEndpointId): The unique identifier of a ML endpoint.
            clone_ids (list[CloneId]): The unique identifiers of the clones.
            parameters (dict | None): parameters passed to the invocation.

        Returns:
            output_key (MlInvocationOutputKey): The output key of a ML invocation.
            invocation_id (MlInvocationId): The unique identifier of a ML invocation.
        """
        ml_api_instance = openapi_client.MlApi(self._inner_api_client)
        if clone_ids is not None and collection_ids is not None:
            raise ValueError("Either clone_ids or collection_ids must be provided, but not both")

        with ApiErrorContext():
            result = ml_api_instance.invoke_endpoint(
                id=endpoint_id,
                invoke_ml_endpoint_request=openapi_client.InvokeMlEndpointRequest.from_dict(
                    dict(clone_ids=clone_ids, collection_ids=collection_ids, parameters=parameters)
                ),
            )
            assert result.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(result.workflow_execution_id)

            def on_complete(workflow_execution_id: WorkflowExecutionId, execution_state: TaskState) -> None:
                assert (
                    execution_state == TaskState.SUCCEEDED
                ), f"Workflow execution {workflow_execution_id} did not reach {TaskState.SUCCEEDED} state, got {execution_state} state instead"

                logger.success(f"Ml invocation with workflow execution ID: {workflow_execution_id} has successfully finished.")
                return

            waitable = WorkflowExecutionWaitable(
                workflow_execution_id=workflow_execution_id,
                on_complete=on_complete,
            )
            return Execution(wait=waitable.wait, check_execution_state=waitable.check_execution_state)
