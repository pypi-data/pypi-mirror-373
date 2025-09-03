import pytest
from ghoshell_container import Container, Provider, Bootstrapper, IoCContainer


class _Foo:

    def __init__(self):
        self.foo = 0


class _FooBootstrapper(Bootstrapper):

    def __init__(self, count=1):
        self.count = count

    def bootstrap(self, container: IoCContainer) -> None:
        container.force_fetch(_Foo).foo += self.count


def test_bootstrap():
    c = Container()
    c.bind(_Foo, _Foo)

    c.add_bootstrapper(_FooBootstrapper())

    c.bootstrap()

    assert c.force_fetch(_Foo).foo is 1


def test_bootstrap_with_callable():
    c = Container()
    c.bind(_Foo, _Foo)

    def init_foo(foo: _Foo):
        foo.foo = 2

    # bootstrap will call the init_foo by container.call
    c.add_bootstrapper(init_foo)

    c.bootstrap()
    assert c.force_fetch(_Foo).foo is 2


def test_boostrap_and_shutdown():
    c = Container()
    c.bind(_Foo, _Foo)
    with c:
        assert c.force_fetch(_Foo) is not None

    # not allow to use it again
    with pytest.raises(RuntimeError):
        c.force_fetch(_Foo)


def test_boostrap_with_shutdown():
    c = Container()
    c.bind(_Foo, _Foo)

    def init_foo(foo: _Foo):
        foo.foo = 2

    def shutdown_foo(foo: _Foo):
        foo.foo = 0

    c.add_bootstrapper(init_foo)
    c.add_shutdown(shutdown_foo)

    c.bootstrap()
    foo1 = c.force_fetch(_Foo)
    assert foo1.foo is 2

    c.shutdown()
    assert foo1.foo is 0
