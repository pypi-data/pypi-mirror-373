from datetime import datetime
from enum import Enum
from typing import Literal, NewType, cast

from pydantic import BaseModel
from typing_extensions import assert_never

from enpi_api.l1 import openapi_client
from enpi_api.l2.types.cluster import ClusterRunId
from enpi_api.l2.types.collection import CollectionId
from enpi_api.l2.types.tag import TagId, TagValue
from enpi_api.l2.util.from_raw_model import FromRawModel

EnrichmentRunId = NewType("EnrichmentRunId", int)
"""The unique identifier of a Enrichment Run."""

EnrichmentTemplateId = NewType("EnrichmentTemplateId", str)
"""The unique identifier of a Enrichment Template."""

EnrichmentTemplateVersion = NewType("EnrichmentTemplateVersion", int)
"""The Version of a Enrichment Template."""


class EnrichmentOperationType(str, Enum):
    """Types of operations available in Enrichment."""

    UNION = "union"
    INTERSECTION = "intersection"
    DIFFERENCE = "difference"
    FOLD_CHANGE = "fold_change"


class SimplifiedEnrichmentOperation(BaseModel):
    """Simplified read model for Enrichment Operation."""

    name: str
    """Operation name."""
    type: EnrichmentOperationType
    """Operation type."""


class SimplifiedEnrichmentTemplate(BaseModel):
    """Simplified read model for Enrichment Template."""

    id: EnrichmentTemplateId
    """Enrichment Template Id."""
    name: str
    """Operation name."""
    created_at: datetime | None
    """Date when the template was created."""


class CollectionByIdSelector(BaseModel):
    """Selects a collection by matching it with the provided unique ID."""

    type: Literal["collection_id"] = "collection_id"
    """Internal type used to recognize the selector object."""
    value: CollectionId
    """The unique identifier of a collection."""


class CollectionByNameSelector(BaseModel):
    """Selects a collection by matching it with the provided unique ID."""

    type: Literal["collection_name"] = "collection_name"
    """Internal type used to recognize the selector object."""
    value: str
    """The name of a collection."""


class CollectionByTagValueSelector(BaseModel):
    """Selects a collection by matching it with the provided unique ID."""

    type: Literal["collection_tag_value"] = "collection_tag_value"
    """Internal type used to recognize the selector object."""
    tag_id: TagId
    """The collection tag id"""
    tag_value: TagValue
    """The tag value to look for"""


class SetOperationSelector(BaseModel):
    """Selects a collection by matching it with the provided unique ID."""

    type: Literal["set_operation"] = "set_operation"
    """Internal type used to recognize the selector object."""
    value: str
    """The set operation name"""


CollectionSelector = CollectionByIdSelector | CollectionByNameSelector | CollectionByTagValueSelector
EnrichmentTemplateNodeInput = CollectionByIdSelector | CollectionByNameSelector | CollectionByTagValueSelector | SetOperationSelector


class EnrichmentRun(FromRawModel[openapi_client.EnrichmentRun]):
    """Existing Enrichment Run configuration."""

    id: EnrichmentRunId
    """Enrichment Run Id."""
    name: str
    """Enrichment Run name."""
    template_id: EnrichmentTemplateId
    """Enrichment Template Id."""
    template_version: EnrichmentTemplateVersion
    """Enrichment Template Version."""
    cluster_run_id: ClusterRunId
    """Cluster Run Id."""
    operations: list[SimplifiedEnrichmentOperation]
    """List of operations present in this Enrichment run."""

    @classmethod
    def _build(cls, raw: openapi_client.EnrichmentRun) -> "EnrichmentRun":
        assert raw.id is not None
        return cls(
            id=EnrichmentRunId(raw.id),
            name=str(raw.name),
            template_id=EnrichmentTemplateId(raw.template.id),
            template_version=EnrichmentTemplateVersion(raw.template.version),
            cluster_run_id=ClusterRunId(raw.cluster_run_id),
            operations=[SimplifiedEnrichmentOperation(name=d.name, type=EnrichmentOperationType(d.type)) for d in raw.operations],
        )


class EnrichmentTemplateFoldChangeInputs(BaseModel):
    """Enrichment Fold change input operations that can be specified within the Enrichment template.

    The results of the operations specified for this object will be used as inputs
    for the fold change measeurement computation.

    Example:
        Fold change ratio between results "A" and "B" after operation "C" is done equals 2.
    """

    from_input: EnrichmentTemplateNodeInput | None = None
    """Previously computed operation results or input clone collections.
        Serves as the `B` value in the `A`/`B` fold change ratio formula."""
    to_input: EnrichmentTemplateNodeInput | None = None
    """Previously computed operation results or input clone collections.
        Serves as the `A` value in the `A`/`B` fold change ratio formula."""


class EnrichmentTemplateFoldChangeAnnotation(FromRawModel[openapi_client.EnrichmentTemplateFoldChangeAnnotation]):
    """Enrichment fold change annotation computed for input operations results, defined within a Enrichment template."""

    name: str
    """Name of the fold change annotation annotation. Has to be unique."""
    inputs: EnrichmentTemplateFoldChangeInputs | None = None
    """Fold change input operations, a results of previously planned (performed during Enrichment run) operations within the template."""

    @classmethod
    def _build(cls, raw: openapi_client.EnrichmentTemplateFoldChangeAnnotation) -> "EnrichmentTemplateFoldChangeAnnotation":
        return cls(
            name=str(raw.name),
            inputs=EnrichmentTemplateFoldChangeInputs(
                from_input=build_node_input(raw.inputs.var_from) if raw.inputs.var_from is not None else None,
                to_input=build_node_input(raw.inputs.to) if raw.inputs.to is not None else None,
            )
            if raw.inputs is not None
            else None,
        )


class EnrichmentTemplateUnionOperation(FromRawModel[openapi_client.EnrichmentTemplateJoinOperation]):
    """Definition of a Enrichment union operation performed on the results of provided operations."""

    name: str
    """Name of the union operation. Has to be unique."""
    inputs: list[EnrichmentTemplateNodeInput] | None = None
    """A list of input operations for results of which the union will be applied."""
    annotations: list[EnrichmentTemplateFoldChangeAnnotation] | None = None
    """Optional annotations to be added onto this operation result."""

    @classmethod
    def _build(cls, raw: openapi_client.EnrichmentTemplateJoinOperation) -> "EnrichmentTemplateUnionOperation":
        return cls(
            name=str(raw.name),
            inputs=[build_node_input(inp) for inp in raw.inputs],
            annotations=[EnrichmentTemplateFoldChangeAnnotation.from_raw(x) for x in raw.annotations] if raw.annotations is not None else None,
        )


class EnrichmentTemplateIntersectionOperation(FromRawModel[openapi_client.EnrichmentTemplateJoinOperation]):
    """Definition of a Enrichment intersection operation performed on the results of provided operations."""

    name: str
    """Name of the intersection operation. Has to be unique."""
    inputs: list[EnrichmentTemplateNodeInput] | None = None
    """A list of input operations for results of which the intersection will be applied."""
    annotations: list[EnrichmentTemplateFoldChangeAnnotation] | None = None
    """Optional annotations to be added onto this operation result."""

    @classmethod
    def _build(cls, raw: openapi_client.EnrichmentTemplateJoinOperation) -> "EnrichmentTemplateIntersectionOperation":
        return cls(
            name=str(raw.name),
            inputs=[build_node_input(inp) for inp in raw.inputs],
            annotations=[EnrichmentTemplateFoldChangeAnnotation.from_raw(x) for x in raw.annotations] if raw.annotations is not None else None,
        )


class EnrichmentTemplateDifferenceInputs(BaseModel):
    """Enrichment difference operation inputs that can be specified within
    the Enrichment template.

    Example:
        Assuming two operations `Operation A` and `Operation B` were already specified in the Enrichment template:

        ```python
        # A difference operation specified in the Enrichment template
        EnrichmentTemplateDifferenceOperation(
            name="Operation C",
            input_operations=EnrichmentTemplateDifferenceInputs(
                remove_operation="Operation A",
                from_operation="Operation B",
            ),
        ),
        ```
    """

    remove_input: EnrichmentTemplateNodeInput | None = None
    """Clusters from this operation will be subtracted from the other one."""
    from_input: EnrichmentTemplateNodeInput | None = None
    """Clusters from the other operation result will be subtracted from this one."""


class EnrichmentTemplateDifferenceOperation(FromRawModel[openapi_client.EnrichmentTemplateDifferenceOperation]):
    """Definition of a Enrichment difference operation performed on the results of provided operations."""

    name: str
    """Name of the difference operation. Has to be unique."""
    inputs: EnrichmentTemplateDifferenceInputs | None = None
    """Enrichment difference operation inputs that can be specified within the Enrichment template."""
    annotations: list[EnrichmentTemplateFoldChangeAnnotation] | None = None
    """Optional annotations to be added onto this operation result."""

    @classmethod
    def _build(cls, raw: openapi_client.EnrichmentTemplateDifferenceOperation) -> "EnrichmentTemplateDifferenceOperation":
        return cls(
            name=str(raw.name),
            inputs=EnrichmentTemplateDifferenceInputs(
                remove_input=build_node_input(raw.inputs.remove) if raw.inputs.remove is not None else None,
                from_input=build_node_input(raw.inputs.var_from) if raw.inputs.var_from is not None else None,
            ),
            annotations=[EnrichmentTemplateFoldChangeAnnotation.from_raw(x) for x in raw.annotations] if raw.annotations is not None else None,
        )


EnrichmentTemplateOperation = EnrichmentTemplateUnionOperation | EnrichmentTemplateIntersectionOperation | EnrichmentTemplateDifferenceOperation
"""A single Enrichment operation definition present in the Enrichment template.

    In general, those are used to to define what operations will be performed during the Enrichment run.
    They need to have unique names (for matching purposes) and either need other operations within the template to be specified
    as their inputs or have inputs matched with them later on via `enpi_api.l2.types.enrichment.EnrichmentWorkInput`.
"""


class EnrichmentTemplate(FromRawModel[openapi_client.EnrichmentTemplate]):
    """Enrichment Template configuration."""

    id: EnrichmentTemplateId
    """The unique identifier of a Enrichment Template."""
    version: EnrichmentTemplateVersion
    """The version of a Enrichment Template"""
    name: str
    """Name of a Enrichment Template."""
    created_at: datetime
    """Date of the Enrichment Template's creation."""
    operations: list[EnrichmentTemplateOperation]
    """List of operations present in this Enrichment Run."""
    saved: bool
    """Indicates whether the template is reusable"""

    @classmethod
    def _build(cls, raw: openapi_client.EnrichmentTemplate) -> "EnrichmentTemplate":
        assert raw.created_at is not None

        return cls(
            id=EnrichmentTemplateId(raw.id),
            version=EnrichmentTemplateVersion(raw.version),
            name=str(raw.name),
            saved=raw.saved,
            created_at=raw.created_at,
            operations=[build_operation(d) for d in raw.operations],
        )


def transform_to_nullable_node_input(inp: EnrichmentTemplateNodeInput | None) -> openapi_client.NullishEnrichmentTemplateNodeInput:
    """An internal function used for transforming Enrichment template node input config into API format.
    @private

    Args:
        inp (EnrichmentTemplateNodeInput): Enrichment template node input in "user format".

    Returns:
        openapi_client.NullishEnrichmentTemplateNodeInput: Enrichment template node input in "API format".
    """
    if inp is None:
        return cast(openapi_client.NullishEnrichmentTemplateNodeInput, None)
    else:
        return openapi_client.NullishEnrichmentTemplateNodeInput.from_dict(inp.model_dump())


def transform_to_node_input(inp: EnrichmentTemplateNodeInput) -> openapi_client.EnrichmentTemplateNodeInput:
    """An internal function used for transforming Enrichment template node input config into API format.
    @private

    Args:
        inp (EnrichmentTemplateNodeInput): Enrichment template node input in "user format".

    Returns:
        openapi_client.EnrichmentTemplateNodeInput: Enrichment template node input in "API format".
    """
    return openapi_client.EnrichmentTemplateNodeInput.from_dict(inp.model_dump())


def build_node_input(inp: openapi_client.EnrichmentTemplateNodeInput | openapi_client.NullishEnrichmentTemplateNodeInput) -> EnrichmentTemplateNodeInput:
    """An internal function used for transforming Enrichment template node inputs from API format to "user format".
    @private

    Args:
        inp (openapi_client.EnrichmentTemplateEnrichmentNodeInput): Enrichment template node input in "API format".

    Returns:
        EnrichmentTemplateNodeInput: Enrichment template in "user format".
    """

    if isinstance(inp.actual_instance, openapi_client.UnionOperationInputsInputsInner):
        if isinstance(inp.actual_instance.actual_instance, openapi_client.MatchCollectionByItsID):
            assert inp.actual_instance.actual_instance.value is not None
            return CollectionByIdSelector(value=CollectionId(inp.actual_instance.actual_instance.value))
        elif isinstance(inp.actual_instance.actual_instance, openapi_client.MatchCollectionByItsName):
            return CollectionByNameSelector(value=inp.actual_instance.actual_instance.value)
        elif isinstance(inp.actual_instance.actual_instance, openapi_client.MatchCollectionByTagValue):
            value: openapi_client.MatchCollectionByTagValueValue = inp.actual_instance.actual_instance.value
            assert value.tag_id is not None
            return CollectionByTagValueSelector(tag_id=TagId(int(value.tag_id)), tag_value=str(value.tag_value))
        else:
            raise ValueError("Wrong Enrichment operation type")
    elif isinstance(inp.actual_instance, openapi_client.SetOperationInput):
        return SetOperationSelector(value=inp.actual_instance.value)
    else:
        raise ValueError("Wrong Enrichment operation type")


def transform_operation(op: EnrichmentTemplateOperation) -> openapi_client.EnrichmentTemplateEnrichmentOperation:
    """An internal function used for transforming Enrichment template operations config into API format.
    @private

    Args:
        op (EnrichmentTemplateOperation): Enrichment template operation in "user format".

    Returns:
        openapi_client.EnrichmentTemplateEnrichmentOperation: Enrichment template in "API format".
    """
    annotations = (
        [
            openapi_client.EnrichmentTemplateFoldChangeAnnotation(
                name=x.name,
                type=EnrichmentOperationType.FOLD_CHANGE,
                inputs=openapi_client.EnrichmentTemplateFoldChangeAnnotationInputs(
                    **{
                        "from": transform_to_nullable_node_input(x.inputs.from_input) if x.inputs is not None else None,
                        "to": transform_to_nullable_node_input(x.inputs.to_input) if x.inputs is not None else None,
                    }
                ),
            )
            for x in op.annotations
        ]
        if op.annotations is not None
        else None
    )

    if isinstance(op, EnrichmentTemplateUnionOperation):
        return openapi_client.EnrichmentTemplateEnrichmentOperation(
            openapi_client.EnrichmentTemplateJoinOperation(
                name=op.name,
                type=EnrichmentOperationType.UNION,
                inputs=[transform_to_node_input(inp) for inp in (op.inputs or [])],
                annotations=annotations,
            )
        )
    elif isinstance(op, EnrichmentTemplateIntersectionOperation):
        return openapi_client.EnrichmentTemplateEnrichmentOperation(
            openapi_client.EnrichmentTemplateJoinOperation(
                name=op.name,
                type=EnrichmentOperationType.INTERSECTION,
                inputs=[transform_to_node_input(inp) for inp in (op.inputs or [])],
                annotations=annotations,
            )
        )
    elif isinstance(op, EnrichmentTemplateDifferenceOperation):
        return openapi_client.EnrichmentTemplateEnrichmentOperation(
            openapi_client.EnrichmentTemplateDifferenceOperation(
                name=op.name,
                type=EnrichmentOperationType.DIFFERENCE,
                inputs=openapi_client.EnrichmentTemplateDifferenceOperationInputs(
                    **{
                        "remove": transform_to_nullable_node_input(op.inputs.remove_input) if op.inputs is not None else None,
                        "from": transform_to_nullable_node_input(op.inputs.from_input) if op.inputs is not None else None,
                    }
                ),
                annotations=annotations,
            )
        )
    else:
        raise ValueError("Wrong Enrichment operation type")


def build_operation(op: openapi_client.EnrichmentTemplateEnrichmentOperation) -> EnrichmentTemplateOperation:
    """An internal function used for transforming Enrichment template operations config from API format to "user format".
    @private

    Args:
        op (openapi_client.EnrichmentTemplateEnrichmentOperation): Enrichment template operation in "API format".

    Returns:
        EnrichmentTemplateOperation: Enrichment template in "user format".
    """
    if isinstance(op.actual_instance, openapi_client.EnrichmentTemplateJoinOperation):
        if op.actual_instance.type == EnrichmentOperationType.UNION:
            return EnrichmentTemplateUnionOperation.from_raw(op.actual_instance)
        else:
            return EnrichmentTemplateIntersectionOperation.from_raw(op.actual_instance)
    elif isinstance(op.actual_instance, openapi_client.EnrichmentTemplateDifferenceOperation):
        return EnrichmentTemplateDifferenceOperation.from_raw(op.actual_instance)
    else:
        raise ValueError("Wrong Enrichment operation type")


class UnionOperationInput(BaseModel):
    """Used to specify input collections for union operation during Enrichment run configuration."""

    name: str
    """Name of the union operation. Has to match the one defined in the Enrichment template."""
    inputs: list[CollectionSelector]
    """A list of input clone collections."""


class IntersectionOperationInput(BaseModel):
    """Used to specify input collections for intersection operation during Enrichment run configuration."""

    name: str
    """Name of the intersection operation. Has to match the one defined in the Enrichment template."""
    inputs: list[CollectionSelector]
    """A list of input clone collections."""


class DifferenceOperationInputs(BaseModel):
    """Used to specify input collections for difference operation during Enrichment run configuration."""

    remove_input: CollectionSelector | None = None
    """Clusters from this collection will be removed from the other one."""
    from_input: CollectionSelector | None = None
    """Clusters from the other collection will be removed from this one."""


class DifferenceOperationInput(BaseModel):
    """Used to specify input collections for intersection operation during Enrichment run configuration."""

    name: str
    """Name of the intersection operation. Has to match the one defined in the Enrichment template."""
    inputs: DifferenceOperationInputs | None = None
    """Used to specify input collections for difference operation during Enrichment run configuration."""


class FoldChangeInputs(BaseModel):
    """Enrichment Fold change input operations that can be specified during the Enrichment run configuration.

    The clone collection inputs specified for this object will be used as inputs
    for the fold change measeurement computation.

    Example:
        Fold change ratio between results "A" and "B" after operation "C" is done equals 2.
    """

    from_input: CollectionSelector | None = None
    """An input clone collection.
        Serves as the `B` value in the `A`/`B` fold change ratio formula."""
    to_input: CollectionSelector | None = None
    """An input clone collection.
        Serves as the `A` value in the `A`/`B` fold change ratio formula."""


class FoldChangeInput(BaseModel):
    """Enrichment fold change annotation specification."""

    name: str
    """Name of the fold change annotation annotation. Has to match the one defined in the Enrichment template."""
    operation_name: str
    """Name of the operation this annotation belongs to. Has to match the one defined in the Enrichment template."""
    inputs: FoldChangeInputs | None = None
    """Input collections for the fold change."""


EnrichmentWorkInput = UnionOperationInput | IntersectionOperationInput | DifferenceOperationInput | FoldChangeInput
"""An input for Enrichment run configuration, used to provide data for the operations and annotations specified
    previously within the Enrichment template configuration.

    In general, they need to match the unique names specified within Enrichment templates in order to fill them
    with the clustered clone data - for info about the templates, see `enpi_api.l2.types.enrichment.EnrichmentTemplateOperation`.
"""


def transform_collection_selector(
    sel: CollectionSelector,
) -> openapi_client.MatchCollectionByItsID | openapi_client.MatchCollectionByItsName | openapi_client.MatchCollectionByTagValue:
    """Internal transform function for collection selectors.
    @private
    """
    if isinstance(sel, CollectionByIdSelector):
        return openapi_client.MatchCollectionByItsID(type="collection_id", value=int(sel.value))
    if isinstance(sel, CollectionByNameSelector):
        return openapi_client.MatchCollectionByItsName(type="collection_name", value=sel.value)
    if isinstance(sel, CollectionByTagValueSelector):
        return openapi_client.MatchCollectionByTagValue(
            type="collection_tag_value", value=openapi_client.MatchCollectionByTagValueValue(tag_id=sel.tag_id, tag_value=str(sel.tag_value))
        )
    else:
        assert_never(sel)


def transform_operation_input(input_value: EnrichmentWorkInput) -> openapi_client.EnrichmentWorkInputsInner:
    """Internal transform function for operation inputs.
    @private
    """
    if isinstance(input_value, UnionOperationInput):
        return openapi_client.EnrichmentWorkInputsInner(
            openapi_client.UnionOperationInputs(
                name=input_value.name,
                type=EnrichmentOperationType.UNION,
                inputs=[openapi_client.UnionOperationInputsInputsInner(transform_collection_selector(x)) for x in input_value.inputs],
            )
        )
    elif isinstance(input_value, IntersectionOperationInput):
        return openapi_client.EnrichmentWorkInputsInner(
            openapi_client.IntersectionOperationInputs(
                name=input_value.name,
                type=EnrichmentOperationType.INTERSECTION,
                inputs=[openapi_client.UnionOperationInputsInputsInner(transform_collection_selector(x)) for x in input_value.inputs],
            )
        )
    elif isinstance(input_value, DifferenceOperationInput):
        return openapi_client.EnrichmentWorkInputsInner(
            openapi_client.DifferenceOperationInputs(
                name=input_value.name,
                type=EnrichmentOperationType.DIFFERENCE,
                inputs=openapi_client.DifferenceOperationInputsInputs(
                    **{
                        "remove": openapi_client.DifferenceOperationInputsInputsRemove(transform_collection_selector(input_value.inputs.remove_input))
                        if input_value.inputs is not None and input_value.inputs.remove_input is not None
                        else None,
                        "from": openapi_client.DifferenceOperationInputsInputsRemove(transform_collection_selector(input_value.inputs.from_input))
                        if input_value.inputs is not None and input_value.inputs.from_input is not None
                        else None,
                    }
                ),
            )
        )
    elif isinstance(input_value, FoldChangeInput):
        inputs = input_value.inputs
        assert inputs is not None

        return openapi_client.EnrichmentWorkInputsInner(
            openapi_client.FoldChangeAnnotationInputs(
                name=input_value.name,
                operation_name=input_value.operation_name,
                type=EnrichmentOperationType.FOLD_CHANGE,
                inputs=openapi_client.FoldChangeAnnotationInputsInputs(
                    **{
                        "from": openapi_client.DifferenceOperationInputsInputsRemove(transform_collection_selector(inputs.from_input))
                        if inputs.from_input is not None
                        else None,
                        "to": openapi_client.DifferenceOperationInputsInputsRemove(transform_collection_selector(inputs.to_input))
                        if inputs.to_input is not None
                        else None,
                    }
                ),
            )
        )
    else:
        assert_never(input_value)


class EnrichmentExportMode(str, Enum):
    """Mode of Enrichment export that determines the shape and content of the final file."""

    CLONES = "clones"
    """All clones from each cluster will be exported."""
    REPRESENTATIVES = "representatives"
    """Within each cluster, every unique CDR/FR sequence will be tallied and the most abundant sequence for each region will be chosen."""
    CONSENSUS = "consensus"
    """The clone abundance will be used to choose a representative from each cluster."""
