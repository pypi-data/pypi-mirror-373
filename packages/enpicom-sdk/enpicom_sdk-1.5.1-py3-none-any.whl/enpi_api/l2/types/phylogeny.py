from enum import Enum
from typing import NewType

from enpi_api.l1 import openapi_client
from enpi_api.l2.types.cluster import ClusterId, ClusterRunId
from enpi_api.l2.util.from_raw_model import FromRawModel

TreeId = NewType("TreeId", int)
"""The unique identifier of a phylogenetic tree."""


class PhylogenyType(str, Enum):
    """Type of a phylogenetic tree."""

    NUCLEOTIDE = "nucleotide"
    AMINO_ACID = "amino_acid"


class Phylogeny(FromRawModel[openapi_client.Phylogeny]):
    """A single amino acid or nucleotide phylogenetic tree."""

    cluster_run_id: ClusterRunId
    """The unique identifier of a Cluster run."""
    cluster_id: ClusterId
    """The identifier of a cluster, unique only within a given Cluster run."""
    tree_id: TreeId
    """The unique identifier of a phylogenetic tree."""
    newick: str
    """Tree's representation in Newick format."""
    type: PhylogenyType
    """Type of a phylogenetic tree."""

    @classmethod
    def _build(cls, raw: openapi_client.Phylogeny) -> "Phylogeny":
        return cls(
            cluster_run_id=ClusterRunId(raw.cluster_run_id),
            cluster_id=ClusterId(int(raw.cluster_id)),
            tree_id=TreeId(int(raw.tree_id)),
            newick=raw.newick,
            type=PhylogenyType.NUCLEOTIDE if raw.type == "nucleotide" else PhylogenyType.AMINO_ACID,
        )
