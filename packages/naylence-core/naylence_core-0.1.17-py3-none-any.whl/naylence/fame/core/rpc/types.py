from typing import Any, Generic, Literal, TypeVar, cast
from pydantic import BaseModel, Field

from naylence.fame.core.util.id_generator import generate_id


class JSONRPCMessage(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: int | str | None = Field(default_factory=generate_id)


P = TypeVar("P")


class JSONRPCRequest(JSONRPCMessage, Generic[P]):
    """A JSON-RPC request with a typed `params` payload."""

    # jsonrpc: Literal["2.0"] = "2.0"
    method: Any
    params: P = Field(default_factory=lambda: cast(P, {}))


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Any | None = None


class JSONRPCResponse(JSONRPCMessage):
    result: Any | None = None
    error: JSONRPCError | None = None
