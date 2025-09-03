"""
Message containers for binding channels that preserve delivery context.
"""

from typing import Optional, Union

from pydantic import BaseModel

from naylence.fame.core.protocol.delivery_context import FameDeliveryContext
from naylence.fame.core.protocol.envelope import FameEnvelope


class FameChannelMessage(BaseModel):
    """
    Container for messages sent through binding channels.

    This allows us to preserve delivery context while maintaining
    backward compatibility with direct envelope messages.
    """

    envelope: FameEnvelope
    context: Optional[FameDeliveryContext] = None


# Type alias for messages that can be sent through binding channels
FameBindingChannelMessage = Union[FameEnvelope, FameChannelMessage]


def create_channel_message(
    envelope: FameEnvelope, context: Optional[FameDeliveryContext] = None
) -> FameBindingChannelMessage:
    """
    Create a channel message, using the wrapped form only when context is present.

    This preserves backward compatibility by sending raw envelopes when no context
    is provided, but wraps them when context needs to be preserved.
    """
    if context is not None:
        return FameChannelMessage(envelope=envelope, context=context)
    else:
        return envelope


def extract_envelope_and_context(
    message: FameBindingChannelMessage,
) -> tuple[FameEnvelope, Optional[FameDeliveryContext]]:
    """
    Extract envelope and context from a binding channel message.

    Returns:
        tuple of (envelope, context) where context may be None
    """
    if isinstance(message, FameChannelMessage):
        return message.envelope, message.context
    elif isinstance(message, FameEnvelope):
        return message, None
    else:
        raise TypeError(f"Unexpected message type in binding channel: {type(message)}")
