from typing import Protocol

from naylence.fame.core.protocol.envelope import FameEnvelope


class SenderProtocol(Protocol):
    async def __call__(self, envelope: FameEnvelope) -> None: ...
