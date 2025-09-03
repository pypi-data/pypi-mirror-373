import os
import zipfile
from pathlib import Path

import pandas as pd
from loguru import logger

from enpi_api.l1 import openapi_client
from enpi_api.l2.client.api.file_api import FileApi
from enpi_api.l2.events.workflow_execution_task_waitable import WorkflowExecutionTaskWaitable
from enpi_api.l2.types.api_error import ApiErrorContext
from enpi_api.l2.types.cluster import ClusterRunId
from enpi_api.l2.types.enrichment import (
    EnrichmentExportMode,
    EnrichmentRun,
    EnrichmentRunId,
    EnrichmentTemplate,
    EnrichmentTemplateId,
    EnrichmentTemplateOperation,
    EnrichmentWorkInput,
    SimplifiedEnrichmentTemplate,
    transform_operation,
    transform_operation_input,
)
from enpi_api.l2.types.execution import Execution
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.types.tag import TagId
from enpi_api.l2.types.task import TaskState
from enpi_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName
from enpi_api.l2.util.file import unique_temp_dir


class EnrichmentApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_runs(
        self,
    ) -> list[EnrichmentRun]:
        """Get all successful Enrichment Runs.

        Returns:
            list[enpi_api.l2.types.enrichment.EnrichmentRun]: List of Enrichment Runs.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with EnpiApiClient() as enpi_client:
                enrichment_runs = enpi_client.enrichment_api.get_runs()
            ```
        """
        enrichment_api_instance = openapi_client.EnrichmentApi(self._inner_api_client)

        with ApiErrorContext():
            data = enrichment_api_instance.get_enrichment_runs()

        return [EnrichmentRun.from_raw(cr) for cr in data.runs]

    def get_run(self, enrichment_run_id: EnrichmentRunId) -> EnrichmentRun:
        """Get a single Enrichment Run by its ID.

        Args:
            enrichment_run_id (enpi_api.l2.types.enrichment.EnrichmentRunId): ID of the Enrichment run to get.

        Returns:
            enpi_api.l2.types.enrichment.EnrichmentRun: A successful Enrichment Run.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with EnpiApiClient() as enpi_client:
                enrichment_run = enpi_client.enrichment_api.get_run(EnrichmentRunId(123))
            ```
        """
        enrichment_api_instance = openapi_client.EnrichmentApi(self._inner_api_client)

        with ApiErrorContext():
            data = enrichment_api_instance.get_enrichment_run(int(enrichment_run_id))

        return EnrichmentRun.from_raw(data.run)

    def get_run_by_task_id(self, task_id: WorkflowExecutionTaskId) -> EnrichmentRun:
        """Get a single Enrichment Run by its task ID.

        Args:
            task_id (enpi_api.l2.types.task.TaskId): ID of a task linked to a successful Enrichment Run.

        Returns:
            enpi_api.l2.types.enrichment.EnrichmentRun: Successful Enrichment Run linked to the provided task ID.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Fetch a Enrichment Run

            ```python
            with EnpiApiClient() as enpi_client:
                enrichment_run = enpi_client.enrichment_api.get_run_by_task_id(TaskId(1234))
            ```
        """
        enrichment_api_instance = openapi_client.EnrichmentApi(self._inner_api_client)

        with ApiErrorContext():
            data = enrichment_api_instance.get_enrichment_run_by_task_id(task_id)

        return EnrichmentRun.from_raw(data.run)

    def get_templates(self) -> list[SimplifiedEnrichmentTemplate]:
        """Get all available Enrichment templates.

        Returns:
            list[enpi_api.l2.types.enrichment.SimplifiedEnrichmentTemplate]: Available Enrichment templates.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with EnpiApiClient() as enpi_client:
                templates = enpi_client.enrichment_api.get_templates()
            ```
        """
        enrichment_api_instance = openapi_client.EnrichmentApi(self._inner_api_client)

        with ApiErrorContext():
            data = enrichment_api_instance.get_enrichment_templates()

        return [
            SimplifiedEnrichmentTemplate(
                id=EnrichmentTemplateId(d.id),
                name=d.name,
                created_at=d.created_at,
            )
            for d in data.templates
        ]

    def get_template(self, enrichment_template_id: EnrichmentTemplateId) -> EnrichmentTemplate:
        """Get a Enrichment template by its ID.

        Args:
            enrichment_template_id (enpi_api.l2.types.enrichment.EnrichmentTemplateId): ID of a Enrichment template to get.

        Returns:
            enpi_api.l2.types.enrichment.EnrichmentTemplate: A Enrichment template matching the provided ID.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with EnpiApiClient() as enpi_client:
                template = enpi_client.enrichment_api.get_template(EnrichmentTemplateId(24))
            ```
        """
        enrichment_api_instance = openapi_client.EnrichmentApi(self._inner_api_client)

        with ApiErrorContext():
            data = enrichment_api_instance.get_enrichment_template(str(enrichment_template_id))

        return EnrichmentTemplate.from_raw(data.template)

    def delete_template(self, enrichment_template_id: EnrichmentTemplateId) -> None:
        """Delete a Enrichment Template by its ID.

        Args:
            enrichment_template_id (enpi_api.l2.types.enrichment.EnrichmentTemplateId): ID of the deleted Enrichment template.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with EnpiApiClient() as enpi_client:
                template = enpi_client.enrichment_api.delete_template(EnrichmentTemplateId(24))
            ```
        """
        enrichment_api_instance = openapi_client.EnrichmentApi(self._inner_api_client)

        with ApiErrorContext():
            enrichment_api_instance.delete_enrichment_template(str(enrichment_template_id))

    def create_template(
        self,
        name: str,
        operations: list[EnrichmentTemplateOperation],
    ) -> EnrichmentTemplate:
        """Create a new Enrichment Template.

        Args:
            name (str): Enrichment template name.
            operations (list[enpi_api.l2.types.enrichment.EnrichmentTemplateOperation]): Configs for the template's operations.

        Returns:
            enpi_api.l2.types.enrichment.EnrichmentTemplate: A newly created Enrichment template.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with EnpiApiClient() as enpi_client:
                operations=[
                    EnrichmentTemplateUnionOperation(
                        name="Counter",
                    ),
                    EnrichmentTemplateIntersectionOperation(
                        name="Target",
                    ),
                    EnrichmentTemplateDifferenceOperation(
                        name="Result",
                        input_operations=EnrichmentTemplateDifferenceInputs(
                            remove_operation="Counter",
                            from_operation="Target",
                        ),
                        annotations=[
                            EnrichmentTemplateFoldChangeAnnotation(name="Target FC"),
                        ],
                    ),
                ],
                template = enpi_client.enrichment_api.create_template(name="my new template", operations=operations)
            ```
        """
        enrichment_api_instance = openapi_client.EnrichmentApi(self._inner_api_client)

        payload = openapi_client.NewEnrichmentTemplate(name=name, saved=True, operations=[transform_operation(op) for op in operations])

        with ApiErrorContext():
            data = enrichment_api_instance.create_enrichment_template(payload)

        return EnrichmentTemplate.from_raw(data.template)

    def start(
        self,
        name: str,
        enrichment_template: EnrichmentTemplate,
        cluster_run_id: ClusterRunId,
        inputs: list[EnrichmentWorkInput],
    ) -> Execution[EnrichmentRun]:
        """Start a new Enrichment run.

        Args:
            name (str):
                Enrichment run name.
            enrichment_template (enpi_api.l2.types.enrichment.EnrichmentTemplate):
                Enrichment template ID.
            cluster_run_id (enpi_api.l2.types.cluster.ClusterRunId):
                Cluster run ID.
            inputs (list[enpi_api.l2.types.enrichment.EnrichmentWorkInput]):
                Configs for the template's operations.

        Returns:
            enpi_api.l2.types.execution.Execution[enpi_api.l2.types.enrichment.EnrichmentRun]: An awaitable that returns the new Enrichment Run.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Assuming that those are the collections meant for Enrichment run:
                - Counter collection IDs: 1, 2
                - Target collection IDs: 3, 4

            ```python
            with EnpiApiClient() as enpi_client:
                enrichment_run = client.enrichment_api.start(
                    name="Test Run",
                    enrichment_template=template,
                    cluster_run_id=cluster_run.id,
                    inputs=[
                        UnionOperationInput(
                            name="Counter",
                            input_collections=[CollectionSelector(value=CollectionId(1)),
                                CollectionSelector(value=CollectionId(2))],
                        ),
                        IntersectionOperationInput(
                            name="Target",
                            input_collections=[CollectionSelector(value=CollectionId(3)),
                                CollectionSelector(value=CollectionId(4))
                            ],
                        ),
                        FoldChangeInput(
                            name="Target FC",
                            operation_name="Result"
                            input_collections=FoldChangeInputCollections(
                                from_collection=CollectionSelector(value=CollectionId(3)),
                                to_collection=CollectionSelector(value=CollectionId(4)),
                            ),
                        ),
                    ],
                ).wait()
            ```
        """
        enrichment_api_instance = openapi_client.EnrichmentApi(self._inner_api_client)

        payload = openapi_client.EnrichmentWork(
            name=name,
            template=openapi_client.EnrichmentTemplateIdVersion(id=str(enrichment_template.id), version=int(enrichment_template.version)),
            cluster_run_id=cluster_run_id,
            inputs=[transform_operation_input(x) for x in inputs],
        )

        with ApiErrorContext():
            data = enrichment_api_instance.start_enrichment_run(payload)
            assert data.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(int(data.workflow_execution_id))

            def on_complete(task_id: WorkflowExecutionTaskId, task_state: TaskState) -> EnrichmentRun:
                enrichment_run = self.get_run_by_task_id(task_id)

                logger.success(f"Enrichment run with task ID: {data.workflow_execution_id} has successfully finished.")

                return enrichment_run

            waitable = WorkflowExecutionTaskWaitable[EnrichmentRun](
                workflow_execution_id=workflow_execution_id, task_template_name=WorkflowTaskTemplateName.ENPI_APP_ENRICHMENT, on_complete=on_complete
            )
            return Execution(wait=waitable.wait_and_return_result, check_execution_state=waitable.check_execution_state)

    def export_as_tsv(
        self,
        enrichment_run_id: EnrichmentRunId,
        operation: str,
        mode: EnrichmentExportMode,
        tag_ids: list[TagId],
        limit: int | None = None,
        output_directory: str | Path | None = None,
    ) -> Execution[Path]:
        """Run an export of a Enrichment operation result and download the TSV file.

        Args:
            enrichment_run_id (enpi_api.l2.types.enrichment.EnrichmentRunId): Enrichment run ID.
            operation (str): Name of the operation to export.
            mode (enpi_api.l2.types.enrichment.EnrichmentExportMode): Mode in which export will be run.
            tag_ids (list[enpi_api.l2.types.tag.TagId]): List of tags to be included in the export.
            limit (int | None):
                If specified, the export will contain only the first N clusters, N being the value passed as this param.
            output_directory (str | Path | None): The directory where to download the TSV file. Defaults to a
              unique temporary directory.

        Returns:
            enpi_api.l2.types.execution.Execution[Path]: An awaitable that returns the path to the downloaded TSV file containing the sequences.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with EnpiApiClient() as enpi_client:
                tsv_path = enpi_client.enrichment_api.export_as_tsv(
                    enrichment_run_id=EnrichmentRunId(42),
                    operation="Result",
                    mode=EnrichmentExportMode.REPRESENTATIVES,
                    tag_ids=[SequenceTags.Cdr3AminoAcids, SequenceTags.Chain],
                    limit=50,
                    output_directory="/results",
                ).wait()
            ```
        """

        # Ensure that the directory exists
        if output_directory is None:
            output_directory = unique_temp_dir()

        enrichment_api_instance = openapi_client.EnrichmentApi(self._inner_api_client)

        payload = openapi_client.EnrichmentExportPayload(
            operation_name=operation,
            enrichment_run_id=enrichment_run_id,
            mode=mode,
            tag_ids=[int(id) for id in tag_ids],
            limit=limit,
        )

        with ApiErrorContext():
            response = enrichment_api_instance.export_enrichment_results(payload)
            assert response.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(response.workflow_execution_id)

            def on_complete(task_id: WorkflowExecutionTaskId, task_state: TaskState) -> Path:
                file_api = FileApi(self._inner_api_client, self._log_level)
                zip_path = file_api.download_export_by_workflow_execution_task_id(task_id=task_id, output_directory=output_directory)

                with zipfile.ZipFile(zip_path, "r") as archive:
                    names = archive.namelist()
                    archive.extractall(output_directory)
                paths = [Path(os.path.join(output_directory, name)) for name in names]

                if len(paths) > 1:
                    logger.warning(f"More than 1 file encountered in the zipped export: {','.join([str(path) for path in paths])}, only returning first file")
                logger.success(f"Enrichment results export with task ID: {task_id} has successfully finished.")

                return paths[0]

            waitable = WorkflowExecutionTaskWaitable[Path](
                workflow_execution_id=workflow_execution_id, on_complete=on_complete, task_template_name=WorkflowTaskTemplateName.ENPI_APP_ENRICHMENT_EXPORT
            )
            return Execution(wait=waitable.wait_and_return_result, check_execution_state=waitable.check_execution_state)

    def export_as_df(
        self,
        enrichment_run_id: EnrichmentRunId,
        operation: str,
        mode: EnrichmentExportMode,
        tag_ids: list[TagId],
        limit: int | None = None,
    ) -> Execution[pd.DataFrame]:
        """Runs an Export of a Enrichment Operation results and loads it as a pandas DataFrame.

        Args:
            enrichment_run_id (enpi_api.l2.types.enrichment.EnrichmentRunId): Enrichment run ID.
            operation (str): Name of the operation to export.
            mode (enpi_api.l2.types.enrichment.EnrichmentExportMode): Mode in which export will be run.
            tag_ids (list[enpi_api.l2.types.tag.TagId]): List of tags to be included in the export.
            limit (int | None):
                If specified, the export will contain only the first N clusters, N being the value passed as this param.

        Returns:
            enpi_api.l2.types.execution.Execution[Path]: An awaitable that returns the path to the downloaded TSV file containing the sequences.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            with EnpiApiClient() as enpi_client:
                tsv_path = enpi_client.enrichment_api.export_as_df(
                    enrichment_run_id=EnrichmentRunId(42),
                    operation="Result",
                    mode=EnrichmentExportMode.REPRESENTATIVES,
                    tag_ids=[SequenceTags.Cdr3AminoAcids, SequenceTags.Chain],
                    limit=50
                ).wait()
            ```
        """

        export_tsv = self.export_as_tsv(enrichment_run_id, operation, mode, tag_ids, limit)

        def wait() -> pd.DataFrame:
            file_path = export_tsv.wait()
            return pd.read_csv(file_path, delimiter="\t")

        return Execution(wait=wait, check_execution_state=export_tsv.check_execution_state)
