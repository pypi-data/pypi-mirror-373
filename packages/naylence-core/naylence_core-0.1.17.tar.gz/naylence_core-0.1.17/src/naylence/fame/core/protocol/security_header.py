from typing import Optional
from pydantic import BaseModel, Field


DEFAULT_SIGNATURE_ALGORITHM = "EdDSA"
DEFAULT_ENC_ALG = "ECDH-ES+A256GCM"


class SignatureHeader(BaseModel):
    alg: Optional[str] = None  # DEFAULT_SIGNATURE_ALGORITHM
    kid: Optional[str] = Field(default=None, description="Key id")
    val: str


class EncryptionHeader(BaseModel):
    alg: Optional[str] = DEFAULT_ENC_ALG
    kid: Optional[str] = Field(default=None, description="Key id")
    val: str


class SecurityHeader(BaseModel):
    """The only thing that travels over Fame connections."""

    sig: Optional[SignatureHeader] = Field(
        default=None,
        description="Signature header",
    )

    enc: Optional[EncryptionHeader] = Field(
        default=None,
        description="Encryption header",
    )
