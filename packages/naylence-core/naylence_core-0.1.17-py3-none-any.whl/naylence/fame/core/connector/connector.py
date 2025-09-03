from typing import Protocol, Optional

from naylence.fame.core.connector.connector_state import ConnectorState
from naylence.fame.core.handlers.handlers import FameEnvelopeHandler
from naylence.fame.core.protocol.channel_message import FameChannelMessage
from naylence.fame.core.protocol.delivery_context import AuthorizationContext
from naylence.fame.core.protocol.envelope import FameEnvelope


class FameConnector(Protocol):
    async def start(self, inbound_handler: FameEnvelopeHandler) -> None: ...

    async def stop(self) -> None: ...

    async def replace_handler(self, handler: FameEnvelopeHandler) -> None: ...

    async def send(self, envelope: FameEnvelope) -> None: ...

    async def close(
        self, code: Optional[int] = None, reason: Optional[str] = None
    ) -> None: ...

    async def push_to_receive(
        self, raw_or_envelope: bytes | FameEnvelope | FameChannelMessage
    ) -> None: ...

    @property
    def state(self) -> ConnectorState: ...

    @property
    def close_code(self) -> Optional[int]: ...

    @property
    def close_reason(self) -> Optional[str]: ...

    @property
    def last_error(self) -> Optional[BaseException]: ...

    @property
    def authorization_context(self) -> Optional[AuthorizationContext]: ...

    @authorization_context.setter
    def authorization_context(
        self, context: Optional[AuthorizationContext]
    ) -> None: ...
