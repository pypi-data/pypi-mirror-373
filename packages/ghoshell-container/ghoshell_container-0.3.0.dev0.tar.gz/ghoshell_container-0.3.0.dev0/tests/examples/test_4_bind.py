import pytest
from ghoshell_container import Container

container = Container()


class _Foo:
    pass


class _Bar:
    def __init__(self, foo: _Foo):
        self.foo = foo


class _Baz(_Foo):
    pass


class _Cat:

    def __init__(self, bar: _Bar, a: int):
        self.bar = bar
        self.a = a


@container.factory(_Foo)
def make_foo() -> _Foo:
    return _Foo()


def make_foo2() -> _Foo:
    return _Foo()


def test_bind_decorator():
    assert isinstance(container.force_fetch(_Foo), _Foo)


def test_bind_with_singleton():
    c = Container()
    c.bind(_Foo, _Foo())
    assert c.bound(_Foo)
    assert isinstance(container.force_fetch(_Foo), _Foo)


def test_bind_with_singleton_factory():
    c = Container()

    # bind with factory
    c.bind(_Foo, make_foo2)

    foo = c.get(_Foo)
    foo2 = c.get(_Foo)
    assert isinstance(foo, _Foo)
    assert foo is foo2


def test_bind_with_injection():
    c = Container()
    c.set(_Foo, _Foo())
    c.bind(_Bar)
    assert isinstance(c.get(_Bar), _Bar)
    assert isinstance(c.get(_Bar).foo, _Foo)


def test_bind_but_not_singleton():
    c = Container()

    c.bind(_Foo, make_foo2, singleton=False)

    foo = c.get(_Foo)
    foo2 = c.get(_Foo)
    # make twice
    assert foo is not foo2


def test_bind_with_subclass():
    c = Container()
    # bind with subclass
    c.bind(_Foo, _Baz)
    assert isinstance(c.get(_Foo), _Baz)
    assert isinstance(c.force_fetch(_Foo), _Foo)


def test_bind_none():
    c = Container()
    # bind itself
    c.bind(_Foo)

    assert isinstance(container.force_fetch(_Foo), _Foo)


def test_bind_with_invalid_subclass():
    c = Container()
    with pytest.raises(TypeError):
        c.bind(_Foo, _Bar)


def test_bind_with_kwargs():
    c = Container()
    c.bind(_Cat, kwargs=dict(a=1))
    assert isinstance(c.get(_Cat), _Cat)
    assert c.get(_Cat).a is 1
