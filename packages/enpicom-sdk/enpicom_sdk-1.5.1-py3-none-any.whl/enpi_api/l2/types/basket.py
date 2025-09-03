from enum import Enum
from typing import NewType

from enpi_api.l1 import openapi_client
from enpi_api.l2.types.sequence import Chain
from enpi_api.l2.types.tag import TagId
from enpi_api.l2.types.user import UserId
from enpi_api.l2.util.from_raw_model import FromRawModel

BasketId = NewType("BasketId", int)
"""Unique identifier of a Basket."""


class Basket(FromRawModel[openapi_client.Basket]):
    """A single Basket info."""

    id: BasketId
    """Unique identifier of a Basket."""
    name: str
    """Name of a Basket."""
    shared: bool
    """Determines if a Basket is visible to other users in the organization."""
    user_id: UserId
    """Unique identifier of a user which created given Basket."""

    @classmethod
    def _build(cls, raw: openapi_client.Basket) -> "Basket":
        assert raw.id is not None
        assert raw.user_id is not None
        return cls(
            id=BasketId(raw.id),
            name=str(raw.name),
            shared=bool(raw.shared),
            user_id=UserId(raw.user_id),
        )


class BasketExportFormat(str, Enum):
    """Format of the result file of a Basket clones export."""

    TSV = "tsv"
    FASTA = "fasta"


class FastaExportHeadersConfig(FromRawModel[openapi_client.StartFastaClonesExportRequestBodyFastaConfigHeaders]):
    """Configuration of the FASTA sequence headers that are written in Basket FASTA export flow."""

    include_unique_clone_id: bool
    """Determines if clone IDs will be included in the FASTA sequence headers."""
    include_unique_sequence_id: bool
    """Determines if sequence IDs will be included in the FASTA sequence headers."""
    include_chain: bool
    """Determines if sequence Chain Tag will be included in FASTA sequence headers."""
    tags: list[TagId]
    """Unique identifiers of tags that are meant to be included in FASTA sequence headers."""

    @classmethod
    def _build(cls, raw: openapi_client.StartFastaClonesExportRequestBodyFastaConfigHeaders) -> "FastaExportHeadersConfig":
        return cls(
            include_unique_clone_id=raw.include_unique_clone_id,
            include_unique_sequence_id=raw.include_unique_sequence_id,
            include_chain=raw.include_chain,
            tags=[TagId(tag_id) for tag_id in raw.tags if tag_id is not None],
        )

    def to_api_payload(self) -> openapi_client.StartFastaClonesExportRequestBodyFastaConfigHeaders:
        return openapi_client.StartFastaClonesExportRequestBodyFastaConfigHeaders(
            include_unique_clone_id=self.include_unique_clone_id,
            include_unique_sequence_id=self.include_unique_sequence_id,
            include_chain=self.include_chain,
            tags=[int(tag_id) for tag_id in self.tags],
        )


class FastaExportConfig(FromRawModel[openapi_client.StartFastaClonesExportRequestBodyFastaConfig]):
    """Full configuration of Basket FASTA export."""

    headers: FastaExportHeadersConfig
    """The configuration of FASTA sequence headers."""
    sequence: list[TagId]
    """Entries representing sequences (lines) written in the FASTA file."""
    chains: list[Chain]
    """Which chains need to be exported (if found in the clone)."""

    @classmethod
    def _build(cls, raw: openapi_client.StartFastaClonesExportRequestBodyFastaConfig) -> "FastaExportConfig":
        return cls(
            headers=FastaExportHeadersConfig.from_raw(raw.headers),
            sequence=[TagId(int(tag)) for tag in raw.sequence],
            chains=[Chain(chain.lower()) for chain in raw.chains],
        )

    def to_api_payload(self) -> openapi_client.StartFastaClonesExportRequestBodyFastaConfig:
        return openapi_client.StartFastaClonesExportRequestBodyFastaConfig(
            headers=self.headers.to_api_payload(), sequence=[int(tag) for tag in self.sequence], chains=[str(chain.value) for chain in self.chains]
        )


def fasta_config(
    sequence: list[TagId] = [],
    include_chain_header: bool = True,
    include_unique_clone_id_header: bool = True,
    include_unique_sequence_id_header: bool = False,
    headers: list[TagId] = [],
    chains: list[Chain] = [],
) -> FastaExportConfig:
    """A utility function used for building a Basket FASTA export configuration from user input.

    Args:
        include_unique_clone_id_header (bool): determines if Unique Clone Identifier will be included in FASTA sequence headers.
        include_unique_sequence_id_header (bool): determines if Unique Sequence Identifier will be included in FASTA sequence headers.
        include_chain_header (bool): determines if sequence Chain will be included in FASTA sequence headers.
        header_tags (list[TagId]): tags that are meant to be included in FASTA sequence headers, they will be displayed with their key and their value.
        sequences (dict[Chain, list[FastaExportSequenceRegion]): entries representing sequences (lines) written in the FASTA file:
            e.g. in case of two clones, each with a heavy sequence, a `{Chain.HEAVY: [FastaExportSequenceRegion.CDR3_AMINO_ACIDS]}`
            object will result in two lines written in the FASTA file. Specifying multiple sequence regions for a single Chain will
            result in concatenation of those sequences.
    """

    return FastaExportConfig(
        headers=FastaExportHeadersConfig(
            include_unique_clone_id=include_unique_clone_id_header,
            include_unique_sequence_id=include_unique_sequence_id_header,
            include_chain=include_chain_header,
            tags=headers,
        ),
        sequence=sequence,
        chains=chains,
    )
