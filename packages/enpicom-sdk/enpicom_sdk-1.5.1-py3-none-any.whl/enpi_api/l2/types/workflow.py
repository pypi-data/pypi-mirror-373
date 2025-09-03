from enum import StrEnum
from typing import NewType, Optional

from enpi_api.l1 import openapi_client
from enpi_api.l2.types.task import TaskState
from enpi_api.l2.util.from_raw_model import FromRawModel

WorkflowExecutionId = NewType("WorkflowExecutionId", int)
"""The unique identifier of a workflow execution."""

WorkflowExecutionTaskId = NewType("WorkflowExecutionTaskId", int)
"""The unique identifier of a workflow execution task."""


class WorkflowExecutionTask(FromRawModel[openapi_client.WorkflowExecutionTaskStatesInner]):
    task_id: WorkflowExecutionTaskId
    """The unique identifier of the workflow execution task."""
    task_template_name: Optional[str]
    """The unique identifier of the workflow execution."""
    state: TaskState
    """The state of the workflow execution."""

    @classmethod
    def _build(cls, raw: openapi_client.WorkflowExecutionTaskStatesInner) -> "WorkflowExecutionTask":
        assert raw.id is not None

        return cls(
            task_id=WorkflowExecutionTaskId(raw.id),
            task_template_name=raw.task_template_name,
            state=TaskState(raw.state.lower()),
        )


class WorkflowTaskTemplateName(StrEnum):
    ENPI_APP_BASKET_ADD_CLONES = "enpi-app-basket-add-clones"
    ENPI_APP_BASKET_EXPORT = "enpi-app-basket-export-table"
    ENPI_APP_BASKET_EXPORT_FASTA = "enpi-app-basket-export-fasta"
    ENPI_APP_BASKET_MSA = "enpi-app-basket-msa"
    ENPI_APP_BASKET_REMOVE_CLONES = "enpi-app-basket-remove-clones"
    ENPI_APP_PHYLOGENY = "enpi-app-phylogeny"
    ENPI_APP_PHYLOGENY_EXPORT = "enpi-app-phylogeny-export"
    ENPI_APP_CHROMATOGRAM_CREATE = "enpi-app-chromatogram"
    ENPI_APP_CHROMATOGRAM_SAVE = "enpi-app-chromatogram-save"
    ENPI_APP_CLUSTER = "enpi-app-cluster"
    ENPI_APP_CLUSTER_EXPORT = "enpi-app-cluster-export"
    ENPI_APP_COLLECTION_EXPORT = "enpi-app-collection-export"
    ENPI_APP_COLLECTION_IMPORT = "enpi-app-collection-import"
    ENPI_APP_REPERTOIRE_OVERVIEW = "enpi-app-repertoire-overview"
    ENPI_APP_QUALITY_CONTROL = "enpi-app-quality-control"
    ENPI_APP_LIABILITIES = "enpi-app-liabilities"
    ENPI_APP_METADATA_IMPORT = "enpi-app-metadata-import"
    ENPI_APP_METADATA_IMPORT_TEMPLATED = "enpi-app-metadata-import-templated"
    ENPI_APP_ML_ENDPOINT_DEPLOY = "enpi-app-ml-endpoint-deploy"
    ENPI_APP_ML_INVOCATION_PROCESSING = "enpi-app-ml-invocation-processing"
    ENPI_APP_SEQUENCE_ANNOTATION = "enpi-app-sequence-annotation"
    ENPI_APP_COLLECTION_EXPORT_READ_FATES = "enpi-app-collection-export-read-fates"
    ENPI_APP_REFERENCE_CREATE = "enpi-app-reference-create"
    ENPI_APP_SEQUENCE_VIEWER_EXPORT_PDB = "enpi-app-sequence-viewer-export-pdb"
    ENPI_APP_TAG_CREATE = "enpi-app-tag-create"
    ENPI_APP_ENRICHMENT = "enpi-app-enrichment"
    ENPI_APP_ENRICHMENT_EXPORT = "enpi-app-enrichment-export"


"""Map of all workflow task templates"""
