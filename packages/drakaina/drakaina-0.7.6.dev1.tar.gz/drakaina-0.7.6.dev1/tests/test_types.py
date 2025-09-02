from typing import MutableMapping

from pytest import raises

from drakaina.types import ProxyRequest


def test_proxy_request_is_mapping():
    r = ProxyRequest({"key": "value"})

    assert isinstance(r, MutableMapping)

    # Get item
    assert r["key"] == "value"
    assert r.get("key") == "value"

    # Get a non-existent item
    with raises(KeyError):
        _ = r["nothing"]
    assert r.get("nothing") is None
    assert r.get("nothing", "default") == "default"

    # Set item
    r["key_2"] = "value_2"
    assert r["key_2"] == "value_2"
    r.update(key_3="value_3")
    assert r["key_3"] == "value_3"
    r.update({"key_4": "value_4"})
    assert r["key_4"] == "value_4"

    # Contains
    assert "key_2" in r
    assert "key_3" in r.keys()
    assert "nothing" not in r
    assert len(r) == 4

    # Remove item
    del r["key_2"]
    assert "key_2" not in r

    # Methods
    assert tuple(r.keys()) == ("key", "key_3", "key_4")
    assert [key for key in r] == ["key", "key_3", "key_4"]
    assert [key for key in r.keys()] == ["key", "key_3", "key_4"]
    assert [value for value in r.values()] == ["value", "value_3", "value_4"]

    assert "key_4" in r
    assert r.pop("key_4") == "value_4"
    assert "key_4" not in r

    assert [item for item in r.items()] == [
        ("key", "value"),
        ("key_3", "value_3"),
    ]

    assert "key_3" in r
    assert r.popitem() == ("key_3", "value_3")
    assert "key_3" not in r
    assert len(r) == 1

    r_copy = r.copy()
    assert isinstance(r_copy, MutableMapping)
    assert isinstance(r_copy, ProxyRequest)
    assert len(r) == len(r_copy)
    assert r_copy["key"] == "value"


def test_proxy_request_is_proxy_object():
    r = ProxyRequest({"key": "value"})

    # Get attribute
    assert r.key == "value"
    r.key = "new_value"
    assert r.key == "new_value"

    # Set attribute
    r.key_2 = "value_2"
    assert r.key_2 == "value_2"
    assert r["key_2"] == "value_2"
    r.key_2 = "value_22"
    assert r.get("key_2", "default") == "value_22"

    # Delete attribute
    del r.key_2
    assert "key_2" not in r
    assert "key_2" not in r.keys()
