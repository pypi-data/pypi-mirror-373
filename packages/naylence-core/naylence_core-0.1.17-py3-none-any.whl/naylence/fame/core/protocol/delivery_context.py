from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from naylence.fame.core.protocol.origin_type import DeliveryOriginType
from naylence.fame.core.protocol.response_type import FameResponseType


class AuthorizationContext(BaseModel):
    """
    Enhanced authorization context supporting 2-step auth process.

    Step 1 (Authentication): Validates credentials and populates this context
    Step 2 (Authorization): Uses this context to authorize specific operations
    """

    # Authentication results
    authenticated: bool = Field(
        default=False, description="Whether authentication succeeded"
    )
    authorized: bool = Field(
        default=False, description="Whether authorization succeeded"
    )

    principal: Optional[str] = Field(
        default=None, description="Authenticated principal/user ID"
    )
    claims: Dict[str, Any] = Field(default_factory=dict, description="Token claims")

    # Authorization results
    granted_scopes: List[str] = Field(
        default_factory=list, description="Granted permission scopes"
    )
    restrictions: Dict[str, Any] = Field(
        default_factory=dict, description="Authorization restrictions"
    )

    # Context metadata
    auth_method: Optional[str] = Field(
        default=None, description="Authentication method used"
    )
    expires_at: Optional[datetime] = Field(
        default=None, description="When authorization expires"
    )

    def has_scope(self, scope: str) -> bool:
        """Check if a specific scope is granted"""
        return scope in self.granted_scopes

    def has_any_scope(self, scopes: List[str]) -> bool:
        """Check if any of the specified scopes are granted"""
        return any(scope in self.granted_scopes for scope in scopes)

    def is_valid(self) -> bool:
        """Check if authorization context is still valid"""
        if not self.authenticated:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True


class SecurityContext(BaseModel):
    """Security-related context for message delivery"""

    # Crypto level classification for inbound messages
    inbound_crypto_level: Optional[Any] = Field(
        default=None,
        description="Classified crypto level of the inbound message (CryptoLevel enum)",
    )

    # Signature tracking for inbound messages
    inbound_was_signed: Optional[bool] = Field(
        default=None,
        description="Whether the inbound message was signed (for signature mirroring)",
    )

    # Channel encryption tracking
    crypto_channel_id: Optional[str] = Field(
        default=None,
        description="ID of the virtual secure channel used for message delivery",
    )

    authorization: Optional[AuthorizationContext] = Field(
        default=None,
        description="Authorization context containing claims and permissions",
    )


class FameDeliveryContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    from_system_id: Optional[str] = Field(
        default=None, description="Delivery source system id"
    )

    from_connector: Optional[Any] = Field(
        default=None, description="Delivery connector"
    )

    origin_type: Optional[DeliveryOriginType] = Field(
        default=None,
        description="Where this envelope came from: downstream, upstream, or local",
    )

    # Security context for cryptographic and channel information
    security: Optional[SecurityContext] = Field(
        default=None,
        description="Security-related context including crypto level and channel information",
    )

    meta: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Ad-hoc metadata for the delivery.",
    )

    stickiness_required: Optional[bool] = Field(
        default=None,
        description="Whether this delivery requires stickiness. When True, the delivery should use sticky routing even if not explicitly configured.",
    )

    sticky_sid: Optional[str] = Field(
        default=None,
        description="Original client session ID for sticky routing. Set when stickiness is requested to preserve the client's session identifier for AFT token generation.",
    )

    expected_response_type: FameResponseType = Field(
        default=FameResponseType.NONE,
        description="Expected response type for the delivery.",
    )


def local_delivery_context(
    system_id: Optional[str] = None,
) -> FameDeliveryContext:
    return FameDeliveryContext(
        from_system_id=system_id,
        origin_type=DeliveryOriginType.LOCAL,
    )
