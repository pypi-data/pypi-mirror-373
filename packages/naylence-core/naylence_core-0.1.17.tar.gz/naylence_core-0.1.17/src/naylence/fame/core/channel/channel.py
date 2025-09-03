from typing import Any, Protocol


class Channel(Protocol):
    """
    A logical, transport-agnostic representation of a message channel.
    Can be adapted into consumer/system-bound read/write variants.
    """

    ...


class ReadChannel(Channel, Protocol):
    """
    A channel capable of reading messages.
    """

    async def receive(self, timeout: int = 5000) -> Any:
        """
        Pull the next available message. Returns None if no message is available.
        Implementations should return a dict with a unique 'id' field if acknowledgment is supported.
        """
        ...

    async def acknowledge(self, message_id: str) -> None:
        """
        Optional operation.
        Acknowledge a previously received message by its unique ID.
        This is only meaningful for backends that track delivery state.
        """
        ...


class WriteChannel(Channel, Protocol):
    """
    A channel capable of writing messages.
    """

    async def send(self, message: Any) -> None:
        """
        Send a message payload to the channel.
        Payload format is backend-specific but must be serializable.
        """
        ...


class ReadWriteChannel(ReadChannel, WriteChannel, Protocol):
    """
    A channel capable of both reading and writing.
    This is the most common case for two-way message delivery flows.
    """

    ...
