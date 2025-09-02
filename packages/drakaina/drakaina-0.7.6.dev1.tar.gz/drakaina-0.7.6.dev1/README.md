<p style="text-align: center;"><img src="https://gitlab.com/tau_lex/drakaina/-/raw/main/content/drakaina300.png" style="" /></p>
<h2 style="text-align: center;">drakaina</h2>

[![image](https://img.shields.io/pypi/v/drakaina.svg)](https://pypi.python.org/pypi/drakaina)
[![image](https://img.shields.io/pypi/l/drakaina.svg)](https://pypi.python.org/pypi/drakaina)
[![image](https://img.shields.io/pypi/pyversions/drakaina.svg)](https://pypi.python.org/pypi/drakaina)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)
[![OpenRPC](https://img.shields.io/endpoint?url=https%3A%2F%2Fgitlab.com%2Ftau_lex%2Fdrakaina%2F-%2Fraw%2Fmain%2Fcontent%2Fopenrpc-badge.json)](https://open-rpc.org)
[![libera manifesto](https://img.shields.io/badge/libera-manifesto-lightgrey.svg)](https://liberamanifesto.com)

Framework for simple RPC service implementation.


## Features

- Serializers layer.
  - `json`, `orjson`, `ujson` and `msgpack` serializers.
- Generates schemas for documentation in OpenRPC format.
- WSGI protocol implementation
  - CORS middleware
  - JWT Authorization middleware.
  - Compatible with middlewares for others wsgi-frameworks,
    like as [Werkzeug](https://palletsprojects.com/p/werkzeug/),
    [Flask](https://palletsprojects.com/p/flask/)
- `login_required` and `check_permissions` decorators.


## Installation and Dependencies

Drakaina may be installed via `pip` and requires Python 3.8 or higher :

```shell
pip install drakaina
```

## Usage Examples

A minimal Drakaina example is:

```python
from drakaina import remote_procedure
from drakaina.wsgi import WSGIHandler

@remote_procedure("hello")
def hello_method(name):
    return f"Hello, {name}!"

"""
>>> from drakaina.rpc_protocols import JsonRPCv2
>>> JsonRPCv2().handle({"jsonrpc": "2.0", "method": "hello", "params": ["🐍 Python"] "id": 1})
{"jsonrpc": "2.0", "result": "Hello, 🐍 Python!", "id": 1}
"""

# Or define WSGI application
app = WSGIHandler(route="/jrpc")

```


# Documentation


### Optional requirements

```shell
pip install drakaina[jwt, orjson, ujson]
```


## Middlewares


### CORS


### JWT

Drakaina may be installed via `pip` and requires Python 3.7 or higher :

```shell
pip install drakaina[jwt]
```

Example of using Drakaina:

```python
from functools import partial
from drakaina import check_permissions
from drakaina import ENV_IS_AUTHENTICATED
from drakaina import ENV_USER_ID
from drakaina import login_required
from drakaina import match_any
from drakaina import remote_procedure
from drakaina.contrib.jwt.middleware import JWTAuthenticationMiddleware
from drakaina.wsgi import WSGIHandler

import user_store


@login_required
@remote_procedure(provide_request=True)
def my_method(request):
    assert request[ENV_IS_AUTHENTICATED]
    return f"Hello Bro ✋! Your ID={request[ENV_USER_ID]}"


@check_permissions(["user_read", "user:admin", "username:johndoe"], match_any)
@remote_procedure
def my_method():
    return "Hello Bro! ✋️"


def get_user(request, payload):
    user_id = request[ENV_USER_ID] or payload["user_id"]
    return user_store.get(id=user_id)


def get_jwt_scopes(request, payload):
    # here `scp` is the key for the scopes value in the token payload
    return payload.get("scp")


app = WSGIHandler(
    middlewares=[
        partial(
            JWTAuthenticationMiddleware,
            secret_phrase="_secret_",
            credentials_required=True,
            auth_scheme="Bearer",
            # token_getter=custom_implementation_get_token,
            user_getter=get_user,
            scopes_getter=get_jwt_scopes,
            # revoke_checker=is_revoked,
        )
    ]
)
```

Drakaina may be ran with any WSGI-compliant server,
such as [Gunicorn](http://gunicorn.org).

```shell
gunicorn main:app
```

or ran with any ASGI-compliant server

```shell
uvicorn main:app2
```


### Using with Django

Create file `rpc_views.py` in your django application.
Define function and wrap it `remote_procedure` decorator:

```python
from drakaina import remote_procedure

@remote_procedure
def my_method():
    return "Hello, Django Bro! ✋"
```

Add `RPCView` class to urlpatterns. The `as_view` method
must accept the `autodiscover` argument as the name of
the remote procedure files.

```python
from django.urls import path
from drakaina.contrib.django.views import RPCView

urlpatterns = [
    ...,
    path("api/", RPCView.as_view(autodiscover="rpc_views")),
]
```


### JWT Authentication in your Django project

Wrap an instance of `RPCView` with the `JWTAuthenticationMiddleware`.

```python
from django.urls import path
from drakaina.contrib.django import RPCView, JWTAuthenticationMiddleware

urlpatterns = [
    ...,
    path("api/", JWTAuthenticationMiddleware(
        RPCView.as_view(autodiscover="rpc_views")
    )),
]
```

Define the parameters in the `settings.py` file.

```python
...

DRAKAINA_JWT_SECRET_KEY = "__SECRET_KEY__"

...
```


## License

Apache License 2.0

## Artwork

"[drakaina.png](content/drakaina.png)" by Korolko Anastasia is licensed under
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="License Creative Commons" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/80x15.png" /></a> ([CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/)).
