from __future__ import annotations

import inspect
from typing import Type, Callable, Optional
from functools import wraps
from ghoshell_container.abcd import INSTANCE, FactoryFunc, Provider, IoCContainer, BINDING
from contextvars import ContextVar

__all__ = [
    'provide',
    'get_caller_info',
    'get_container',
    'set_container',
    'is_builtin_type',
    'fetch',
    'make',
    'depends',
]

container_var = ContextVar('ghoshell_container', default=None)


def fetch(contract: type[INSTANCE]) -> INSTANCE:
    """
    fetch the implement of the contract
    """
    return get_container().force_fetch(contract)


def make(contract: type[INSTANCE], **kwargs) -> INSTANCE:
    """
    make an instance of the contract
    """
    return get_container().make(contract, **kwargs)


def set_container(container: IoCContainer) -> None:
    container_var.set(container)


def get_container() -> IoCContainer | None:
    return container_var.get()


def get_caller_info(backtrace: int = 1, with_full_file: bool = False) -> str:
    """
    get the filename:line from the backtrace caller
    """
    stack = inspect.stack()
    # 获取调用者的上下文信息
    if backtrace > len(stack) - 1:
        backtrace = len(stack) - 1
    caller_frame_record = stack[backtrace]
    frame = caller_frame_record[0]
    info = inspect.getframeinfo(frame)
    filename = info.filename
    if not with_full_file:
        filename = filename.split("/")[-1]
    return f"{filename}:{info.lineno}"


class FactoryProvider(Provider):

    def __init__(self, contract: Type[INSTANCE], factory: FactoryFunc, singleton: bool, kwargs: dict | None):
        if not callable(factory):
            raise TypeError("factory must be callable")
        self._contract = contract
        self._factory = factory
        self._singleton = singleton
        self._kwargs = kwargs or {}

    def singleton(self) -> bool:
        return self._singleton

    def contract(self) -> Type[INSTANCE]:
        return self._contract

    def factory(self, con: IoCContainer) -> Optional[INSTANCE]:
        return con.call(self._factory, **self._kwargs)


class ClassProvider(Provider):
    def __init__(self, contract: Type[INSTANCE], bound: Type[INSTANCE], singleton: bool, kwargs: dict | None):
        if not issubclass(bound, contract):
            raise TypeError(f"bound must be a subclass of {contract}")
        self._contract = contract
        self._bound = bound
        if not issubclass(self._bound, self._contract):
            raise TypeError(f"bound must be a subclass of {self._bound}")
        self._singleton = singleton
        self._kwargs = kwargs or {}

    def singleton(self) -> bool:
        return self._singleton

    def contract(self) -> Type[INSTANCE]:
        return self._contract

    def factory(self, con: IoCContainer) -> INSTANCE:
        if self._contract is self._bound:
            return con.new(self._contract, **self._kwargs)
        return con.make(self._bound, **self._kwargs)


def provide(
        contract: Type[INSTANCE],
        singleton: bool = True,
        lineinfo: str = "",
        kwargs: dict | None = None,
) -> Callable[[BINDING], Provider]:
    """
    helper function to generate provider with factory.
    can be used as a decorator.
    """
    if not lineinfo:
        lineinfo = get_caller_info(2)

    def wrapper(binding: BINDING) -> Provider:
        if isinstance(binding, Provider):
            return binding
        elif isinstance(binding, type):
            if issubclass(binding, contract):
                provider = ClassProvider(contract, binding, singleton, kwargs)
            else:
                raise TypeError(f"factory must be a subclass of {contract}, {binding} given")
        else:
            provider = FactoryProvider(contract, binding, singleton, kwargs)
        provider.registered_at = lineinfo
        return provider

    return wrapper


def depends(func: Callable) -> Callable:
    """
    function decorator
    """

    @wraps(func)
    def wrapped(*args, **kwargs):
        container = get_container()
        return container.call(func, *args, **kwargs)

    return wrapped


def is_builtin_type(val) -> bool:
    if not isinstance(val, type):
        return False
    elif val.__module__ in ("builtins", "__builtin__", "types"):
        return True
    return False
