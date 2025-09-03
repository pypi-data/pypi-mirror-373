from ghoshell_container import Container


def test_set_and_get():
    container = Container()
    container.set('foo', 'bar')
    assert container.get('foo') == 'bar'
    assert container.bound('foo')


def test_get_none():
    container = Container()
    container.set('foo', 'bar')
    # if not set, get none
    assert container.get('zoo') is None
    assert container['foo'] is 'bar'
    del container['foo']
    assert container.get('foo') is None


def test_get_recursively():
    parent = Container()
    parent.set('foo', 'bar')

    child = Container(parent, name="self")
    assert child.name == 'self'
    assert child.parent is parent

    # child get contract from parent
    assert child.get('foo') == 'bar'
    # child get contract from self only
    assert child.get('foo', recursively=False) is None
