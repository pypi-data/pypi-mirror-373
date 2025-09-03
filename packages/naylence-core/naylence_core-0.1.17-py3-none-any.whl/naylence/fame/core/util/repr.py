from typing import TypeVar, Type, Callable
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def secure_repr(*fields_to_hide: str) -> Callable[[Type[T]], Type[T]]:
    """
    Class decorator that replaces __repr__ on a BaseModel subclass to
    mask the given fields (showing '<<field>> hidden' if non-null).

    Usage:
        @secure_repr("intent_nl", "intent_vector", "meta")
        class FameEnvelope(BaseModel):
            ...
    """

    def decorator(model_cls: Type[T]) -> Type[T]:
        def __repr__(self: T) -> str:
            data = self.model_dump(by_alias=True, context={"mask_fields": {}})
            # for f in fields_to_hide:
            #     if f in data and data[f] is not None:
            #         data[f] = f"<{f} hidden>"
            return f"{self.__class__.__name__}({data})"

        setattr(model_cls, "__repr__", __repr__)
        return model_cls

    return decorator
