# it illustrates a session scoped fixture, it retains the value all along the functions in the session

import pytest

x: int = 0


@pytest.fixture(scope="session")
def my_fixture():
    global x
    x += 1
    return f"fixture {x}"


def test_ok(my_fixture):
    assert my_fixture == "fixture 1"


def test_ok2(my_fixture):
    assert my_fixture == "fixture 1"
