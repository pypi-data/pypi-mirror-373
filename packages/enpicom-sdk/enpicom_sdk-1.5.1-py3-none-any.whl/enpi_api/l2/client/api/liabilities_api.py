from loguru import logger

from enpi_api.l1 import openapi_client
from enpi_api.l2.events.workflow_execution_task_waitable import WorkflowExecutionTaskWaitable
from enpi_api.l2.types.api_error import ApiError
from enpi_api.l2.types.clone import CloneId
from enpi_api.l2.types.execution import Execution
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.types.sequence import SequenceId
from enpi_api.l2.types.task import TaskState
from enpi_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName


class LiabilitiesApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def start(
        self,
        clone_ids: list[CloneId] | None = None,
        sequence_ids: list[SequenceId] | None = None,
    ) -> Execution[WorkflowExecutionTaskId]:
        """Run liabilities computation on a set of target clones.

        This will compute liabilities for clones matched with clone and sequence IDs passed
        to the function and will add new tags to those clones if computations are successful.

        > This functionality uses clone resolving.\n
        > Clone resolving uses passed clone and sequence IDs in order to resolve clones.
        > For each clone, a maximum of one *big* chain and one *small* chain sequence will be picked, resulting in a
        maximum of two sequences per clone.
        > Sequences matched with passed sequence IDs have priority over internally resolved sequences, meaning that if
        possible, they will be picked as sequences for the resolved clones.

        Args:
            clone_ids (list[enpi_api.l2.types.clone.CloneId]): IDs of clones based on which clones will be
                resolved and passed for liabilities computation.
            sequence_ids (list[enpi_api.l2.types.sequence.SequenceId]): IDs of sequences based on which clones will be
                resolved and passed for liabilities computation. If clone resolving based on clone IDs and sequence IDs results in the same,
                "overlapping" clones (with the same clone IDs) but potentially different sequences within, clones resolved with use of sequence IDs
                will be picked over the ones resolved with clone IDs.

        Returns:
            enpi_api.l2.types.execution.Execution[None]: An awaitable.

        Raises:
            ValueError: If clone and/or sequence IDs passed to this function are empty or invalid.
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            ```
            collection_id = CollectionId(1234)

            # Get all clones belonging to a collection
            collection_filter = client.filter_api.create_filter(name="test_collection", condition=MatchId(target=MatchIdTarget.COLLECTION, id=collection_id))
            clones_df = client.collection_api.get_as_df(
                collection_ids=[collection_id],
                filter=collection_filter,
                tag_ids=[],
            ).wait()

            # Extract clone ids from the dataframe
            clone_ids = [CloneId(id) for id in clones_df.index.tolist()]

            # Run liabilities computation
            client.liabilities_api.start(clone_ids=clone_ids).wait()

            # Get clones updated with new tags, result of liabilities computation
            updated_clones_df = client.collection_api.get_as_df(
                collection_ids=[collection_id],
                filter=collection_filter,
                tag_ids=[
                    CloneTags.TapScore # Tag added during liabilities run
                ],
            ).wait()
            ```
        """
        liabilities_api_instance = openapi_client.LiabilitiesApi(self._inner_api_client)

        # Check if we got any ids to work with
        if (clone_ids is None or len(clone_ids) == 0) and (sequence_ids is None or len(sequence_ids) == 0):
            raise ValueError("Both clone and sequence IDs arrays are null, at least one of them needs to contain proper values.")

        # Validate if ID types are right
        if clone_ids is not None and not all([isinstance(id, str) for id in clone_ids]):
            raise ValueError("Some of the passed clone IDs are not strings.")
        elif sequence_ids is not None and not all([isinstance(id, int) for id in sequence_ids]):
            raise ValueError("Some of the passed sequence IDs are not integers.")

        try:
            liabilities_work = openapi_client.LiabilitiesWork(
                clone_ids=None if clone_ids is None else [str(id) for id in clone_ids],
                sequence_ids=None if sequence_ids is None else [int(id) for id in sequence_ids],
            )
            logger.info("Making a request for liabilities computation run start...")
            data = liabilities_api_instance.start_liabilities(liabilities_work=liabilities_work)
            assert data.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(int(data.workflow_execution_id))

            def on_complete(task_id: WorkflowExecutionTaskId, task_state: TaskState) -> WorkflowExecutionTaskId:
                logger.success(f"Liabilities task ID: {task_id} in workflow execution with ID: {workflow_execution_id} has successfully finished.")

                return task_id

            waitable = WorkflowExecutionTaskWaitable[WorkflowExecutionTaskId](
                workflow_execution_id=workflow_execution_id, task_template_name=WorkflowTaskTemplateName.ENPI_APP_LIABILITIES, on_complete=on_complete
            )
            return Execution(wait=waitable.wait_and_return_result, check_execution_state=waitable.check_execution_state)
        except openapi_client.ApiException as e:
            raise ApiError(e)
