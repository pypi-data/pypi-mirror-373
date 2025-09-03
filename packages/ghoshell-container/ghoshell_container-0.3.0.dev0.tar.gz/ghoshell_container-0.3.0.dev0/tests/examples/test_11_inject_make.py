from ghoshell_container import Container, Inject


class _Foo:
    def __init__(self, foo: int = 1):
        self.foo = foo


class _Bar:
    # marked the property need to be injected
    foo1: _Foo = Inject(binding=_Foo)
    foo2: _Foo = Inject(_Foo(2))


def test_inject_make():
    bar = _Bar()
    assert bar.foo1 is None
    c = Container()

    assert c.get(_Bar) is None
    # inject by Inject scan
    bar1 = c.make(_Bar)
    assert bar1.foo1.foo == 1
    assert bar1.foo2.foo == 1

    # cause foo1 has binding, foo2 also has binding
    assert bar1.foo1 is bar1.foo2
