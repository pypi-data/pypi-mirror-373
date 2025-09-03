from enum import Enum
from typing import Literal, NewType, NotRequired, TypedDict, Union

from pydantic import BaseModel

from enpi_api.l1 import openapi_client
from enpi_api.l2.types.tag import TagId
from enpi_api.l2.util.from_raw_model import FromRawModel

MlEndpointId = NewType("MlEndpointId", str)
"""The unique identifier of a ML endpoint."""

MlflowModelUri = NewType("MlflowModelUri", str)
"""The URI of a MLflow model."""

MlInvocationOutputKey = NewType("MlInvocationOutputKey", str)
"""The output key of a ML invocation."""

MlInvocationId = NewType("MlInvocationId", str)
"""The unique identifier of a ML invocation."""


class MlEndpoint(FromRawModel[openapi_client.MLModelEndpoint]):
    id: MlEndpointId
    display_name: str

    @classmethod
    def _build(cls, raw: openapi_client.MLModelEndpoint) -> "MlEndpoint":
        return cls(
            id=MlEndpointId(raw.id),
            display_name=raw.display_name,
        )


class MlInvocationStats(FromRawModel[openapi_client.GetMlInvocationStatsResponseBodyStatsInner]):
    endpoint_id: MlEndpointId
    display_name: str
    total_invocations: int
    success_ratio: float
    last_invoked_at: str
    invocations_last_24h: int
    invocations_last_7d: int
    invocations_last_1m: int

    @classmethod
    def _build(cls, raw: openapi_client.GetMlInvocationStatsResponseBodyStatsInner) -> "MlInvocationStats":
        return cls(
            endpoint_id=MlEndpointId(raw.endpoint_id),
            display_name=raw.display_name,
            total_invocations=raw.total_invocations,
            success_ratio=float(raw.success_ratio),
            last_invoked_at=str(raw.last_invoked_at),
            invocations_last_24h=raw.invocations_last_24h,
            invocations_last_7d=raw.invocations_last_7d,
            invocations_last_1m=raw.invocations_last_1m,
        )


class Chain(str, Enum):
    """Chain of a sequence."""

    ALPHA = "Alpha"
    BETA = "Beta"
    DELTA = "Delta"
    GAMMA = "Gamma"
    HEAVY = "Heavy"
    KAPPA = "Kappa"
    LAMBDA = "Lambda"


class MlInputMapItem(TypedDict):
    tag_id: TagId
    input_key: str
    chains: NotRequired[list[Chain]]


class MlParamMapItem(TypedDict):
    type: Union[Literal["numeric"], Literal["boolean"], Literal["text"]]
    input_key: str
    label: NotRequired[str]


class MlFileIntent(TypedDict):
    type: Literal["file"]
    filetype: str
    output_key: NotRequired[str]


class MlMetadataIntent(TypedDict):
    type: Literal["metadata"]
    chains: NotRequired[list[Chain]]
    output_key: NotRequired[str]
    tag_id: TagId


MlOutputIntent = MlFileIntent | MlMetadataIntent


class MlAwsEndpointConfig(TypedDict):
    endpoint_name: str
    iam_role_arn: str
    external_id: str
    region: str
    s3_input_path: str
    s3_output_path: str
    sqs_url: str


class MlEndpointSignature(TypedDict):
    key: str
    kind: str
    type: str


class MlInvocationStatus(str, Enum):
    """Status of a ML invocation."""

    Pending = "Pending"
    HandlingIntent = "HandlingIntent"
    Succeeded = "Succeeded"
    Failed = "Failed"


class MlInvocation(BaseModel):
    id: MlInvocationId
    ml_endpoint_id: MlEndpointId
    started_at: str
    completed_at: str | None
    status: MlInvocationStatus
