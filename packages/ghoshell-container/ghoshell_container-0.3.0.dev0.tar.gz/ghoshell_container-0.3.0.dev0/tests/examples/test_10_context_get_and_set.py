from ghoshell_container import get_container, set_container, Container
from contextvars import copy_context


def test_container_is_the_same():
    container = get_container()

    def foo():
        assert container is get_container()

    def bar():
        foo()
        assert container is get_container()

    # the container is always the same cause context
    bar()
    assert container is get_container()


def test_set_container_in_same_ctx():
    container = get_container()

    def foo():
        set_container(Container(name="foo"))

    # container has been changed by foo
    foo()
    assert container is not get_container()


def test_set_container_in_defer_ctx():
    set_container(Container(name="root"))
    container = get_container()
    assert container.name != "foo"

    def foo():
        assert get_container().name == "foo"

    def bar():
        assert container.name != "foo"
        # assert get_container().name != "foo"
        set_container(Container(container, name="foo"))
        assert get_container().name == "foo"
        foo()

    # bar change the container in copied context
    ctx = copy_context()
    ctx.run(bar)

    # but outside bar, the container name is the same
    assert get_container().name != "foo"
    # container has not been changed
    assert get_container() is container
