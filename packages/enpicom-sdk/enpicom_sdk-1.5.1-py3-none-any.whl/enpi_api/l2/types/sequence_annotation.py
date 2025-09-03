from enum import Enum
from typing import Literal, NewType, cast

from pydantic import BaseModel

from enpi_api.l1 import openapi_client
from enpi_api.l2.types.file import FileId
from enpi_api.l2.types.tag import TagId
from enpi_api.l2.util.from_raw_model import FromRawModel

QualityControlTemplateId = NewType("QualityControlTemplateId", str)
"""The unique identifier of a quality control template."""


SequenceTemplateId = NewType("SequenceTemplateId", str)
"""The unique identifier of a sequence template."""


class SequencingMethod(str, Enum):
    single_end = "Single-End"
    paired_end = "Paired-End"


class SequenceTemplateSelector(FromRawModel[openapi_client.SequenceTemplateSelector]):
    """A selector to match a sequence template file by its ID.

    Args:
        value (FileId): The ID of the sequence template file to match.

    Example:
        To match a file by its ID, use the `SequenceTemplateSelector` class:

        ```python
        selector = SequenceTemplateSelector(
            value=FileId("570f0f8c-33c4-4d4d-905b-87f3637d49eb")
        )
        ```
    """

    type: Literal["file_id"] = "file_id"
    """Internal type used to recognize type of the object."""
    value: FileId
    """The ID of the sequence template file to match."""

    @classmethod
    def _build(cls, raw: openapi_client.SequenceTemplateSelector) -> "SequenceTemplateSelector":
        return cls(type="file_id", value=FileId(cast(openapi_client.MatchAFileByItsID, raw).value))


class SequenceTemplateConfig(FromRawModel[openapi_client.SequenceAnnotationWorkSequenceTemplatesInner]):
    """A configuration object specifying which files get assigned which sequence template.

    Args:
        selector (SequenceTemplateSelector): The selector to match the sequence template file.
        id (SequenceTemplateId): The ID of the sequence template to assign.
        version (int | None): The version of the sequence template to assign. If none, will default to the latest version.

    Example:
        Assume we have a sequence template with ID 1, and we have a file with ID "a".

        If we want to assign file "a" to use the sequence template with ID 1, the configuration would look like this:

        ```python
        config = SequenceTemplateConfig(
            # We select the file
            selector=SequenceTemplateSelector(value=FileId("570f0f8c-33c4-4d4d-905b-87f3637d49eb")),
            # And specify the sequence template to use
            id=SequenceTemplateId(1)
        )
        ```
    """

    selector: SequenceTemplateSelector
    """The selector to match the sequence template file."""
    id: SequenceTemplateId
    """The ID of the sequence template to assign."""
    version: int | None = None
    """The version of the sequence template to assign. If none, will default to the latest version."""

    @classmethod
    def _build(cls, raw: openapi_client.SequenceAnnotationWorkSequenceTemplatesInner) -> "SequenceTemplateConfig":
        return cls(
            selector=SequenceTemplateSelector.from_raw(raw.selector),
            id=SequenceTemplateId(raw.template_id),
            version=int(raw.template_version) if raw.template_version is not None else None,
        )


class SequenceTemplate(FromRawModel[openapi_client.SequenceTemplate]):
    """A sequence template describing the structure of a raw sequencing data read."""

    id: SequenceTemplateId
    """The unique identifier of a sequence template."""
    version: int
    """Version of a sequence template."""
    name: str
    """Name of a sequence template."""
    shared: bool
    """Whether the sequence template is shared with other users in the organization."""
    author: str
    """Sequence template's author's name."""
    created_at: str
    """Date of sequence template's creation."""
    updated_at: str
    """Date of sequence template's last update."""
    sequencing_method: SequencingMethod
    """Method used for sequencing"""

    @classmethod
    def _build(cls, raw: openapi_client.SequenceTemplate) -> "SequenceTemplate":
        return cls(
            id=SequenceTemplateId(raw.id),
            version=int(raw.version),
            name=str(raw.name),
            shared=bool(raw.shared),
            author=str(raw.author),
            created_at=str(raw.created_at),
            updated_at=str(raw.updated_at),
            sequencing_method=SequencingMethod(raw.sequencing_method),
        )


class QualityControlTemplate(FromRawModel[openapi_client.QualityControlTemplate]):
    """A quality control template specifying the strictness of Sequence Annotation."""

    id: QualityControlTemplateId
    """The unique identifier of a quality control template."""
    version: int
    """Version of a quality control template."""
    name: str
    """Name of a quality control template."""
    shared: bool
    """Whether the quality control template is shared within the organization."""
    author: str
    """Quality control template's author's name."""
    created_at: str
    """Date of quality control template's creation."""
    updated_at: str
    """Date of quality control template's last update."""

    @classmethod
    def _build(cls, raw: openapi_client.QualityControlTemplate) -> "QualityControlTemplate":
        return cls(
            id=QualityControlTemplateId(raw.id),
            version=int(raw.version),
            name=str(raw.name),
            shared=bool(raw.shared),
            author=str(raw.author),
            created_at=str(raw.created_at),
            updated_at=str(raw.updated_at),
        )


class CloneIdentifierExtractionSource(str, Enum):
    """Source from which the manually specified clone identifier
    should be extracted during the Sequence Annotation run."""

    FILENAME = "filename"
    """Extract the clone identifier from the filename."""
    HEADER = "header"
    """Extract the clone identifier from the sequence headers."""


class CloneIdentifierExtractionConfig(BaseModel):
    """The configuration for extracting clone identifiers from the input files.

    This only needs to be used when a sequence template has the option "Manually Specify Clone Identifier" enabled.

    Example:

        Assuming we have a filename structure that looks like this: `foo_clone_a_bar.fasta`, `bar_clone_b_foo.fasta`, and
        you want to extract the clone identifier `a` and `b` respectively, you can use the following `CloneIdentifierExtraction` configuration:

        ```python
        CloneIdentifierExtractionConfig(
            source=CloneIdentifierExtractionSource.FILENAME, # Extract from the filename
            delimiter="_", # Split the filename string by `_` characters
            index=2, # Select the third string part
            target_tag_id=TagId(1337)  # Use the tag ID you want to store the clone identifier in
        )
        ```
    """

    source: CloneIdentifierExtractionSource
    """The source to extract the clone identifier from."""
    delimiter: str | list[str]
    """The delimiter to split the source on.

    You can also specify multiple delimiters.

    Example:

        Assuming you have a header structure that looks like this: `>43370843|CloneId=Clone1|Heavy 1|Bmax=1.2`, and you
        want to extract the clone identifier `Clone1` you can use the following `CloneIdentifierExtractionConfig`:

        ```python
        CloneIdentifierExtractionConfig(
            source=CloneIdentifierExtractionSource.HEADER, # Extract from header
            delimiter=["CloneId=", "|"],
            # Because we have multiple delimiters, the first `43270843` is at index 0 because it is split by the `|`,
            # afterwards the `Clone1` is at index 1 because it is between the `CloneId=` and the next `|`.
            index=1, # Select the second string part
            target_tag_id=TagId(1337)  # Use the tag ID you want to store the clone ID in
        )
        ```

    """
    index: int
    """The index of the split to use as the clone identifier.
    Since this is an index, it is 0-based. So the first item is at index 0, the second at index 1, etc.
    """
    target_tag_id: TagId
    """The tag to store the extracted clone identifier in."""

    def to_api_payload(self) -> openapi_client.CloneIdToTagSpec:
        """@private"""
        return openapi_client.CloneIdToTagSpec(
            source=self.source.capitalize(),
            delimiter=self.delimiter if isinstance(self.delimiter, str) else "/".join(self.delimiter),
            index=self.index,
            target_tag_id=self.target_tag_id,
        )


class CorrectionRegion(str, Enum):
    FR1 = "FR1"
    CDR1 = "CDR1"
    FR2 = "FR2"
    CDR2 = "CDR2"
    FR3 = "FR3"
    CDR3 = "CDR3"
    FR4 = "FR4"


class CorrectionSettings(BaseModel):
    """The settings to correct or complete regions of sequences.

    Example:

        To complete the FR1 and FR4 regions and correct all regions (except CDR3 that is not a region that can be configured to be corrected),
        you can use the following `CorrectionSettings` configuration:

        ```python
        CorrectionSettings(
            should_complete_ends=True,
            regions=[
                CorrectionRegion.FR1,
                CorrectionRegion.CDR1,
                CorrectionRegion.FR2,
                CorrectionRegion.CDR2,
                CorrectionRegion.FR3,
                CorrectionRegion.CDR3,
                CorrectionRegion.FR4,
            ],
        )
        ```
    """

    should_complete_ends: bool
    """Whether to complete FR1 and FR4 region of sequences."""
    regions: list[CorrectionRegion]
    """The names of the regions to correct"""

    def to_api_payload(self) -> openapi_client.CorrectionSettings:
        return openapi_client.CorrectionSettings(should_complete_ends=self.should_complete_ends, regions=[i.value for i in self.regions])


class LiabilityType(str, Enum):
    UnpairedCys = "Unpaired Cys"
    TrpOxidation = "Trp oxidation"
    LysineGlycation = "Lysine Glycation"
    CD11cCD18Binding = "CD11c/CD18 binding"
    NlinkedGlycosylation = "N-linked glycosylation"
    AsnDeamidation = "Asn deamidation"
    NterminalGlutamate = "N-terminal glutamate"
    Fragmentation = "Fragmentation"
    MetOxidation = "Met oxidation"
    AspIsomerisation = "Asp isomerisation"
    IntegrinBinding = "Integrin binding"


class MutationAssaySettings(BaseModel):
    """The settings to use with a mutation assay experiment.

    Example:

        To filter out VDJ lengths that are not equal to the reference and to filter out non-synonymous mutations with a base quality below 30,
        you can use the following `MutationAssaySettings` configuration:

        ```python
        MutationAssaySettings(
            should_filter_vdj_length=True,
            mutation_base_quality_threshold=30,
        )
        ```
    """

    should_filter_vdj_length: bool
    """Whether to filter out reads when the VDJ length is unequal to the reference."""
    mutation_base_quality_threshold: int
    """The base quality threshold below which non-synonymous mutations are filtered out."""

    def to_api_payload(self) -> openapi_client.MutationAssaySettings:
        return openapi_client.MutationAssaySettings(
            should_filter_vdj_length=self.should_filter_vdj_length, mutation_base_quality_threshold=self.mutation_base_quality_threshold
        )
