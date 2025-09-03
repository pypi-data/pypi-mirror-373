from pathlib import Path

import pandas as pd
from loguru import logger

from enpi_api.l1 import openapi_client
from enpi_api.l2.client.api.file_api import FileApi
from enpi_api.l2.events.workflow_execution_task_waitable import WorkflowExecutionTaskWaitable
from enpi_api.l2.types.api_error import ApiError, ApiErrorContext
from enpi_api.l2.types.cluster import ClusterId, ClusterRunId
from enpi_api.l2.types.execution import Execution
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.types.phylogeny import Phylogeny
from enpi_api.l2.types.task import TaskState
from enpi_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName


class PhylogenyApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_phylogeny_by_task_id(self, task_id: WorkflowExecutionTaskId) -> list[Phylogeny]:
        """Get the calculated trees for a phylogenetic calculation.

        Args:
            task_id (enpi_api.l2.types.task.TaskId): The phylogeny task id

        Returns:
            list[enpi_api.l2.types.phylogeny.Phylogeny]: The calculated trees.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
                task_id = TaskId(456)
                phylogeny = self.get_phylogeny_by_task_id(task_id=task_id)
            ```
        """

        phylogeny_api_instance = openapi_client.PhylogenyApi(self._inner_api_client)

        try:
            return [Phylogeny.from_raw(i) for i in phylogeny_api_instance.get_phylogeny_by_task_id(task_id=task_id).phylogeny]
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def start(self, cluster_run_id: ClusterRunId, cluster_id: ClusterId) -> Execution[list[Phylogeny]]:
        """Start the calculation of phylogenetic trees for a specified cluster.

        Args:
            cluster_run_id (enpi_api.l2.types.cluster.ClusterRunId): The unique identifier of the cluster run.
            cluster_id (enpi_api.l2.types.cluster.ClusterId): The unique identifier of the cluster.

        Returns:
            enpi_api.l2.types.execution.Execution[list[enpi_api.l2.types.phylogeny.Phylogeny]]: An awaitable that returns the calculated trees.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
                cluster_run_id = ClusterRunId("b35a7864-0887-44e5-896a-feffdcc9d022")
                cluster_id = ClusterId(123)
                phylogeny = client.phylogeny_api.start(cluster_run_id=cluster_run_id, cluster_id=cluster_id).wait()
            ```
        """

        phylogeny_api_instance = openapi_client.PhylogenyApi(self._inner_api_client)

        try:
            phylogeny_work = openapi_client.PhylogenyWork(cluster_run_id=cluster_run_id, cluster_id=cluster_id)
            data = phylogeny_api_instance.start_phylogeny(phylogeny_work)

            assert data.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(int(data.workflow_execution_id))

            def on_complete(task_id: WorkflowExecutionTaskId, task_state: TaskState) -> list[Phylogeny]:
                phylogeny: list[Phylogeny] = self.get_phylogeny_by_task_id(task_id=task_id)

                logger.success(f"Phylogeny compute with task ID: {task_id} in workflow execution with ID: {workflow_execution_id} has successfully finished.")

                return phylogeny

            waitable = WorkflowExecutionTaskWaitable[list[Phylogeny]](
                workflow_execution_id=workflow_execution_id, task_template_name=WorkflowTaskTemplateName.ENPI_APP_PHYLOGENY, on_complete=on_complete
            )
            return Execution(wait=waitable.wait_and_return_result, check_execution_state=waitable.check_execution_state)
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def export_phylogeny_as_tsv(self, phylogeny: Phylogeny, output_directory: str | Path | None = None) -> Execution[Path]:
        """Export the sequences of the specified tree into a TSV file and download it to the specified directory.

        Args:
            phylogeny (enpi_api.l2.types.phylogeny.Phylogeny): The phylogenetic tree to export.
            output_directory (str | Path | None): The directory where to download the TSV file. Defaults to a
              unique temporary directory.

        Returns:
            enpi_api.l2.types.execution.Execution[Path]: An awaitable that returns the path to the downloaded TSV file containing the sequences.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            # Assuming phylogenetic trees were computed and fetched already
            trees = ...

            # Export the sequences of the Amino Acid tree
            amino_acid_tree: Phylogeny = next(tree for tree in trees if tree.type == PhylogenyType.AMINO_ACID)

            # Export the phylogenentic tree as a TSV file
            logger.info("Exporting the phylogenentic tree as a TSV file")
            phylogeny_tsv_path: Path = enpi_client.phylogeny_api.export_phylogeny_as_tsv(
                phylogeny=amino_acid_tree,
            ).wait()
            ```
        """

        phylogeny_api_instance = openapi_client.PhylogenyApi(self._inner_api_client)

        with ApiErrorContext():
            export_request = openapi_client.StartPhylogenyExportRequest(tree_id=phylogeny.tree_id)
            export_job = phylogeny_api_instance.start_phylogeny_export(export_request)
            assert export_job.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(export_job.workflow_execution_id)

            def on_complete(task_id: WorkflowExecutionTaskId, task_state: TaskState) -> Path:
                file_api = FileApi(self._inner_api_client, self._log_level)
                file_path = file_api.download_export_by_workflow_execution_task_id(task_id=task_id, output_directory=output_directory)

                return file_path

            waitable = WorkflowExecutionTaskWaitable[Path](
                workflow_execution_id=workflow_execution_id, on_complete=on_complete, task_template_name=WorkflowTaskTemplateName.ENPI_APP_PHYLOGENY_EXPORT
            )
            return Execution(wait=waitable.wait_and_return_result, check_execution_state=waitable.check_execution_state)

    def export_phylogeny_as_df(self, phylogeny: Phylogeny) -> Execution[pd.DataFrame]:
        """Export the sequences of the specified phylogeny into a pandas DataFrame.

        Args:
            phylogeny (enpi_api.l2.types.phylogeny.Phylogeny): The phylogenetic tree to export.

        Returns:
            enpi_api.l2.types.execution.Execution[pd.DataFrame]: An awaitable that returns a pandas DataFrame containing the sequences.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            # Assuming trees were computed and fetched already
            trees = ...

            # Export the sequences of the Amino Acid tree
            amino_acid_tree: Phylogeny = next(tree for tree in trees if tree.type == PhylogenyType.AMINO_ACID)

            # Export the phylogenetic tree as a Pandas DataFrame
            tree_df: pd.DataFrame = enpi_client.phylogeny_api.export_phylogeny_as_df(
                tree=amino_acid_tree,
            ).wait()
        ```
        """

        export_tsv = self.export_phylogeny_as_tsv(phylogeny)

        def wait() -> pd.DataFrame:
            tsv_path = export_tsv.wait()
            return pd.read_csv(tsv_path, sep="\t")

        return Execution(wait=wait, check_execution_state=export_tsv.check_execution_state)
