from ghoshell_container import get_container, set_container, depends, Container
from contextvars import copy_context


class Foo:
    def __init__(self, a: int = 1):
        self.a = a


@depends
def foo(f: Foo) -> int:
    return f.a


def test_foo():
    # inject
    assert foo() == 1
    # not inject
    assert foo(Foo(2)) == 2


def test_foo_in_container():
    c = get_container()
    c.set(Foo, Foo(2))

    assert foo() == 2


def test_foo_in_sub_container():
    # outside
    get_container().set(Foo, Foo(2))

    def bar():
        # inside
        new_c = Container()
        new_c.set(Foo, Foo(3))
        set_container(new_c)
        assert foo() == 3

    ctx = copy_context()
    ctx.run(bar)

    assert foo() == 2
