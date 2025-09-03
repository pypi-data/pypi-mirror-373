from typing import Optional, Protocol, runtime_checkable

from .address import FameAddress


@runtime_checkable
class Addressable(Protocol):
    @property
    def address(self) -> Optional[FameAddress]: ...

    @address.setter
    def address(self, address): ...
