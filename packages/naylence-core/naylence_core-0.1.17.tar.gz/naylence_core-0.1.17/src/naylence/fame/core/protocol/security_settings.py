"""
Security profile definitions for negotiating cryptographic settings between nodes.
"""

from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class SigningMaterial(StrEnum):
    """Types of cryptographic evidence used for signing envelopes."""

    RAW_KEY = "raw-key"  # Default: JWK-based signing
    X509_CHAIN = "x509-chain"  # CA-signed certificate chain for signing


class SecuritySettings(BaseModel):
    """
    Negotiated security settings for node signing material.
    This model is extensible - new fields can be added without breaking compatibility.
    """

    signing_material: SigningMaterial = Field(
        default=SigningMaterial.RAW_KEY,
        description="Type of cryptographic evidence used for signing envelopes.",
    )

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",  # Allow future extensions
    )
