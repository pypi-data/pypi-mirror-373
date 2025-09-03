from ghoshell_container import Container


class _Foo:

    def __init__(self):
        self.foo = 1


def test_call_with_foo():
    def fn(_foo: _Foo) -> int:
        return _foo.foo

    c = Container()
    assert c.call(fn) is 1

    foo = _Foo()
    foo.foo = 2

    c.set(_Foo, foo)
    # foo is changed
    assert c.call(fn) is 2


def test_call_with_kwargs():
    def fn(_foo: _Foo, a: int) -> int:
        return _foo.foo + a

    c = Container()
    foo = _Foo()
    foo.foo = 2
    c.set(_Foo, foo)
    assert c.call(fn, a=1) is 3
