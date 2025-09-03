from typing import Protocol, runtime_checkable


@runtime_checkable
class Closeable(Protocol):
    async def close(self) -> None: ...
