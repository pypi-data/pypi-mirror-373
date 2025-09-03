from ghoshell_container import Container
from abc import ABC, abstractmethod
import pytest


class _Foo(ABC):
    pass


class _Bar(_Foo):
    pass


class _Baz:
    pass


def test_fetch():
    container = Container()
    bar = _Bar()
    container.set(_Foo, bar)

    assert container.fetch(_Foo) is bar
    assert container.force_fetch(_Foo) is bar


def test_fetch_exception():
    container = Container()
    container.set(_Foo, _Baz())

    with pytest.raises(TypeError):
        container.fetch(_Foo)
        assert isinstance(container[_Foo], _Baz)


def test_fetch_non_existent():
    container = Container()
    container.set(_Foo, _Baz())

    assert container.fetch(_Baz) is None
    with pytest.raises(KeyError):
        # force fetch raise exception when not bound
        container.force_fetch(_Baz)
