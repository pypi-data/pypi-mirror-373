from typing import (
    Any,
    Awaitable,
    Generic,
    List,
    Optional,
    Protocol,
    TypeVar,
    cast,
    runtime_checkable,
)


from naylence.fame.core.address.address import FameAddress
from naylence.fame.core.handlers.handlers import FameRPCHandler, FameEnvelopeHandler
from naylence.fame.core.protocol.envelope import FameEnvelope
from naylence.fame.core.util.constants import (
    DEFAULT_INVOKE_TIMEOUT_MILLIS,
    DEFAULT_POLLING_TIMEOUT_MS,
)
from naylence.fame.factory import ResourceFactory


class InvokeProtocol(Protocol):
    def __call__(
        self,
        target_addr: FameAddress,
        method: str,
        params: dict[str, Any],
        timeout_ms: int = DEFAULT_INVOKE_TIMEOUT_MILLIS,
    ) -> Awaitable[Any]: ...


class InvokeByCapabilityProtocol(Protocol):
    def __call__(
        self,
        capabilties: list[str],
        method: str,
        params: dict[str, Any],
        timeout_ms: int = DEFAULT_INVOKE_TIMEOUT_MILLIS,
    ) -> Awaitable[Any]: ...


_P = TypeVar("_P", bound="FameService")


@runtime_checkable
class FameService(Protocol):
    @property
    def capabilities(self) -> Optional[List[str]]: ...

    @classmethod
    def remote_by_address(cls: type[_P], address: FameAddress, **kwargs: Any) -> _P:
        """
        Return a strongly-typed proxy bound to *address*.

        Example
        -------
        >>> calc = Calculator.remote(addr)        # calc: Calculator proxy
        >>> result = await calc.add(2, 3)
        """
        return cast(_P, FameServiceProxy(address=address, **kwargs))

    @classmethod
    def remote_by_capabilities(
        cls: type[_P], capabilities: list[str], **kwargs: Any
    ) -> _P:
        """
        Return a strongly-typed proxy bound to *address*.

        Example
        -------
        >>> calc = Calculator.remote(addr)        # calc: Calculator proxy
        >>> result = await calc.add(2, 3)
        """
        return cast(_P, FameServiceProxy(capabilities=capabilities, **kwargs))


class FameServiceFactory(ResourceFactory[FameService, Any]): ...


@runtime_checkable
class FameMessageService(FameService, Protocol):
    async def handle_message(
        self, envelope: FameEnvelope, context: Optional[Any] = None
    ) -> None: ...


@runtime_checkable
class FameRPCService(FameService, Protocol):
    async def handle_rpc_request(self, method: str, params: Any) -> Any: ...


class ServeProtocol(Protocol):
    async def __call__(
        self,
        service_name: str,
        handler: FameEnvelopeHandler,
        *,
        capabilities: list[str] | None = None,
        poll_timeout_ms: int | None = DEFAULT_POLLING_TIMEOUT_MS,
    ) -> FameAddress: ...


class ServeRPCProtocol(Protocol):
    async def __call__(
        self,
        service_name: str,
        handler: FameRPCHandler,
        *,
        capabilities: list[str] | None = None,
        poll_timeout_ms: int | None = DEFAULT_POLLING_TIMEOUT_MS,
    ) -> FameAddress: ...


class FameServiceProxy(FameService, Generic[_P]):
    def __init__(
        self,
        *,
        address: Optional[FameAddress] = None,
        capabilities: Optional[list[str]] = None,
        fabric: Optional[Any] = None,
        invoke: Optional[InvokeProtocol] = None,
        invoke_by_capability: Optional[InvokeByCapabilityProtocol] = None,
        timeout: int = DEFAULT_INVOKE_TIMEOUT_MILLIS,
        **kwargs,
    ):
        self._invoke = invoke or self._invoke_default
        self._invoke_by_capability = (
            invoke_by_capability or self._invoke_by_capability_default
        )

        self._fabric = fabric
        self._address = address
        self._capabilities = capabilities
        self._timeout = timeout

    @property
    def capabilities(self):
        return self._capabilities

    def _invoke_default(self, *args, **kwargs):
        from naylence.fame.core.fame_fabric import FameFabric

        fabric = self._fabric or FameFabric.current()
        return fabric.invoke(*args, **kwargs)

    def _invoke_by_capability_default(self, *args, **kwargs):
        from naylence.fame.core.fame_fabric import FameFabric

        fabric = self._fabric or FameFabric.current()
        return fabric.invoke_by_capability(*args, **kwargs)

    def __getattr__(self, method_name):
        async def method(*args, **kwargs):
            # If you passed exactly one dict, treat it as the full params
            if len(args) == 1 and not kwargs and isinstance(args[0], dict):
                params = args[0]
            else:
                # Otherwise, wrap posargs + kwargs in a single object
                params = {"args": args, "kwargs": kwargs}

            if self._address:
                return await self._invoke(
                    self._address, method_name, params, timeout_ms=self._timeout
                )
            elif self._capabilities:
                return await self._invoke_by_capability(
                    self._capabilities, method_name, params, timeout_ms=self._timeout
                )
            else:
                raise RuntimeError("This shouldn't happen")

        return method

    async def __call__(self, name: str, **kwargs):
        assert self._address
        """
        Generic RPC-by-name: invokes the special "__call__" RPC on the service.
        """
        params = {"name": name, "args": kwargs or {}}
        return await self._invoke(
            self._address,
            "__call__",
            params,
            timeout_ms=self._timeout,
        )
