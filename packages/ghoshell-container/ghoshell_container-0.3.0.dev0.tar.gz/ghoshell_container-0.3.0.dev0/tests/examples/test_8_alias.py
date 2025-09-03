from ghoshell_container import Container


class _Foo:
    pass


class _Bar(_Foo):
    pass


def test_alias():
    c = Container()
    c.bind(_Foo, _Bar())

    assert c.bound(_Foo)
    assert not c.bound(_Bar)
    assert isinstance(c.force_fetch(_Foo), _Bar)

    # set alias
    c.alias(_Foo, _Bar)
    assert c.bound(_Bar)

    # same singleton
    assert c.force_fetch(_Foo) is c.force_fetch(_Bar)
