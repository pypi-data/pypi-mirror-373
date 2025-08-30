from typing import Any
from typing import Callable
from typing import Type


def unavailable_function(ex: Exception) -> Callable[..., Any]:
    """Return a function that raises the given exception when called."""

    def _raiser(*args: Any, **kwargs: Any) -> Any:
        raise ex

    _raiser.__unavailable__ = True
    return _raiser


class UnavailableObject:
    """Object placeholder that raises an exception on any attribute access."""

    __unavailable__ = True

    def __init__(self, ex: Exception) -> None:
        self.__ex = ex

    def __getattr__(self, name: str) -> Any:
        if name in ("__func__", "_is_coroutine_marker", "_is_coroutine"):
            # Allow monkey patching for tests
            return super().__getattr__(name)
        raise self.__ex


def unavailable_class(ex: Exception) -> Type[Any]:
    """Return a class that raises the given exception on instantiation."""

    class _Unavailable:
        __unavailable__ = True

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ex

    return _Unavailable


def unavailable_type(ex: Exception) -> Type[Any]:
    """Return a type placeholder that raises the given exception on instantiation."""
    return unavailable_class(ex)


def unavailable_module(ex: Exception) -> Any:
    """Return an object acting like an unavailable module, raising on attribute access."""
    return UnavailableObject(ex)


def is_available(obj: Any) -> bool:
    """Check if an object is marked as unavailable."""
    return not getattr(obj, "__unavailable__", False)
