from typing import Type

from ghoshell_container import Provider, Container, IoCContainer, INSTANCE, BootstrapProvider


class _Foo:

    def __init__(self):
        self.foo = 1


class _FooProvider(Provider[_Foo]):

    def __init__(self, val: int = 2):
        self.val = val

    def singleton(self) -> bool:
        return True

    def factory(self, con: IoCContainer) -> INSTANCE:
        foo = _Foo()
        foo.foo = self.val
        return foo


def test_register():
    c = Container()
    p = _FooProvider(2)
    c.register(p)

    foo = c.force_fetch(_Foo)
    # generic check
    assert p.contract() is _Foo
    assert foo.foo is 2
    # singleton bound
    assert c.force_fetch(_Foo) is foo


class _FooBootstrapProvider(BootstrapProvider[_FooProvider]):

    def singleton(self) -> bool:
        return True

    def factory(self, con: IoCContainer) -> INSTANCE:
        return _Foo()

    def contract(self) -> Type[INSTANCE]:
        return _Foo

    def bootstrap(self, container: IoCContainer) -> None:
        foo = container.fetch(_Foo)
        foo.foo = 3

        def shutdown(f: _Foo):
            f.foo = 0

        container.add_shutdown(shutdown)


def test_register_boostrap():
    c = Container()
    c.register(_FooBootstrapProvider())

    c.bootstrap()

    foo = c.force_fetch(_Foo)
    # bootstrap
    assert foo.foo is 3

    c.shutdown()
    # shutdown is called
    assert foo.foo is 0


def test_register_rebind():
    c = Container()
    c.register(_FooBootstrapProvider())

    with c:
        foo = c.force_fetch(_Foo)
        assert foo.foo is 3

        # rebind provider
        c.register(_FooProvider(1))

        assert foo.foo is 3
        # the binding has been changed
        assert c.force_fetch(_Foo) is not foo
        assert c.force_fetch(_Foo).foo is 1
