from ghoshell_container import DeclaredContainer, Inject, provide


class Foo:
    pass


class Bar:
    def __init__(self, a=1):
        self.a = a


class Baz:
    pass


def test_declared_container():
    # declare injections
    class MyContainer(DeclaredContainer):
        foo: Foo
        bar: Bar = Inject(binding=lambda: Bar(2))
        baz: Baz = Inject(binding=provide(Baz)(lambda: Baz()))

    c = MyContainer()
    c.bootstrap()
    assert isinstance(c.foo, Foo)
    assert isinstance(c.bar, Bar)
    assert isinstance(c.baz, Baz)
    assert c.bar.a == 2
