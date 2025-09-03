from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Generic, Optional, Protocol, TypeVar, List, Union
from typing import Dict as _Dict

from pydantic import BaseModel, ConfigDict, Field, SerializationInfo, field_serializer
from pydantic.alias_generators import to_camel


from naylence.fame.core.address.address import FameAddress
from naylence.fame.core.protocol.flow import CreditUpdateFrame, FlowFlags
from naylence.fame.core.protocol.frames import (
    AddressBindFrame,
    AddressBindAckFrame,
    AddressUnbindFrame,
    AddressUnbindAckFrame,
    DataFrame,
    FameFrame,
    FameFrameUnion,
    KeyAnnounceFrame,
    KeyRequestFrame,
    NodeAttachFrame,
    NodeHeartbeatFrame,
    NodeHeartbeatAckFrame,
    NodeAttachAckFrame,
    NodeHelloFrame,
    NodeWelcomeFrame,
    DeliveryAckFrame,
    CapabilityAdvertiseFrame,
    CapabilityWithdrawFrame,
    CapabilityAdvertiseAckFrame,
    CapabilityWithdrawAckFrame,
    SecureOpenFrame,
    SecureAcceptFrame,
    SecureCloseFrame,
)
from naylence.fame.core.protocol.response_type import FameResponseType
from naylence.fame.core.protocol.security_header import SecurityHeader
from naylence.fame.core.util.id_generator import generate_id

T = TypeVar(
    "T",
    FameFrame,
    AddressBindFrame,
    AddressBindAckFrame,
    AddressUnbindFrame,
    AddressUnbindAckFrame,
    KeyAnnounceFrame,
    KeyRequestFrame,
    NodeHeartbeatFrame,
    NodeHeartbeatAckFrame,
    DataFrame,
    NodeAttachFrame,
    NodeAttachAckFrame,
    NodeHelloFrame,
    NodeWelcomeFrame,
    DeliveryAckFrame,
    CapabilityAdvertiseFrame,
    CapabilityWithdrawFrame,
    CapabilityAdvertiseAckFrame,
    CapabilityWithdrawAckFrame,
    SecureOpenFrame,
    SecureAcceptFrame,
    SecureCloseFrame,
)

AllFramesUnion = Union[FameFrameUnion, CreditUpdateFrame]

# define exactly what value types are allowed in meta
MetaValue = Union[
    str,
    int,
    float,
    bool,
    List[Union[str, int, float, bool]],
    _Dict[str, Union[str, int, float, bool]],
]


ENVELOPE_VERSION = "1.0"


class Priority(str, Enum):
    LOW = "low"  # bulk work, non-critical
    NORMAL = "normal"  # default
    HIGH = "high"  # time-sensitive
    SPECULATIVE = "speculative"  # race-style, best-effort


class FameEnvelope(BaseModel):
    """The only thing that travels over Fame connections."""

    version: Optional[str] = Field(default=ENVELOPE_VERSION)

    id: str = Field(
        default_factory=generate_id,
        description="Unique envelope identifier for de-duplication and tracing",
    )

    sid: Optional[str] = Field(
        default=None,
        description="Source system id, hash of the sender's physical path",
    )

    trace_id: Optional[str] = Field(
        default=None,
        description="Logical trace id for correlating related envelopes",
    )

    to: Optional[FameAddress] = Field(
        default=None,
        description="Destination address; if unset, uses capability routing",
    )

    reply_to: Optional[FameAddress] = Field(
        default=None,
        description="Address where receivers should send their response",
    )

    capabilities: Optional[List[str]] = Field(
        default=None,
        description="List of capability names this envelope is intended for",
    )

    rtype: Optional[FameResponseType] = Field(
        default=None,
        description="Expected response type for the envelope.",
    )

    corr_id: Optional[str] = Field(
        default=None,
        description="Correlation ID for tracking related envelopes",
    )

    flow_id: Optional[str] = Field(
        default=None,
        description="Logical stream identifier for handling backpressure",
    )

    seq_id: Optional[int] = Field(
        default=0,
        description="Monotonic counter per-sender to order envelopes if needed",
    )

    flow_flags: Optional[FlowFlags] = Field(
        default=FlowFlags.NONE,
        description="Flags controlling flow behavior (e.g., start/end of window)",
    )

    ttl: Optional[int] = Field(
        default=None,
        description="Time-to-live (in hops) after which the envelope is dropped",
    )

    priority: Optional[Priority] = Field(
        default=None,
        description="Delivery priority hint (e.g., low, normal, high)",
    )

    frame: AllFramesUnion = Field(
        ...,
        discriminator="type",
        description="The actual payload frame (e.g. DataFrame, NodeNodeHeartbeatFrame)",
    )

    ts: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the envelope was created",
    )

    sec: Optional[SecurityHeader] = Field(
        default=None,
        description="Optional security header",
    )

    aft: Optional[str] = Field(
        default=None,
        description=(
            "Node-signed affinity tag. JWS compact format. "
            "Sentinel verifies signature & expiry; routes accordingly."
        ),
    )

    # everything else ↓ should go into meta
    meta: Optional[Dict[str, MetaValue]] = Field(
        default=None,
        description=(
            "Extension metadata: kebab-case or dotted keys; values must be "
            "str, int, float, bool or small list thereof."
        ),
    )

    @field_serializer("ts")
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")

    @field_serializer("sec")
    def conditionally_mask_sec(
        self,
        v: Any,
        info: SerializationInfo,
    ) -> Any:
        if not info.context:
            return v
        safe_log = info.context.get("safe_log", False)
        if safe_log is True:
            return "<hidden>"

        return v

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


def create_fame_envelope(
    *,
    frame: AllFramesUnion,
    id: Optional[str] = None,
    sid: Optional[str] = None,
    trace_id: Optional[str] = None,
    to: Optional[FameAddress | str] = None,
    capabilities: Optional[list[str]] = None,
    response_type: Optional[FameResponseType] = None,
    reply_to: Optional[FameAddress] = None,
    flow_id: Optional[str] = None,
    window_id: Optional[int] = 0,
    flags: Optional[FlowFlags] = FlowFlags.NONE,
    corr_id: Optional[str] = None,
    timestamp: Optional[datetime] = None,
) -> FameEnvelope:
    env = FameEnvelope(
        id=id or generate_id(),
        sid=sid,
        trace_id=trace_id or generate_id(),
        to=FameAddress(to) if to else None,
        capabilities=capabilities,
        rtype=response_type,
        reply_to=reply_to,
        frame=frame,
        flow_id=flow_id,
        seq_id=window_id,
        flow_flags=flags,
        corr_id=corr_id,
        ts=timestamp or datetime.now(timezone.utc),
    )

    return env


def envelope_from_dict(data: dict[str, Any]) -> FameEnvelope:
    return FameEnvelope.model_validate(dict, by_alias=True)


class FameEnvelopeWith(FameEnvelope, Generic[T]):
    frame: T  # type: ignore


class EnvelopeFactory(Protocol):
    def create_envelope(
        self,
        *,
        frame: FameFrame,
        id: Optional[str] = None,
        trace_id: Optional[str] = None,
        to: Optional[FameAddress | str] = None,
        capabilities: Optional[list[str]] = None,
        reply_to: Optional[FameAddress] = None,
        flow_id: Optional[str] = None,
        window_id: Optional[int] = 0,
        flags: Optional[FlowFlags] = FlowFlags.NONE,
        timestamp: Optional[datetime] = None,
        corr_id: Optional[str] = None,
        response_type: Optional[FameResponseType] = None,
    ) -> FameEnvelope: ...
