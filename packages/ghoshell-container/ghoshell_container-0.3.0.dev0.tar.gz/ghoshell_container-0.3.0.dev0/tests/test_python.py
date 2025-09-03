def test_raise_from():
    def foo():
        raise ValueError("hello")

    def bar():
        try:
            foo()
        except Exception as e:
            raise RuntimeError("foo raised exception") from e

    e = None
    try:
        bar()
    except Exception as ex:
        e = ex

    assert e is not None


def test_callable():
    def foo():
        return None

    class Bar:
        pass

    assert callable(foo)
    # class is also callable
    assert callable(Bar)
    # but foo is not type
    assert not isinstance(foo, type)
