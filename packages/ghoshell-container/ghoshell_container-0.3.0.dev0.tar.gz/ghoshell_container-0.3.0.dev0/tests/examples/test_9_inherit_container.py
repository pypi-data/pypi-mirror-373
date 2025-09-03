from ghoshell_container import Container, Provider, IoCContainer, INSTANCE


class _Foo:
    def __init__(self):
        self.foo = 1


class _FooSingletonButInheritanceProvider(Provider[_Foo]):

    def singleton(self) -> bool:
        return True

    def inheritable(self) -> bool:
        return True

    def factory(self, con: IoCContainer) -> INSTANCE:
        return _Foo()


def test_container_without_bind():
    parent = Container(name="parent")
    assert parent.parent is None

    child = Container(parent, name="child")
    assert child.parent is parent

    parent.set(_Foo, _Foo())
    assert parent.bound(_Foo)
    assert child.bound(_Foo)

    assert child.force_fetch(_Foo) is parent.force_fetch(_Foo)
    assert not child.bound(_Foo, recursively=False)


def test_inherit_bind():
    parent = Container(name="parent")
    # if singleton is false, rebound at child
    parent.bind(_Foo, singleton=False)

    child = Container(parent, name="child")
    # child inherit the provider
    assert child.bound(_Foo, recursively=False)


def test_inheritable_provider():
    parent = Container(name="parent")
    parent.register(_FooSingletonButInheritanceProvider())
    child = Container(parent, name="child")

    # child also bind
    assert child.bound(_Foo, recursively=False)
    # child instance is not the same as parent
    assert child.force_fetch(_Foo) is not parent.force_fetch(_Foo)


def test_child_shutdown_when_parent_shutdown():
    parent = Container(name="parent")
    child = Container(parent, name="child")
    child.bind(_Foo, singleton=True)

    def shutdown(_foo: _Foo) -> None:
        _foo.foo = 0

    child.add_shutdown(shutdown)
    foo = child.force_fetch(_Foo)
    assert foo.foo == 1

    # and child shutdown
    parent.shutdown()
    assert foo.foo == 0
