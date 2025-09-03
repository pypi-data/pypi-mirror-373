from typing import Any, Callable, TypeVar, overload

T = TypeVar("T")


class _Unset:
    pass


@overload
def map_key(conf: dict[str, Any], key: str) -> Any: ...


@overload
def map_key(conf: dict[str, Any], key: str, *, default: T) -> T: ...


@overload
def map_key(conf: dict[str, Any], key: str, *, decoder: Callable[[Any], T]) -> T: ...


@overload
def map_key(conf: dict[str, Any], key: str, *, decoder: Callable[[Any], T], default: T) -> T: ...


def map_key(
    conf: dict[str, Any], key: str, *, decoder: Callable[[Any], Any] = lambda v: v, default: Any = _Unset()
) -> Any:
    if key in conf:
        return decoder(conf[key])
    if isinstance(default, _Unset):
        raise ValueError(f"Unset config value for {key}")
    return default
