"""
Helper functions for JSON-RPC 2.0 request/response framing, parsing, and serialization.
"""

from typing import Any, Dict, Optional, Mapping, Union

from naylence.fame.core.rpc.types import JSONRPCRequest, JSONRPCResponse, JSONRPCError
from naylence.fame.core.util.id_generator import generate_id


def make_request(
    method: str,
    params: Optional[Dict[str, Any]] = None,
    id: Optional[Union[str, int]] = None,
) -> dict[str, Any]:
    """
    Construct a JSON-RPC 2.0 request payload.

    :param method: Name of the RPC method.
    :param params: Parameters for the RPC call.
    :param id: Optional unique identifier. If omitted, a UUID4 string is generated.
    :return: A dict ready for serialization into a JSON-RPC 2.0 request.
    """
    request_id = id or generate_id()
    req = JSONRPCRequest(id=request_id, method=method, params=params)
    # model_dump preserves field ordering and types
    return req.model_dump(by_alias=True)


def parse_request(payload: Mapping[str, Any]) -> JSONRPCRequest:
    """
    Validate and parse a JSON-RPC 2.0 request payload into a Pydantic model.

    :param payload: The raw dict from an incoming frame or transport.
    :return: A JSONRPCRequest instance.
    """
    return JSONRPCRequest.model_validate(payload, by_alias=True)


def make_response(
    id: Union[str, int],
    result: Any = None,
    error: Optional[Any] = None,
) -> dict[str, Any]:
    """
    Construct a JSON-RPC 2.0 response payload, either successful or error.

    :param id: Identifier matching the original request.
    :param result: The result of the RPC method, if successful.
    :param error: A dict with "code", "message", and optional "data" if an error occurred.
    :return: A dict ready for serialization into a JSON-RPC 2.0 response.
    """
    if error is not None:
        # Accept either a JSONRPCError instance or a raw dict
        err = error if isinstance(error, JSONRPCError) else JSONRPCError(**error)
        resp = JSONRPCResponse(id=id, error=err)
    else:
        resp = JSONRPCResponse(id=id, result=result)
    return resp.model_dump(by_alias=True)


def parse_response(payload: Mapping[str, Any]) -> JSONRPCResponse:
    """
    Validate and parse a JSON-RPC 2.0 response payload into a Pydantic model.

    :param payload: The raw dict from an incoming frame or transport.
    :return: A JSONRPCResponse instance.
    """
    return JSONRPCResponse.model_validate(payload, by_alias=True)
