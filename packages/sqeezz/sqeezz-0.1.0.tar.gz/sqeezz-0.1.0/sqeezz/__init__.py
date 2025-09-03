from contextlib import contextmanager
from functools import wraps
from importlib import import_module
from inspect import iscoroutinefunction, signature
from typing import Any, Callable, Generator

__version__ = "0.1.0"

_refs = {}
_group_name = 'default'


class _Builder:

    def __init__(self, name: str):
        self.name = name
        self._refs = _refs

    def add_ref(self, ref: Callable[..., Any] | type) -> '_Builder':
        self.add_named_ref(ref.__name__, ref)

        return self

    def add_named_ref(self, name: str, ref: Any) -> '_Builder':
        if self.name not in self._refs:
            self._refs[self.name] = {}

        self._refs[self.name][name] = ref

        return self

    def lazy_add_ref(self, ref_name: str) -> '_Builder':
        self.add_named_ref(ref_name, import_module(ref_name))

        return self


class Using:

    def __init__(self, name: str):
        self._refs = _refs
        self._name = name

    @property
    def get(self) -> Any:
        return self._refs[_group_name][self._name]


def builder(name: str = 'default') -> _Builder:
    return _Builder(name)


def using(name: str) -> Any:
    _using = Using(name)
    return _using.get


def group(group_name: str, func: Callable[..., Any]) -> Callable[..., Any]:
    if iscoroutinefunction(func):

        @wraps(func)
        async def async_inner(*args: list[Any], **kwargs: dict[str, Any]):
            global _group_name

            original_group_name = _group_name
            _group_name = group_name
            value = await func(*args, **kwargs)
            _group_name = original_group_name
            return value

        async_inner.__signature__ = signature(func)
        return async_inner

    @wraps(func)
    def inner(*args: list[Any], **kwargs: dict[str, Any]):
        global _group_name

        original_group_name = _group_name
        _group_name = group_name
        value = func(*args, **kwargs)
        _group_name = original_group_name
        return value

    inner.__signature__ = signature(func)
    return inner


@contextmanager
def group_switcher(group_name: str) -> Generator[Any, Any, Any]:
    global _group_name
    original_group_name = _group_name
    _group_name = group_name
    yield
    _group_name = original_group_name
