from __future__ import annotations

import re
from typing import Annotated, Any, Tuple, Optional

from pydantic import GetCoreSchemaHandler, ValidationInfo
from pydantic import AfterValidator
from pydantic_core import CoreSchema, core_schema


_PARTICIPANT_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_SEGMENT_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_HOST_SEGMENT_RE = re.compile(r"^[A-Za-z0-9.-]+$")  # Allow dots for host parts
_POOL_WILDCARD = "*"  # Only * allowed for pool definitions


class FameAddress(str):
    """
    A validated Fame address string.
    """

    def __new__(cls, value: str) -> "FameAddress":
        """Create a new FameAddress with validation."""
        # Validate the address format by parsing it (this will raise if invalid)
        parse_address(value)
        return super().__new__(cls, value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        str_schema = core_schema.str_schema()
        return core_schema.with_info_after_validator_function(
            _make_fame_address_with_info, str_schema
        )


def _validate_participant(name: str) -> None:
    if not _PARTICIPANT_RE.fullmatch(name):
        raise ValueError(
            "Participant must match [A-Z a-z 0-9 _ -]+ : {!r}".format(name)
        )


def _validate_host(host: str, allow_wildcards: bool = False) -> None:
    """Validate host-like part of address. Wildcards allowed only in logical contexts."""
    if not host:
        return

    # Split host into segments separated by dots
    segments = host.split(".")
    for i, segment in enumerate(segments):
        if not segment:  # Empty segment
            raise ValueError(f"Empty host segment in {host!r}")

        # Check wildcards
        if segment == _POOL_WILDCARD:
            # Allow wildcards in leftmost position for pool addresses like math@*.fame.fabric
            if i != 0:
                raise ValueError(f"Wildcard '*' must be leftmost segment in: {host!r}")
            continue

        if not _HOST_SEGMENT_RE.match(segment):
            raise ValueError(f"Bad host segment {segment!r} - use A-Za-z0-9.-")


def _validate_path(path: str) -> None:
    """Validate path part of address. Wildcards are NOT allowed in paths."""
    if not path:
        return

    if path == "/":
        return

    if not path.startswith("/"):
        path = "/" + path

    stripped = path.lstrip("/")
    parts = stripped.split("/") if stripped else []

    # Check segments - no wildcards allowed in paths
    for seg in parts:
        if seg == _POOL_WILDCARD:
            raise ValueError(f"Wildcards not allowed in path segments: {path!r}")
        if not _SEGMENT_RE.match(seg):
            raise ValueError(f"Bad segment {seg!r} - use A-Za-z0-9._-")


def parse_address(address: str) -> Tuple[str, str]:
    """
    Parse a FAME address supporting both host-like and path-like notation.

    Formats supported:
    - 'participant@/path'           (traditional path-only)
    - 'participant@host.name'       (host-only)
    - 'participant@host.name/path'  (host with path)
    - 'participant@*.host.name'     (pool address with leftmost wildcard)

    Rules:
    - participant: [A-Z a-z 0-9 _ -]+
    - host: dot-separated segments [A-Za-z0-9.-]+, wildcards (*) allowed in leftmost position only
    - path: '/' seg ('/' seg)*, NO wildcards allowed in path segments
    - At least one of host or path must be present

    Returns:
        Tuple of (participant, combined_location) where combined_location
        preserves the original format for backward compatibility.
    """
    at = address.rfind("@")
    if at == -1:
        raise ValueError("Missing '@' in address: {!r}".format(address))

    name, location = address[:at], address[at + 1 :]
    _validate_participant(name)

    if not location:
        raise ValueError("Location part cannot be empty")

    # Determine if this is host-only, path-only, or host+path
    if location.startswith("/"):
        # Traditional path-only format: participant@/path
        _validate_path(location)
    elif "/" in location:
        # Host with path format: participant@host.name/path
        host_part, path_part = location.split("/", 1)
        _validate_host(host_part, allow_wildcards=True)
        _validate_path("/" + path_part)
    else:
        # Host-only format: participant@host.name or participant@*.host.name
        _validate_host(location, allow_wildcards=True)

    return name, location


def parse_address_components(address: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Parse a FAME address into its constituent components.

    Returns:
        Tuple of (participant, host, path) where:
        - participant: always present
        - host: present if host-like notation used
        - path: present if path-like notation used
        - At least one of host or path will be non-None
    """
    at = address.rfind("@")
    if at == -1:
        raise ValueError("Missing '@' in address: {!r}".format(address))

    name, location = address[:at], address[at + 1 :]
    _validate_participant(name)

    if not location:
        raise ValueError("Location part cannot be empty")

    # Determine format and extract components
    if location.startswith("/"):
        # Traditional path-only format: participant@/path
        _validate_path(location)
        return name, None, location
    elif "/" in location:
        # Host with path format: participant@host.name/path
        host_part, path_part = location.split("/", 1)
        path_part = "/" + path_part  # Restore leading slash
        _validate_host(host_part, allow_wildcards=True)
        _validate_path(path_part)
        return name, host_part, path_part
    else:
        # Host-only format: participant@host.name or participant@*.host.name
        _validate_host(location, allow_wildcards=True)
        return name, location, None


def format_address(name: str, location: str) -> FameAddress:
    """
    Create a FAME address from participant and location.

    Args:
        name: participant name
        location: either path (/path), host (host.name), or host/path (host.name/path)
                 Wildcards allowed in host part only (*.host.name)
    """
    _validate_participant(name)

    # Validate the location part based on its format
    if location.startswith("/"):
        # Path-only format
        _validate_path(location)
    elif "/" in location:
        # Host with path format
        host_part, path_part = location.split("/", 1)
        _validate_host(host_part, allow_wildcards=True)
        _validate_path("/" + path_part)
    else:
        # Host-only format
        _validate_host(location, allow_wildcards=True)

    return FameAddress(f"{name}@{location}")


def format_address_from_components(
    name: str, host: Optional[str] = None, path: Optional[str] = None
) -> FameAddress:
    """
    Create a FAME address from separate components.

    Args:
        name: participant name
        host: optional host part (e.g., "fame.fabric", "child.fame.fabric", "*.fame.fabric")
        path: optional path part (e.g., "/", "/api/v1") - NO wildcards allowed in paths

    At least one of host or path must be provided.
    """
    _validate_participant(name)

    if not host and not path:
        raise ValueError("At least one of host or path must be provided")

    if host:
        _validate_host(host, allow_wildcards=True)
    if path:
        _validate_path(path)

    if host and path:
        # Both present: host/path format
        location = f"{host}{path}"
    elif host:
        # Host only
        location = host
    else:
        # Path only
        location = path

    return FameAddress(f"{name}@{location}")


def make_fame_address(raw: str) -> FameAddress:
    # validation happens inside
    name, location = parse_address(raw)
    return FameAddress(f"{name}@{location}")


def _make_fame_address_with_info(raw: str, info: ValidationInfo) -> FameAddress:
    """
    Adapter so we can keep using make_fame_address(raw: str) -> FameAddress
    with the new two-arg validator API.
    """
    return make_fame_address(raw)


ValidatedFameAddress = Annotated[FameAddress, AfterValidator(make_fame_address)]
