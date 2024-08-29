import random

import pytest

# TODO review
from src.testables.my_class import MyClass


def test_my_own_random_value(monkeypatch):
    r = random.Random()

    expected_value: float = 3.3
    monkeypatch.setattr(r, "random", lambda: expected_value)
    value = r.random()

    assert value == expected_value


def test_my_class_method_patched(monkeypatch):
    c = MyClass()

    assert c.encrypt("diego ariel") == "g"

    monkeypatch.setattr(c, "secret", lambda: 10)
    assert c.encrypt("diego ariel") == "l"


def test_my_class_attr_patched(monkeypatch):
    c = MyClass()

    assert c.encrypt("diego ariel") == "g"

    monkeypatch.setattr(c, "_the_secret", 9)
    assert c.encrypt("diego ariel") == "e"

    #doesnt work.
    #monkeypatch.setattr(MyClass, "_the_secret",
    #                    property(lambda self: 10))
    #assert c.encrypt("diego ariel") == "l"

    #simply set the value we want
    c._the_secret = 10
    assert c.encrypt("diego ariel") == "l"


def test_encrypt_raises(monkeypatch):
    c = MyClass()

    with pytest.raises(AttributeError):
        monkeypatch.setattr(c, "non_existing_attr", 10, raising=True)
