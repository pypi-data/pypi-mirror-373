from datetime import datetime
from enum import Enum
from typing import NewType

from pydantic import BaseModel

from enpi_api.l1 import openapi_client
from enpi_api.l2.types.collection import CollectionId, Receptor
from enpi_api.l2.types.tag import TagId
from enpi_api.l2.util.from_raw_model import FromRawModel

ClusterRunId = NewType("ClusterRunId", str)
"""The unique identifier of a Cluster run."""

ClusterId = NewType("ClusterId", int)
"""The identifier of a cluster, unique only within a given Cluster run."""


class ChainPercentageMatch(BaseModel):
    # IG
    Heavy: int | None = None
    Kappa: int | None = None
    Lambda: int | None = None
    # TR
    Alpha: int | None = None
    Beta: int | None = None
    Gamma: int | None = None
    Delta: int | None = None


class SequenceFeatureIdentities(FromRawModel[openapi_client.SequenceFeatureIdentities]):
    """Identities per chain.

    Identities used when clustering clones, applied to chosen Sequence Features.
    Mixing receptors (e.g. Heavy + Alpha) is not allowed.
    For TCR mixing Alpha/Beta with Gamma/Delta is not allowed.
    """

    Heavy: int | None = None
    """Identity value for Heavy chain (%)."""
    Lambda: int | None = None
    """Identity value for Lambda chain (%)."""
    Kappa: int | None = None
    """Identity value for Kappa chain (%)."""
    Alpha: int | None = None
    """Identity value for Alpha chain (%)."""
    Beta: int | None = None
    """Identity value for Beta chain (%)."""
    Gamma: int | None = None
    """Identity value for Gamma chain (%)."""
    Delta: int | None = None
    """Identity value for Delta chain (%)."""

    @classmethod
    def _build(cls, raw: openapi_client.SequenceFeatureIdentities) -> "SequenceFeatureIdentities":
        return cls(
            Heavy=raw.heavy if raw.heavy is not None else None,
            Kappa=raw.kappa if raw.kappa is not None else None,
            Lambda=raw.var_lambda if raw.var_lambda is not None else None,
            Alpha=raw.alpha if raw.alpha is not None else None,
            Beta=raw.beta if raw.beta is not None else None,
            Gamma=raw.gamma if raw.gamma is not None else None,
            Delta=raw.delta if raw.delta is not None else None,
        )

    def to_inner(self) -> openapi_client.SequenceFeatureIdentities:
        return openapi_client.SequenceFeatureIdentities(
            # Destructuring the dict here, because `lambda` is a troublesome name for a python class property
            **{
                "heavy": self.Heavy if self.Heavy is not None else None,
                "kappa": self.Kappa if self.Kappa is not None else None,
                "lambda": self.Lambda if self.Lambda is not None else None,
                "alpha": self.Alpha if self.Alpha is not None else None,
                "beta": self.Beta if self.Beta is not None else None,
                "gamma": self.Gamma if self.Gamma is not None else None,
                "delta": self.Delta if self.Delta is not None else None,
            }
        )


class AdditionalOptions(FromRawModel[openapi_client.ClusterAdditionalOptions]):
    """Additional Options for clustering configuration."""

    should_strip_special_chars: bool | None = None
    """Determines if asterisk (*) and underscore (_) characters should be removed from the amino acid sequence
        (during clustering only, the original sequence is not modified)."""
    should_remove_singletons: bool | None = None
    """Determines if singletons should be removed."""
    should_remove_non_productive_vdj: bool | None = None
    """Determines if sequences than contain Frameshifts or Stop Codons in the VDJ region should be discarded """
    should_remove_non_productive_cdr3: bool | None = None
    """Determines if sequences than contain Frameshifts or Stop Codons in the CDR3 region should be discarded."""
    should_remove_incomplete_vdj: bool | None = None
    """Determines if Sequences with incomplete VDJ region should be removed (during clustering only,
        the original sequence is not modified)."""

    @classmethod
    def _build(cls, raw: openapi_client.ClusterAdditionalOptions) -> "AdditionalOptions":
        return cls(
            should_strip_special_chars=raw.should_strip_special_chars,
            should_remove_singletons=raw.should_remove_singletons,
            should_remove_non_productive_vdj=raw.should_remove_non_productive_vdj,
            should_remove_non_productive_cdr3=raw.should_remove_non_productive_cdr3,
            should_remove_incomplete_vdj=raw.should_remove_incomplete_vdj,
        )

    def to_inner(self) -> openapi_client.ClusterAdditionalOptions:
        return openapi_client.ClusterAdditionalOptions(
            should_strip_special_chars=self.should_strip_special_chars,
            should_remove_singletons=self.should_remove_singletons,
            should_remove_non_productive_vdj=self.should_remove_non_productive_vdj,
            should_remove_non_productive_cdr3=self.should_remove_non_productive_cdr3,
            should_remove_incomplete_vdj=self.should_remove_incomplete_vdj,
        )


class ExportClustersMode(str, Enum):
    """Mode of export cluster that determines the shape and content of the final file."""

    CLONES = "clones"
    """Export will contain a Germline Sequence + all clones per cluster"""
    CONSENSUS = "consensus"
    """Export will contain a Germline Sequence + a representative clone per cluster"""
    REPRESENTATIVES = "representatives"
    """Export will contain a consensus clone per cluster"""


class ClusterRun(FromRawModel[openapi_client.ClusterRun]):
    """Cluster Run configuration."""

    id: ClusterRunId
    """Cluster run ID."""
    name: str
    """Cluster run name."""
    collection_ids: list[CollectionId]
    """Collections that were used in the Cluster run."""
    receptor: Receptor
    """Receptor that was picked for the Cluster run."""
    created_at: datetime
    """Cluster run creation date."""
    sequence_features: list[TagId]
    """Sequence features used for clustering."""
    identities: SequenceFeatureIdentities
    """Sequence identities per chains used for clustering."""
    match_tags: list[TagId] | None
    """Matching restrictions applied to sequences before clustering."""
    additional_options: AdditionalOptions | None
    """Additional Options for clustering configuration."""

    @classmethod
    def _build(cls, raw: openapi_client.ClusterRun) -> "ClusterRun":
        assert raw.created_at is not None

        return cls(
            id=ClusterRunId(raw.id),
            name=str(raw.name),
            collection_ids=[CollectionId(cid) for cid in raw.collection_ids],
            receptor=Receptor(raw.receptor),
            created_at=raw.created_at,
            sequence_features=[TagId(i) for i in raw.sequence_features if i is not None],
            identities=SequenceFeatureIdentities.from_raw(raw.identities),
            match_tags=[TagId(i) for i in (raw.match_tags or []) if i is not None],
            additional_options=AdditionalOptions.from_raw(raw.additional_options) if raw.additional_options is not None else None,
        )
