from __future__ import annotations

from contextlib import AbstractAsyncContextManager, asynccontextmanager
from abc import ABC, abstractmethod
from contextvars import ContextVar
from typing import Any, AsyncIterator, Optional

from naylence.fame.core.address.address import FameAddress
from naylence.fame.core.fame_config import FameConfig
from naylence.fame.core.handlers.handlers import FameMessageHandler
from naylence.fame.core.protocol.envelope import (
    FameEnvelope,
    create_fame_envelope,
)
from naylence.fame.core.protocol.frames import DataFrame
from naylence.fame.core.service.fame_service import FameService
from naylence.fame.core.util.constants import DEFAULT_INVOKE_TIMEOUT_MILLIS
from naylence.fame.factory import (
    ExtensionManager,
    create_default_resource,
    create_resource,
)


_FABRIC_STACK: ContextVar[list["FameFabric"]] = ContextVar("_FABRIC_STACK", default=[])


def reset_fabric_stack() -> None:
    """
    *Testing utility*: clear the stack for the current task.
    """
    _FABRIC_STACK.set([])


class FameFabric(ABC):
    # ----- abstract interface --------------------------------------------------

    @abstractmethod
    async def send(self, envelope: FameEnvelope) -> None: ...

    async def send_message(
        self,
        address: FameAddress | str,
        message: Any,
    ) -> None:
        await self.send(
            create_fame_envelope(
                to=FameAddress(address), frame=DataFrame(payload=message)
            )
        )

    @abstractmethod
    async def invoke(
        self,
        address: FameAddress,
        method: str,
        params: dict[str, Any],
        timeout_ms: int = DEFAULT_INVOKE_TIMEOUT_MILLIS,
    ) -> Any: ...

    @abstractmethod
    async def invoke_by_capability(
        self,
        capabilities: list[str],
        method: str,
        params: dict[str, Any],
        timeout_ms: int = DEFAULT_INVOKE_TIMEOUT_MILLIS,
    ) -> Any: ...

    @abstractmethod
    async def invoke_stream(
        self,
        address: FameAddress,
        method: str,
        params: dict[str, Any],
        timeout_ms: int = DEFAULT_INVOKE_TIMEOUT_MILLIS,
    ) -> AsyncIterator[Any]: ...

    @abstractmethod
    async def invoke_by_capability_stream(
        self,
        capabilities: list[str],
        method: str,
        params: dict[str, Any],
        timeout_ms: int = DEFAULT_INVOKE_TIMEOUT_MILLIS,
    ) -> Any: ...

    @abstractmethod
    async def subscribe(
        self,
        sink_address: FameAddress,
        handler: FameMessageHandler,
        name: Optional[str] = None,
    ) -> None: ...

    @abstractmethod
    async def serve(
        self,
        service: FameService,
        service_name: Optional[str] = None,
    ) -> FameAddress: ...

    @abstractmethod
    def resolve_service_by_capability(self, capability: str) -> FameService: ...

    # ----- optional lifecycle hooks -------------------------------------------

    async def start(self) -> None: ...

    async def stop(self) -> None: ...

    # ----- internal state ------------------------------------------------------

    _started: bool = False
    _stopped: bool = False
    _ctx_token = None  # ContextVar token for stack pop

    # ----- async-context-manager ----------------------------------------------

    async def __aenter__(self) -> "FameFabric":
        if self._ctx_token is not None:
            raise RuntimeError("Cannot re-enter the same FameFabric instance")

        # push-on-stack
        stack = _FABRIC_STACK.get()
        self._ctx_token = _FABRIC_STACK.set([*stack, self])

        # start (idempotent)
        if not self._started:
            await self.start()
            self._started = True

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        original_exc = exc_val  # preserve body exception, if any
        try:
            if not self._stopped:
                await self.stop()
                self._stopped = True
        except Exception as stop_err:
            # Chain shutdown failure onto the original body error if both exist
            if original_exc is None:
                raise
            raise stop_err from original_exc
        finally:
            if self._ctx_token is not None:
                _FABRIC_STACK.reset(self._ctx_token)
                self._ctx_token = None
        # Propagate body exception (do not suppress)
        return False

    @classmethod
    def current(cls) -> "FameFabric":
        """
        Return the FameFabric at the top of the task-local stack, or raise.
        Mirrors :meth:`create`.
        """
        stack = _FABRIC_STACK.get()
        if not stack:
            raise RuntimeError("No FameFabric active in this context")
        return stack[-1]

    # ----- async factory -------------------------------------------------------

    @classmethod
    def create(cls, **opts: Any) -> AbstractAsyncContextManager["FameFabric"]:
        # 1️⃣  canonicalise opts → FameFabricConfig
        root_config = opts.get("root_config", None)
        fabric_config: Optional[Any] = None
        fame_config = None
        if root_config:
            if isinstance(root_config, dict):
                fame_config = FameConfig.model_validate(root_config)
                fabric_config = fame_config.fabric
            elif isinstance(root_config, FameConfig):
                fame_config = root_config
                fabric_config = fame_config.fabric

        # 2️⃣  delegate to the real constructor
        return cls.from_config(fabric_config, **opts)

    @classmethod
    def from_config(
        cls, cfg: Optional[Any] = None, **kwargs: Any
    ) -> AbstractAsyncContextManager["FameFabric"]:
        """
        Build and manage a FameFabric using the `ResourceFactory` registry
        (see `create_resource`).

        """

        from naylence.fame.core.fame_fabric_factory import FameFabricFactory

        @asynccontextmanager
        async def _ctx():
            # 🔑  single line: resolve factory & create concrete fabric

            ExtensionManager.lazy_init(
                group="naylence.fabric", base_type=FameFabricFactory
            )
            if cfg:
                fabric = await create_resource(FameFabricFactory, cfg, **kwargs)
            else:
                fabric = await create_default_resource(FameFabricFactory, **kwargs)
                assert fabric, "No default FameFabricFactory registered"

            async with fabric:  # delegates to __aenter__/__aexit__
                yield fabric

        return _ctx()

    @classmethod
    def get_or_create(cls, **opts: Any) -> AbstractAsyncContextManager["FameFabric"]:
        """
        If there's already a Fabric on the stack, yield it without starting or stopping.
        Otherwise, delegate to create() as before.
        """
        stack = _FABRIC_STACK.get()
        if stack:
            # return a no-op async contextmanager around the existing fabric
            @asynccontextmanager
            async def _noop():
                yield stack[-1]

            return _noop()
        return cls.create(**opts)
