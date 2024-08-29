# it illustrates a function scoped fixture, it recalculates the value among functions

import pytest

x: int = 0


@pytest.fixture(scope="function")
def my_fixture():
    global x
    x += 1
    return f"fixture {x}"


def test_ok(my_fixture):
    assert my_fixture == "fixture 1"


def test_ok2(my_fixture):
    assert my_fixture == "fixture 2"
