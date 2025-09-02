import re
from datetime import datetime
from datetime import timedelta
from functools import partial
from functools import wraps

import pytest

from drakaina.utils import get_cookies
from drakaina.utils import iterable_str_arg
from drakaina.utils import match_path
from drakaina.utils import set_cookie
from drakaina.utils import unwrap_func


@pytest.mark.parametrize(
    ("source", "expected"),
    (
        ("a,b,c", ("a", "b", "c")),
        (" a, b, c  ", ("a", "b", "c")),
        ("a b   c", ("a", "b", "c")),
        (["a", "b", "c"], ("a", "b", "c")),
        (("a", "b", "c"), ("a", "b", "c")),
        ((1, 2, 3), ("1", "2", "3")),
    ),
    ids=(
        "str to tuple 1",
        "str to tuple 2",
        "str to tuple 3",
        "list to tuple",
        "tuple to tuple",
        "tuple[int] to tuple[str]",
    ),
)
def test_iterable_str_arg(source, expected):
    assert iterable_str_arg(source) == expected


# Define functions for test `unwrap_func`


def func(*args, **kwargs):
    ...


@wraps(func)
def wrapped_func(*args, **kwargs):
    func(*args, **kwargs)


partial_func = partial(func, "arg0")
partial_wrapped_func = partial(wrapped_func, "arg0")


@wraps(partial_func)
def wrapped_partial_func():
    partial_func()


@pytest.mark.parametrize(
    "wrapped, origin",
    (
        (func, func),
        (wrapped_func, func),
        (partial_func, func),
        (partial_wrapped_func, func),
        (wrapped_partial_func, func),
    ),
)
def test_unwrap_func(wrapped, origin):
    assert unwrap_func(wrapped) == origin


@pytest.mark.parametrize(
    "cookie, result",
    (
        ("some_key=123", {"some_key": "123"}),
        ("some_key=123;", {"some_key": "123"}),
        (
            "some_key=123;some_key_2=123",
            {"some_key": "123", "some_key_2": "123"},
        ),
    ),
)
def test_get_cookies(cookie, result):
    assert get_cookies(cookie) == result


@pytest.mark.parametrize(
    "name, value, kwargs, cookie_value, error",
    (
        ("k", "v", {}, "k=v", None),
        ("k", "v;v", {}, "k=vv", None),
        ("k", "v; v", {}, "k=v v", None),
        ("__Secure-k", "v", {}, "__Secure-k=v; Secure", None),
        ("__Host-k", "v", {}, "__Host-k=v; Path=/; Secure", None),
        (
            "__Host-k",
            "v",
            {"domain": "site.com"},
            "__Host-k=v; Path=/; Secure",
            None,
        ),
        (
            "k",
            "v",
            {"expires": datetime(2001, 1, 1)},
            "k=v; Expires=Mon, 01 Jan 2001 00:00:00",
            None,
        ),
        (
            "k",
            "v",
            {"expires": 978296400},
            "k=v; Expires=Mon, 01 Jan 2001 00:00:00",
            None,
        ),
        (
            "k",
            "v",
            {"expires": "Mon, 01 Jan 2001 00:00:00"},
            "k=v; Expires=Mon, 01 Jan 2001 00:00:00",
            None,
        ),
        ("k", "v", {"expires": 978296400.0}, None, AssertionError),
        (
            "k",
            "v",
            {"max_age": timedelta(1)},
            f"k=v; Max-Age={24 * 60 * 60}",
            None,
        ),
        (
            "k",
            "v",
            {"max_age": 24 * 60 * 60},
            f"k=v; Max-Age={24 * 60 * 60}",
            None,
        ),
        ("k", "v", {"domain": "site.com"}, "k=v; Domain=site.com", None),
        ("k", "v", {"path": "/url"}, "k=v; Path=/url", None),
        ("k", "v", {"secure": True}, "k=v; Secure", None),
        ("k", "v", {"http_only": True}, "k=v; HttpOnly", None),
        ("k", "v", {"same_site": "Strict"}, "k=v; SameSite=Strict", None),
        ("k", "v", {"same_site": "Lax"}, "k=v; SameSite=Lax", None),
        ("k", "v", {"same_site": "None"}, None, AssertionError),
        (
            "k",
            "v",
            {"same_site": "None", "secure": True},
            "k=v; Secure; SameSite=None",
            None,
        ),
        ("k", "v", {"flags": ("f1", "f2")}, "k=v; f1; f2", None),
    ),
)
def test_set_cookies(name, value, kwargs, cookie_value, error):
    if error:
        with pytest.raises(error):
            assert set_cookie(name, value, **kwargs) == (
                "Set-Cookie",
                cookie_value,
            )
    else:
        assert set_cookie(name, value, **kwargs) == ("Set-Cookie", cookie_value)


@pytest.mark.parametrize(
    "item_path, path_info, matched",
    (
        (None, "/", True),  # todo: need refactor it?
        ("/url", "/url", True),
        ("/url", "/url_", False),
        ("/url/", "/url", False),
        (re.compile("/url"), "/url", True),
        (re.compile("^/url(/subdir?)?"), "/url", True),
    ),
)
def test_match_path(item_path, path_info, matched):
    assert match_path(item_path, path_info) == matched
