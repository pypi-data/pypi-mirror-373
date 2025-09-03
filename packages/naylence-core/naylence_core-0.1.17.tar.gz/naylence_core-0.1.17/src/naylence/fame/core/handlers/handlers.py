from typing import Any, Awaitable, Callable, Optional, TYPE_CHECKING
from pydantic import BaseModel

from naylence.fame.core.protocol.delivery_context import FameDeliveryContext
from naylence.fame.core.protocol.envelope import FameEnvelope

if TYPE_CHECKING:
    from typing import Union


class FameMessageResponse(BaseModel):
    """Response containing an envelope to be delivered."""

    envelope: FameEnvelope
    context: Optional[FameDeliveryContext] = None


# Handler type definitions using forward references to avoid circular imports
FameMessageHandler = Callable[[Any], Awaitable["Union[Any, FameMessageResponse, None]"]]

FameEnvelopeHandler = Callable[
    [FameEnvelope, Optional[FameDeliveryContext]],
    Awaitable["Union[FameMessageResponse, None]"],
]

# Updated RPC handler that can return a result directly or a FameMessageResponse
FameRPCHandler = Callable[
    [str, Optional[dict[str, Any]]], Awaitable["Union[Any, FameMessageResponse, None]"]
]
