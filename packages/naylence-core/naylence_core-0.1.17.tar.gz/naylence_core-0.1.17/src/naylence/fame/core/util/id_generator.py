from argparse import ArgumentParser
import base64
import hashlib
import os
import pathlib
import secrets
import socket
import sys
import uuid
from typing import Iterable, Union, cast

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Base64-encoded blacklist of forbidden substrings
_BLACKLIST_ID_WORDS_B64 = [
    "c2hpdA==",
    "ZnVj",
    "ZnVr",
    "ZGFtbg==",
    "Yml0Y2g=",
    "YmFzdGFy",
    "YXNzaG9s",
    "Y3JhcA==",
    "ZGljaw==",
    "cGlzcw==",
    "Ym9sbG9jaw==",
    "cHVzcw==",
    "YnVnZ2Vy",
    "Ymxvb2Q=",
    "ZmFnZw==",
    "Y3VudA==",
    "Y3Vt",
]

_BLACKLIST_ID_WORDS = {
    base64.b64decode(b).decode("utf8").lower() for b in _BLACKLIST_ID_WORDS_B64
}


BytesLike = Union[str, bytes]


def _base62(n: int) -> str:
    """Integer → Base-62 string (no leading zeros)."""
    if n == 0:
        return "0"
    chars = []
    while n:
        n, rem = divmod(n, 62)
        chars.append(ALPHABET[rem])
    return "".join(reversed(chars))


def _encode_digest(digest: bytes, length: int) -> str:
    return _base62(int.from_bytes(digest, "big"))[:length]


# Any CLI flag that should NOT affect the fingerprint
_ARG_WHITELIST = {"--instance"}


def _canonical_argv() -> str:
    """
    Return a stable, order-insensitive representation of the *meaningful*
    command-line arguments (excluding noise flags).
    """
    # Re-parse only the flags we care about
    p = ArgumentParser(add_help=False)
    p.add_argument("--instance", default="")
    known, unknown = p.parse_known_args(sys.argv[1:])

    # Keep only unknown flags *not* in the whitelist, sort them for stability.
    stable_unknown = sorted(
        flag for flag in unknown if flag.startswith("--") and flag not in _ARG_WHITELIST
    )

    parts: list[str] = []
    if known.instance:
        parts.append(f"instance:{known.instance}")

    if stable_unknown:
        parts.append(f"flags:{' '.join(stable_unknown)}")

    # Normalize the entry script path
    entry_script = pathlib.Path(sys.argv[0]).resolve()
    parts.append(f"entry:{entry_script}")

    return "|".join(parts)


def default_node_fingerprint(extra_material: BytesLike | None = None) -> bytes:
    """Return host + code(+argv) fingerprint for deterministic node IDs."""
    # --- host part (unchanged) ---
    mac = uuid.getnode()
    if (mac >> 40) % 2 == 0:
        host_fp = f"mac:{mac:012x}"
    else:
        host_fp = f"hn:{socket.gethostname()}"

    # --- code + argv part ---
    code_fp = _canonical_argv()

    # --- optional caller-supplied salt ---
    if extra_material:
        if isinstance(extra_material, bytes):
            salt = extra_material.decode()
        else:
            salt = str(extra_material)
        salt_fp = f"salt:{salt}"
        blob = f"{host_fp}|{code_fp}|{salt_fp}"
    else:
        blob = f"{host_fp}|{code_fp}"

    return blob.encode()


def generate_id(
    length: int = 15,
    *,
    mode: str = "random",
    material: BytesLike | Iterable[BytesLike] | None = None,
    blacklist: set[str] = _BLACKLIST_ID_WORDS,
    hash_alg: str = "sha256",
) -> str:
    if mode not in {"random", "fingerprint"}:
        raise ValueError("mode must be 'random' or 'fingerprint'")

    if mode == "random":
        while True:
            candidate = "".join(secrets.choice(ALPHABET) for _ in range(length))
            if not any(bad in candidate.lower() for bad in blacklist):
                return candidate

    # -- deterministic path --
    if material is None:
        env_salt = os.getenv("FAME_NODE_ID_SALT", "")
        material = default_node_fingerprint(env_salt)

    if isinstance(material, (str, bytes)):
        material_bytes = material.encode() if isinstance(material, str) else material
    else:  # iterable
        joined = b"|".join(
            cast(
                Iterable[bytes],
                (m.encode() if isinstance(m, str) else m for m in material),
            )
        )
        material_bytes = joined

    digest = hashlib.new(hash_alg, material_bytes).digest()
    candidate = _encode_digest(digest, length)

    # Trim/extend to satisfy blacklist – rare for hashes but keep the loop:
    while any(bad in candidate.lower() for bad in blacklist):
        digest = hashlib.new(hash_alg, digest).digest()  # re-hash once
        candidate = _encode_digest(digest, length)

    return candidate
