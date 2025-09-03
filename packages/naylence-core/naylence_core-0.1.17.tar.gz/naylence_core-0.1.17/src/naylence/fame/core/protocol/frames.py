import base64
from datetime import datetime, timezone
from typing import Literal, Mapping, Optional, Any, List, Sequence, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SerializationInfo,
    field_serializer,
    field_validator,
)
from pydantic.alias_generators import to_camel

from naylence.fame.core.address.address import FameAddress
from naylence.fame.core.protocol.origin_type import DeliveryOriginType
from naylence.fame.core.protocol.security_settings import SecuritySettings


class FameFrame(BaseModel):
    type: Any

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class DeliveryAckFrame(FameFrame):
    type: Literal["DeliveryAck"] = "DeliveryAck"

    ok: bool = True  # True ⇒ ACK, False ⇒ NACK
    code: str | None = None
    reason: str | None = None

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class Stickiness(BaseModel):
    """
    Stickiness negotiation payload used in both NodeAttach and NodeAttachAck.

    Directional semantics:
    - Child → Parent (NodeAttach): set 'mode' (preferred) and/or 'supported_modes'.
    - Parent → Child (NodeAttachAck): set 'enabled', 'mode' (negotiated), and optional 'ttl_sec'.

    All fields are optional except 'version' to keep backward compatibility.
    """

    # Preferred mechanism or negotiated mode: 'aft' (advanced) or 'attr' (simple)
    mode: Optional[Literal["aft", "attr"]] = Field(default=None)

    # Optional multi-mode advertisement from child; if present, 'mode' is the preferred one
    supported_modes: Optional[List[Literal["aft", "attr"]]] = Field(default=None)

    # Parent-side toggle when replying; ignored by child when advertising
    enabled: Optional[bool] = Field(default=None)

    # TTL hint for AFT-based stickiness; ignored for attribute mode
    ttl_sec: Optional[int] = Field(default=None)

    # Schema version for forward-compat negotiation
    version: int = Field(default=1)

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class AddressBindFrame(FameFrame):
    type: Literal["AddressBind"] = "AddressBind"
    address: FameAddress
    encryption_key_id: Optional[str] = None
    physical_path: Optional[str] = None
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class AddressBindAckFrame(DeliveryAckFrame):
    type: Literal["AddressBindAck"] = "AddressBindAck"  # type: ignore
    address: FameAddress

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class AddressUnbindFrame(FameFrame):
    type: Literal["AddressUnbind"] = "AddressUnbind"
    address: FameAddress

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class AddressUnbindAckFrame(DeliveryAckFrame):
    type: Literal["AddressUnbindAck"] = "AddressUnbindAck"  # type: ignore
    address: FameAddress

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class NodeHeartbeatFrame(FameFrame):
    type: Literal["NodeHeartbeat"] = "NodeHeartbeat"
    address: Optional[FameAddress] = None
    system_id: Optional[str] = None
    payload: Optional[Any] = None

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class NodeHeartbeatAckFrame(DeliveryAckFrame):
    type: Literal["NodeHeartbeatAck"] = "NodeHeartbeatAck"  # type: ignore
    address: Optional[FameAddress] = None
    routing_epoch: Optional[str] = None
    payload: Optional[Any] = None

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class DataFrame(FameFrame):
    type: Literal["Data"] = "Data"
    fid: Optional[str] = None
    codec: Optional[Literal["json", "b64"]] = None
    payload: Any
    pd: Optional[str] = None  # Payload digest only for encrypted data frames

    # Channel encryption fields
    cid: Optional[str] = Field(
        default=None, description="Channel ID for encrypted data frames"
    )
    nonce: Optional[bytes] = Field(
        default=None,
        description="Nonce for encrypted frames",
        min_length=12,
        max_length=12,
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )

    @field_serializer("nonce")
    def serialize_nonce(self, value: Optional[bytes]) -> Optional[str]:
        """Serialize nonce bytes to base64 string for JSON compatibility."""
        if value is None:
            return None
        return base64.b64encode(value).decode("ascii")

    @field_validator("nonce", mode="before")
    @classmethod
    def validate_nonce(cls, value: Any) -> Optional[bytes]:
        """Validate and convert nonce from base64 string to bytes."""
        if value is None:
            return None
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            try:
                decoded = base64.b64decode(value)
                if len(decoded) != 12:
                    raise ValueError(
                        f"Nonce must be exactly 12 bytes, got {len(decoded)}"
                    )
                return decoded
            except Exception as e:
                raise ValueError(f"Invalid base64 nonce: {e}")
        raise ValueError(f"Nonce must be bytes or base64 string, got {type(value)}")


class NodeHelloFrame(FameFrame):
    """
    If `system_id` is **None** or empty, the parent is expected to assign one
    and return it in `NodeWelcomeFrame.system_id`.
    """

    type: Literal["NodeHello"] = "NodeHello"

    # Final system_id for this node (might be newly assigned)
    system_id: str

    logicals: Optional[List[str]] = None
    capabilities: Optional[List[str]] = None
    supported_transports: Optional[List[str]] = None

    region_hint: Optional[str] = None

    instance_id: str

    security_settings: Optional[SecuritySettings] = Field(
        default=None, description="Desired security settings for the child node."
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class NodeWelcomeFrame(FameFrame):
    type: Literal["NodeWelcome"] = "NodeWelcome"

    system_id: str

    target_system_id: Optional[str] = None

    target_physical_path: Optional[str] = None

    instance_id: str

    assigned_path: Optional[str] = None

    accepted_capabilities: Optional[List[str]] = None

    accepted_logicals: Optional[List[str]] = None

    rejected_logicals: Optional[List[str]] = None

    connection_grants: Optional[List[Any]] = None

    expires_at: Optional[datetime] = None

    metadata: Optional[Mapping[str, Any]] = None

    reason: Optional[str] = None

    security_settings: Optional[SecuritySettings] = Field(
        default=None,
        description="Security settings the parent expects the child to follow.",
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class NodeAttachFrame(FameFrame):
    type: Literal["NodeAttach"] = "NodeAttach"

    origin_type: Optional[DeliveryOriginType] = (
        DeliveryOriginType.DOWNSTREAM
    )  # TODO: validate DOWNSTREAM or PEER only
    system_id: str
    instance_id: str
    assigned_path: Optional[str] = None
    capabilities: Optional[Sequence[str]] = None
    accepted_logicals: Optional[Sequence[str]] = Field(
        default=None,
    )

    keys: Optional[list[dict]] = Field(default=None)

    supported_inbound_connectors: Optional[List[dict[str, Any]]] = Field(
        default=None,
        description="List of inbound connector directives the child or peer supports "
        "for reverse connections initiated by the parent.",
    )

    # Optional stickiness payload used to advertise capabilities (child → parent)
    stickiness: Optional[Stickiness] = Field(
        default=None,
        description="Stickiness negotiation payload (advertisement when sent by child).",
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )

    @field_serializer("keys")
    def conditionally_mask_keys(
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


class NodeAttachAckFrame(DeliveryAckFrame):
    type: Literal["NodeAttachAck"] = "NodeAttachAck"  # type: ignore
    target_system_id: Optional[str] = Field(default=None)  # filled if success == True
    assigned_path: Optional[str] = Field(default=None)
    target_physical_path: Optional[str] = Field(default=None)
    routing_epoch: Optional[str] = Field(default=None)
    keys: Optional[list[dict]] = Field(default=None)
    expires_at: Optional[datetime] = Field(
        default=None
    )  # RFC 3339; optional lease time

    # Optional stickiness payload used to return negotiated policy (parent → child)
    stickiness: Optional[Stickiness] = Field(
        default=None,
        description="Stickiness negotiation payload (policy when sent by parent).",
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )

    @field_serializer("keys")
    def conditionally_mask_keys(
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


class CapabilityAdvertiseFrame(FameFrame):
    type: Literal["CapabilityAdvertise"] = "CapabilityAdvertise"
    capabilities: list[str]
    address: FameAddress

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class CapabilityAdvertiseAckFrame(DeliveryAckFrame):
    type: Literal["CapabilityAdvertiseAck"] = "CapabilityAdvertiseAck"  # type: ignore
    capabilities: list[str]
    address: FameAddress

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class CapabilityWithdrawFrame(FameFrame):
    type: Literal["CapabilityWithdraw"] = "CapabilityWithdraw"
    capabilities: list[str]
    address: FameAddress
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class CapabilityWithdrawAckFrame(DeliveryAckFrame):
    type: Literal["CapabilityWithdrawAck"] = "CapabilityWithdrawAck"  # type: ignore
    capabilities: list[str]
    address: FameAddress

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class KeyAnnounceFrame(FameFrame):
    type: Literal["KeyAnnounce"] = "KeyAnnounce"
    address: Optional[FameAddress] = None
    physical_path: str
    keys: list[dict]
    created: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Key creation timestamp",
    )
    expires: Optional[datetime] = Field(
        default=None,
        description="Key expiration timestamp",
    )

    @field_serializer("created", "expires")
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")

    @field_serializer("keys")
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


class KeyRequestFrame(FameFrame):
    """
    Downstream → upstream: “please send me the JWK for *kid* (and optionally
    for everything under *physical_path*).”
    """

    type: Literal["KeyRequest"] = "KeyRequest"
    kid: Optional[str] = None
    address: Optional[FameAddress] = None
    physical_path: Optional[str] = None


class SecureOpenFrame(FameFrame):
    """Client → Server: initiate overlay secure channel."""

    type: Literal["SecureOpen"] = "SecureOpen"
    cid: str = Field(description="Client-chosen str for the new channel")
    eph_pub: bytes = Field(
        description="32-byte X25519 public key", min_length=32, max_length=32
    )
    alg: str = Field(
        default="CHACHA20P1305", description="Channel encryption algorithm"
    )
    opts: int = Field(
        default=0, description="Bitfield for cipher-suite, PQ-hybrid flags, etc."
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )

    @field_serializer("eph_pub")
    def serialize_eph_pub(self, value: bytes) -> str:
        """Serialize ephemeral public key bytes to base64 string for JSON compatibility."""
        return base64.b64encode(value).decode("ascii")

    @field_validator("eph_pub", mode="before")
    @classmethod
    def validate_eph_pub(cls, value: Any) -> bytes:
        """Validate and convert ephemeral public key from base64 string to bytes."""
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            try:
                decoded = base64.b64decode(value)
                if len(decoded) != 32:
                    raise ValueError(
                        f"Ephemeral public key must be exactly 32 bytes, got {len(decoded)}"
                    )
                return decoded
            except Exception as e:
                raise ValueError(f"Invalid base64 ephemeral public key: {e}")
        raise ValueError(
            f"Ephemeral public key must be bytes or base64 string, got {type(value)}"
        )


class SecureAcceptFrame(DeliveryAckFrame):
    """Server → Client: accept or reject the channel."""

    type: Literal["SecureAccept"] = "SecureAccept"  # type: ignore
    cid: str  # Channel id, same as in SecureOpen
    eph_pub: bytes = Field(
        description="Server's 32-byte X25519 public key", min_length=32, max_length=32
    )
    alg: str = Field(
        default="CHACHA20P1305", description="Channel encryption algorithm"
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )

    @field_serializer("eph_pub")
    def serialize_eph_pub(self, value: bytes) -> str:
        """Serialize ephemeral public key bytes to base64 string for JSON compatibility."""
        return base64.b64encode(value).decode("ascii")

    @field_validator("eph_pub", mode="before")
    @classmethod
    def validate_eph_pub(cls, value: Any) -> bytes:
        """Validate and convert ephemeral public key from base64 string to bytes."""
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            try:
                decoded = base64.b64decode(value)
                if len(decoded) != 32:
                    raise ValueError(
                        f"Ephemeral public key must be exactly 32 bytes, got {len(decoded)}"
                    )
                return decoded
            except Exception as e:
                raise ValueError(f"Invalid base64 ephemeral public key: {e}")
        raise ValueError(
            f"Ephemeral public key must be bytes or base64 string, got {type(value)}"
        )


class SecureCloseFrame(FameFrame):
    """Either side → peer: clean shutdown or fatal error."""

    type: Literal["SecureClose"] = "SecureClose"
    cid: str  # Channel id, same as in SecureOpen
    reason: Optional[str] = Field(
        default=None, description="Human-friendly reason code"
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


# Union type for deserialization or isinstance checks
FameFrameUnion = Union[
    NodeWelcomeFrame,
    NodeAttachFrame,
    NodeAttachAckFrame,
    AddressBindFrame,
    AddressBindAckFrame,
    AddressUnbindFrame,
    AddressUnbindAckFrame,
    NodeHeartbeatFrame,
    NodeHeartbeatAckFrame,
    DataFrame,
    NodeHelloFrame,
    DeliveryAckFrame,
    CapabilityAdvertiseFrame,
    CapabilityWithdrawFrame,
    CapabilityAdvertiseAckFrame,
    CapabilityWithdrawAckFrame,
    KeyAnnounceFrame,
    KeyRequestFrame,
    SecureOpenFrame,
    SecureAcceptFrame,
    SecureCloseFrame,
]
