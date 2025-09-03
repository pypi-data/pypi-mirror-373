from typing import cast

from loguru import logger
from pydantic import StrictStr

from enpi_api.l1 import openapi_client
from enpi_api.l2.client.api.collection_api import CollectionApi
from enpi_api.l2.events.workflow_execution_task_waitable import WorkflowExecutionTaskWaitable
from enpi_api.l2.types.api_error import ApiError, ApiErrorContext
from enpi_api.l2.types.collection import CollectionId, CollectionMetadata
from enpi_api.l2.types.execution import Execution
from enpi_api.l2.types.file import FileId
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.types.reference_database import ReferenceDatabaseRevision
from enpi_api.l2.types.sequence_annotation import (
    CloneIdentifierExtractionConfig,
    CorrectionSettings,
    LiabilityType,
    MutationAssaySettings,
    QualityControlTemplate,
    SequenceTemplate,
    SequenceTemplateConfig,
)
from enpi_api.l2.types.tag import TagId
from enpi_api.l2.types.task import TaskState
from enpi_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName


class MultipleSequenceTemplatesWithName(Exception):
    """Indicates that multiple sequence templates with the given name can be found."""

    def __init__(self, name: str) -> None:
        """@private"""
        super().__init__(
            f"Multiple sequence templates with name '{name}' found, ensure the names are unique, or use the "
            f"`get_sequence_templates` method to filter them yourself"
        )


class NoQualityControlTemplateWithName(Exception):
    """Indicates that no quality control template with the given name can be found."""

    def __init__(self, name: str) -> None:
        """@private"""
        super().__init__(f"No quality control template with name '{name}' found")


class MultipleQualityControlTemplatesWithName(Exception):
    """Indicates that multiple quality control templates with the given name can be found."""

    def __init__(self, name: str) -> None:
        """@private"""
        super().__init__(
            f"Multiple quality control templates with name '{name}' found, ensure the names are unique, or use the "
            f"`get_quality_control_templates` method to filter them yourself"
        )


class NoSequenceTemplateWithName(Exception):
    """Indicates that no sequence template with the given name can be found."""

    def __init__(self, name: str) -> None:
        """@private"""
        super().__init__(f"No sequence template with name '{name}' found")


class SequenceAnnotationApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_quality_control_templates(self) -> list[QualityControlTemplate]:
        """Get a list of all quality control templates owned by you or shared with you.

        Returns:
            list[enpi_api.l2.types.sequence_annotation.QualityControlTemplate]: A list of quality control templates.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            quality_control_templates = self.get_quality_control_templates()
            ```
        """

        sequence_annotation_api_instance = openapi_client.SequenceAnnotationApi(self._inner_api_client)

        try:
            return [QualityControlTemplate.from_raw(i) for i in sequence_annotation_api_instance.quality_control_templates()]
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def get_quality_control_template_by_name(self, name: str) -> QualityControlTemplate:
        """Get a quality control template by its name.

        It will raise an error if not exactly one quality control template with the given name is found.

        Args:
            name (str): The name of the quality control template to get.

        Returns:
            enpi_api.l2.types.sequence_annotation.QualityControlTemplate: The quality control template.

        Raises:
            enpi_api.l2.client.api.sequence_annotation_api.NoQualityControlTemplateWithName: If no quality control template with the given name can be found.
            enpi_api.l2.client.api.sequence_annotation_api.MultipleQualityControlTemplatesWithName: If multiple quality control templates with the given name can be found.
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            name = "Quality control template 1"
            quality_control_template = self.get_quality_control_template_by_name(name)
            ```
        """

        quality_control_templates = self.get_quality_control_templates()

        matching_templates = [qct for qct in quality_control_templates if qct.name == name]

        if len(matching_templates) == 0:
            raise NoQualityControlTemplateWithName(name)
        elif len(matching_templates) > 1:
            raise MultipleQualityControlTemplatesWithName(name)

        return matching_templates[0]

    def get_sequence_templates(self) -> list[SequenceTemplate]:
        """Get a list of all sequence templates owned by you or shared with you.

        Returns:
            list[enpi_api.l2.types.sequence_annotation.SequenceTemplate]: A list of sequence templates

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            sequence_templates = self.get_sequence_templates()
            ```
        """

        sequence_annotation_api_instance = openapi_client.SequenceAnnotationApi(self._inner_api_client)

        try:
            return [SequenceTemplate.from_raw(i) for i in sequence_annotation_api_instance.sequence_templates()]
        except openapi_client.ApiException as e:
            raise ApiError(e)

    def get_sequence_template_by_name(self, name: str) -> SequenceTemplate:
        """Get a sequence template by its name.

        It will raise an error if not exactly one sequence template with the given name is found.

        Args:
            name (str): The name of the sequence template to get.

        Raises:
            enpi_api.l2.client.api.sequence_annotation_api.NoSequenceTemplateWithName: If no sequence template with the given name can be found.
            enpi_api.l2.client.api.sequence_annotation_api.MultipleSequenceTemplatesWithName: If multiple sequence templates with the given name can be found.
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Returns:
            enpi_api.l2.types.sequence_annotation.SequenceTemplate: The sequence template.

        Example:
            ```python
            name = "Sequence template 1"
            sequence_template = self.get_sequence_template_by_name(name)
            ```
        """

        sequence_templates = self.get_sequence_templates()

        matching_templates = [st for st in sequence_templates if st.name == name]

        if len(matching_templates) == 0:
            raise NoSequenceTemplateWithName(name)
        elif len(matching_templates) > 1:
            raise MultipleSequenceTemplatesWithName(name)

        return matching_templates[0]

    def start(
        self,
        name: str,
        file_ids: list[FileId],
        sequence_templates: list[SequenceTemplateConfig],
        reference_database_revision: ReferenceDatabaseRevision,
        quality_control_template: QualityControlTemplate,
        archive_inputs: bool = False,
        clone_id_extraction: CloneIdentifierExtractionConfig | None = None,
        correction_settings: CorrectionSettings | None = None,
        mutation_assay_settings: MutationAssaySettings | None = None,
        chain_fraction_tag_id: TagId | None = None,
        liability_check: list[LiabilityType | str] = [],
        restrict_deduplication_within_file: bool = False,
        filename_tag_id: TagId | None = None,
    ) -> Execution[CollectionMetadata]:
        """Start Sequence Annotation on raw sequencing data.

        A sequence template (available here: enpi_api.l2.client.api.sequence_annotation_api.SequenceAnnotationApi.get_sequence_template_by_name) and a quality control template
        (enpi_api.l2.client.api.sequence_annotation_api.SequenceAnnotationApi.get_quality_control_template_by_name) are required in order to run a Sequence Annotation task.
        **<u>Templates can be created and configured only via the [web interface of ENPICOM-Platform](https://igx.bio/)</u>**, it can not
        be done through SDK or API. Additionally, getting familiar with Sequence Annotation in the web interface can help
        in understanding it and setting up a desired task configuration due to it being more informative than the
        minimal documentation provided for this function.

        Args:
            name (str): The name of the resulting collection.
            file_ids (list[enpi_api.l2.types.file.FileId]): List of the IDs of raw sequencing data files.
            sequence_templates (list[enpi_api.l2.types.sequence_annotation.SequenceTemplateConfig]): A list of configuration objects to specify the sequence
              templates to be used. For more information, see the `enpi_api.l2.types.sequence_annotation.SequenceTemplateConfig` class.
            reference_database_revision (enpi_api.l2.types.reference_database.ReferenceDatabaseRevision | None): The reference database revision to use.
              The reference database specifies which organism it is linked to.
            archive_inputs (bool): Whether to archive the input files after the Sequence Annotation run is finished.
            quality_control_template (enpi_api.l2.types.sequence_annotation.QualityControlTemplate): The Quality Control Template to use.
            clone_id_extraction (enpi_api.l2.types.sequence_annotation.CloneIdentifierExtractionConfig | None): The configuration for extracting clone IDs. This is only
              needed if your sequence template has the option "Manually Specify Clone Identifier" enabled. In other
              cases, this parameter can be omitted.

              For more information, see the `enpi_api.l2.types.sequence_annotation.CloneIdentifierExtractionConfig` class.
            correction_settings (enpi_api.l2.types.sequence_annotation.CorrectionSettings | None): The settings to correct regions to the germline reference,
            or complete the sequence to full VDJ using germline reference nucleotides.
            This is useful to reduce artificial diversity in libraries with e.g. fixed framework regions.
            mutation_assay_settings (enpi_api.l2.types.sequence_annotation.MutationAssaySettings | None): The settings to run Sequence Annotation for a mutation assay.
            chain_fraction_tag_id (enpi_api.l2.types.tag.TagId | None): The sequence-level tag identifier of the tag that is used to store
              the fraction of each chain within a clone.
            liability_check (list[enpi_api.l2.types.sequence_annotation.LiabilityType | str]): A list of liability checks to perform.
              Summed counts are stored as clone level tags.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Returns:
            enpi_api.l2.types.execution.Execution[enpi_api.l2.types.collection.CollectionMetadata]: An object that allows you to wait for the
              execution to finish and get the resulting collection metadata.

        Example:

            Part of `start_sequence_annotation_run.py` example script.

            ```python
            # Templates need to be present in the ENPICOM-Platform already
            sequence_template_name = "sequence template 1"
            quality_control_template_name = "quality control template 1"

            sequence_templates = [st for st in client.sequence_annotation_api.get_sequence_templates() if st.name == sequence_template_name]
            quality_control_templates = [qct for qct in client.sequence_annotation_api.get_quality_control_templates() if qct.name == quality_control_template_name]

            quality_control_template = QualityControlTemplate(quality_control_templates[0])
            sequence_template_id = SequenceTemplateId(sequence_templates[0].id)

            # Upload the input file
            file_path = "data.fq"
            file: File = client.file_api.upload_file(file_path=file_path, tags=[]).wait()
            file_ids = [file.id]

            # Get the reference database revision
            reference_database_revision = client.reference_database_api.get_revision_by_name(name=REFERENCE_NAME, species=ORGANISM)

            collection_name = "New collection from Sequence Annotation"

            # We will now start Sequence Annotation, which will process raw sequencing data into annotated clone collections
            clone_collection = client.sequence_annotation_api.start(
                name=collection_name,
                file_ids=file_ids,
                # To assign a sequence template to each input file
                sequence_templates=[
                    SequenceTemplateConfig(
                        # We select it using a selector, in this case by matching the file_id, but we could also match on file name or tags
                        selector=SequenceTemplateSelector(value=f),
                        # And then assign it using a sequence template id
                        id=sequence_template_id,
                    )
                    for f in file_ids
                ],
                reference_database_revision=reference_database_revision,
                # Archives the raw sequencing data after they have been processed
                archive_inputs=True,
                quality_control_template=quality_control_template,
            ).wait()
            ```
        """

        if filename_tag_id is not None:
            if not restrict_deduplication_within_file:
                raise ValueError("filename_tag_id can only be set if restrict_deduplication_within_file is set to True")

        sequence_annotation_api_instance = openapi_client.SequenceAnnotationApi(self._inner_api_client)

        try:
            inner_sequence_templates: list[openapi_client.SequenceAnnotationWorkSequenceTemplatesInner] = []
            for st in sequence_templates:
                match st.selector.type:
                    case "file_id":
                        inner_sequence_templates.append(
                            openapi_client.SequenceAnnotationWorkSequenceTemplatesInner(
                                template_id=st.id,
                                template_version=st.version,
                                selector=openapi_client.SequenceTemplateSelector(
                                    openapi_client.MatchAFileByItsID(type=st.selector.type, value=st.selector.value)
                                ),
                            )
                        )
                    case _:
                        assert False, f"Selector type {st.selector.type} should be matched"

            sequence_annotation_work = openapi_client.SequenceAnnotationWork(
                name=name,
                file_ids=cast(list[StrictStr], file_ids),
                sequence_templates=inner_sequence_templates,
                reference_database=openapi_client.ReferenceDatabaseIdVersion(
                    id=str(reference_database_revision.reference_database_id),
                    version=int(reference_database_revision.reference_database_version),
                ),
                quality_control_template=openapi_client.QualityControlTemplateIdOptionalVersion(
                    id=str(quality_control_template.id), version=int(quality_control_template.version)
                ),
                archive_inputs=archive_inputs,
                clone_id_to_tag_spec=clone_id_extraction.to_api_payload() if clone_id_extraction else None,
                correction_settings=correction_settings.to_api_payload() if correction_settings else None,
                mutation_assay_settings=mutation_assay_settings.to_api_payload() if mutation_assay_settings else None,
                chain_fraction_tag_id=chain_fraction_tag_id,
                liability_check=liability_check,
                restrict_deduplication_within_file=restrict_deduplication_within_file,
                filename_tag_id=filename_tag_id,
            )

            with ApiErrorContext():
                sequence_annotation_job = sequence_annotation_api_instance.start_sequence_annotation(sequence_annotation_work=sequence_annotation_work)
                assert sequence_annotation_job.workflow_execution_id is not None

                workflow_execution_id = WorkflowExecutionId(int(sequence_annotation_job.workflow_execution_id))

                def on_complete(task_id: WorkflowExecutionTaskId, task_state: TaskState) -> CollectionMetadata:
                    assert task_state == TaskState.SUCCEEDED, f"Task {task_id} did not reach {TaskState.SUCCEEDED} state, got {task_state} state instead"

                    get_collection_id_response = sequence_annotation_api_instance.get_sequence_annotation_collection_id_by_workflow_execution_task_id(task_id)
                    collection_id = get_collection_id_response.collection_id
                    assert collection_id is not None

                    logger.success(f"Collection with ID `{collection_id}` was successfully obtained by running Sequence Annotation")

                    collection_api = CollectionApi(self._inner_api_client, self._log_level)
                    return collection_api.get_collection_metadata_by_id(CollectionId(collection_id))

                waitable = WorkflowExecutionTaskWaitable[CollectionMetadata](
                    workflow_execution_id=workflow_execution_id,
                    task_template_name=WorkflowTaskTemplateName.ENPI_APP_SEQUENCE_ANNOTATION,
                    on_complete=on_complete,
                )

                return Execution(wait=waitable.wait_and_return_result, check_execution_state=waitable.check_execution_state)

        except openapi_client.ApiException as e:
            raise ApiError(e)
