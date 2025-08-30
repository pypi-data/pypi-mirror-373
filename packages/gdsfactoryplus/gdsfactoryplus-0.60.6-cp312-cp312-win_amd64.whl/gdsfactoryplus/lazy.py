"""Lazy module imports."""

from __future__ import annotations

from collections.abc import Callable
from types import ModuleType
from typing import Any

__all__ = ["lazy_import", "lazy_setattr", "lazy_get"]

CACHE = {}
SETATTR_CACHE = {}


def lazy_import(module_name: str, *callables: str) -> Any:
    """Lazily import a module."""
    if not callables:
        return lazy_module(module_name)
    if len(callables) == 1:
        return lazy_callable(module_name, callables[0])
    return [lazy_callable(module_name, fn) for fn in callables]


def lazy_module(module_name: str) -> LazyModule | ModuleType:
    """Lazily import a module."""
    if module_name not in CACHE:
        CACHE[module_name] = LazyModule(module_name)
    return CACHE[module_name]


def lazy_get(obj: Any) -> Any:
    """Get the underlying object of a lazy import."""
    if isinstance(obj, LazyModule | LazyCallable):
        return obj.unlazy()
    return obj


def lazy_callable(module_name: str, function_name: str) -> LazyCallable | Callable:
    """Lazily import a function."""
    if (module_name, function_name) not in CACHE:
        CACHE[module_name, function_name] = LazyCallable(module_name, function_name)
    return CACHE[module_name, function_name]


def lazy_setattr(
    module_with_attrs: str,
    value: Any,
) -> None:
    """Lazily set an attribute on a LazyModule."""
    parts = module_with_attrs.split(".")
    module = parts[0]
    attrs = parts[1:]
    if not attrs:
        return
    if module not in SETATTR_CACHE:
        SETATTR_CACHE[module] = {}
    SETATTR_CACHE[module][tuple(attrs)] = value


class LazyModule:
    """A class to lazily import modules."""

    def __init__(self, module_name: str) -> None:
        """Lazily imported module."""
        self.module_name = module_name
        self._module = None
        self._delayed_attrs = {}

    def unlazy(self) -> ModuleType:
        if self._module is None:
            import importlib

            self._module = CACHE[self.module_name] = importlib.import_module(
                self.module_name
            )

            if self.module_name in SETATTR_CACHE:
                for attrs, value in SETATTR_CACHE[self.module_name].items():
                    temp = self._module
                    for attr in attrs[:-1]:
                        temp = getattr(temp, attr)
                    setattr(temp, attrs[-1], value)
                del SETATTR_CACHE[self.module_name]
        return self._module

    def __getattr__(self, item: Any) -> Any:
        return getattr(self.unlazy(), item)


class LazyCallable:
    """A class to lazily call a function."""

    def __init__(self, module_name: str, function_name: str) -> None:
        """Lazily callable function."""
        self.module_name = module_name
        self.function_name = function_name
        self._func = None

    def unlazy(self) -> Callable:
        if self._func is None:
            import importlib

            module = importlib.import_module(self.module_name)
            self._func = CACHE[self.module_name, self.function_name] = getattr(
                module, self.function_name
            )
        return self._func

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the lazily imported function."""
        return self.unlazy()(*args, **kwargs)
