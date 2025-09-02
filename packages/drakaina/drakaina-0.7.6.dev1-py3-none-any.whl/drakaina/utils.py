from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime
from datetime import timedelta
from functools import partial
from typing import Callable
from typing import Literal


def iterable_str_arg(s: str | Iterable[str]) -> tuple[str, ...]:
    if isinstance(s, str):
        s = s.replace(",", " ").strip()
        s = s.replace("  ", " ").split()
    return tuple(map(str, s))


def unwrap_func(func: Callable) -> Callable:
    _func = func
    while hasattr(_func, "__wrapped__") or isinstance(_func, partial):
        _func = getattr(_func, "__wrapped__", None) or _func.func
    return _func


def short_description_by_name(s: str) -> str:
    if isinstance(s, str):
        return re.sub(r"[\.-_]", " ", s).capitalize()


def get_cookies(cookie_str: str) -> dict[str, str]:
    if cookie_str is None:
        return {}

    _cookies = {}
    for cookie_item in cookie_str.split(";"):
        if "=" not in cookie_item or "DELETED" in cookie_item:
            continue
        name, value = cookie_item.strip().split("=", 1)
        _cookies[name] = value

    return _cookies


def set_cookie(
    name: str,
    value: str,
    expires: datetime | int | str | None = None,
    max_age: timedelta | int | None = None,
    domain: str | None = None,
    path: str | None = None,
    secure: bool | None = None,
    http_only: bool | None = None,
    same_site: Literal["Strict", "Lax", "None"] | None = None,
    flags: Iterable[str] | None = None,
) -> tuple[str, str]:
    """Returns tuple with cookie values prepared for ASGI/WSGI interface.

    RFC6265: https://datatracker.ietf.org/doc/html/rfc6265

    """
    if "__Secure" in name:
        secure = True
    if "__Host" in name:
        secure = True
        domain = None
        path = "/"
    value = value.replace(";", "")
    if expires:
        if isinstance(expires, int):
            expires = datetime.fromtimestamp(expires)
        if isinstance(expires, datetime):
            expires = expires.strftime("%a, %d %b %Y %H:%M:%S %Z")
        assert isinstance(expires, str)
        value += f"; Expires={expires}"
    if max_age:
        if isinstance(max_age, timedelta):
            max_age = max_age.days * 24 * 3600 + max_age.seconds
        assert isinstance(max_age, int) and max_age > 0
        value += f"; Max-Age={max_age}"
    if isinstance(domain, str):
        value += f"; Domain={domain}"
    if isinstance(path, str):
        value += f"; Path={path}"
    if secure:
        value += "; Secure"
    if http_only:
        value += "; HttpOnly"
    if same_site:
        assert same_site in ("Strict", "Lax", "None")
        if same_site == "None":
            assert secure is True
        value += f"; SameSite={same_site}"
    if flags:
        value += "; " + "; ".join(flags)

    return "Set-Cookie", f"{name}={value}".strip()


def mark_cookie_as_deleted(name: str) -> tuple[str, str]:
    expiry_string = "Thu, 01 Jan 1970 00:00:00 GMT"
    value = "DELETED"
    return "Set-Cookie", f"{name}={value}; Expires={expiry_string}"


def match_path(item_path: str | re.Pattern[str], path_info: str) -> bool:
    """Check if the `path_info` (CGI) is equal to the given `item_path`
    of the element being checked.

    :param item_path: URL or regex pattern to match against the request path.
    :param path_info: Request path string.
    """

    if item_path is None:
        return True
    if isinstance(item_path, str):
        return path_info == item_path
    if isinstance(item_path, re.Pattern):
        return bool(item_path.match(path_info))

    return False
