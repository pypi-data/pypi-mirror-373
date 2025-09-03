from ghoshell_container.utils import get_caller_info


def foo() -> str:
    return get_caller_info(2)


def test_get_caller_info():
    # assert exactly the line number where call it
    assert "test_utils.py:10" in foo()
