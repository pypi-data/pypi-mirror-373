from __future__ import annotations

import re
from collections.abc import Iterable
from functools import partial
from logging import Logger
from sys import version_info

from drakaina import ENV_APP
from drakaina.exceptions import BadRequestError
from drakaina.middleware.base import BaseMiddleware
from drakaina.middleware.exception import ExceptionMiddleware
from drakaina.middleware.request_wrapper import RequestWrapperMiddleware
from drakaina.rpc_protocols import BaseRPCProtocol
from drakaina.rpc_protocols import JsonRPCv2
from drakaina.types import WSGIApplication
from drakaina.types import WSGIEnvironment
from drakaina.types import WSGIInputStream
from drakaina.types import WSGIResponse
from drakaina.types import WSGIStartResponse
from drakaina.utils import match_path

if version_info < (3, 10):
    from typing import Union
    from typing_extensions import TypeAlias

    Middlewares: TypeAlias = Iterable[
        Union[type[BaseMiddleware], partial[BaseMiddleware]],
    ]
else:
    from typing import TypeAlias

    Middlewares: TypeAlias = Iterable[
        type[BaseMiddleware] | partial[BaseMiddleware],
    ]

__all__ = ("WSGIHandler",)

ALLOWED_METHODS = ("OPTIONS", "GET", "POST")


class WSGIHandler:
    """Implementation of WSGI protocol.

    :param route:
    :param handler: RPC protocol implementation.
    :param middlewares: List of WSGI middlewares.
    :param logger: A `logging.Logger` object.
    :param max_content_size: Limiting request body size for DoS protection.
    :param openrpc_url: OpenRPC Schema URL.
        The recommended document name is `openrpc.json`.
    :param openapi_url: OpenAPI Schema URL.
        The recommended document name is `openapi.json`.

    """

    __slots__ = (
        "environ",
        "start_response",
        "handler",
        "route",
        "logger",
        "max_content_size",
        "openrpc_url",
        "openapi_url",
        "_rpc_content_type",
        "_allowed_methods",
        "_middlewares_chain",
    )

    environ: WSGIEnvironment
    start_response: WSGIStartResponse
    _middlewares_chain: WSGIApplication | BaseMiddleware

    def __init__(
        self,
        route: str | re.Pattern | None = None,
        handler: BaseRPCProtocol | None = None,
        middlewares: Middlewares | None = None,
        logger: Logger | None = None,
        max_content_size: int = 4096,
        openrpc_url: str | re.Pattern | None = None,
        openapi_url: str | re.Pattern | None = None,
    ):
        self.handler = handler if handler is not None else JsonRPCv2()
        self._rpc_content_type = self.handler.content_type

        self.route = route
        if isinstance(self.route, str) and not self.route.startswith("/"):
            self.route = "/" + self.route
        schema_url = getattr(self.handler, "schema_url", None)
        if (
            self.route is not None
            and hasattr(self.handler, "schema_url")
            and schema_url is None
        ):
            setattr(self.handler, "schema_url", self.route)

        self.logger = logger
        self.max_content_size = int(max_content_size)
        self.openrpc_url = openrpc_url
        self.openapi_url = openapi_url

        if openrpc_url or openapi_url:
            self._allowed_methods = ", ".join(ALLOWED_METHODS)
        else:
            self._allowed_methods = ", ".join(
                m for m in ALLOWED_METHODS if m != "GET"
            )

        # Build middleware stack
        self._middlewares_chain = self._wsgi_app
        kw = {"is_async": False}
        for mw in reversed(middlewares or ()):
            if (
                isinstance(mw, partial) and issubclass(mw.func, BaseMiddleware)
            ) or issubclass(mw, BaseMiddleware):
                self._middlewares_chain = mw(self._middlewares_chain, **kw)
            else:
                self._middlewares_chain = mw(self._middlewares_chain)

        # The middleware for handling exceptions in the middleware according
        #  to the RPC protocol.
        self._middlewares_chain = ExceptionMiddleware(
            RequestWrapperMiddleware(self._middlewares_chain, **kw),  # noqa
            handler=self.handler,
            logger=self.logger,
            **kw,
        )

    def __call__(
        self,
        environ: WSGIEnvironment,
        start_response: WSGIStartResponse,
    ) -> WSGIResponse:
        environ[ENV_APP] = self
        return self._middlewares_chain(environ, start_response)  # noqa

    def _wsgi_app(
        self,
        environ: WSGIEnvironment,
        start_response: WSGIStartResponse,
    ) -> WSGIResponse:
        self.environ = environ
        self.start_response = start_response

        method = environ["REQUEST_METHOD"]
        if method in self._allowed_methods:
            return getattr(self, method.lower())()

        return self._method_not_allowed()

    def get(self) -> WSGIResponse:
        if match_path(self.openrpc_url, self.environ["PATH_INFO"]):
            response_body = self.handler.get_raw_openrpc_schema()
            response_headers = [
                ("Content-Type", self.handler.schema_content_type),
                ("Content-Length", str(len(response_body))),
            ]
        elif match_path(self.openapi_url, self.environ["PATH_INFO"]):
            response_body = self.handler.get_raw_openapi_schema()
            response_headers = [
                ("Content-Type", self.handler.schema_content_type),
                ("Content-Length", str(len(response_body))),
            ]
        else:
            return self._not_found()

        self.start_response("200 OK", response_headers)
        return (response_body,)

    def post(self) -> WSGIResponse:
        if not match_path(self.route, self.environ["PATH_INFO"]):
            return self._not_found()

        wsgi_input: WSGIInputStream = self.environ["wsgi.input"]

        content_type = self.environ.get("CONTENT_TYPE")
        content_length = int(self.environ.get("CONTENT_LENGTH") or 0)
        if (
            not content_type
            or not content_type.startswith(self._rpc_content_type)
            or content_length > self.max_content_size
        ):
            if not content_type.startswith(self._rpc_content_type):
                response_status = "415 Unsupported Media Type"
            else:
                response_status = "400 Bad Request"
            # Return RPC error
            response_body = self.handler.get_raw_error(BadRequestError())
        else:
            response_status = "200 OK"
            response_body = self.handler.handle_raw_request(
                wsgi_input.read(content_length),
                request=self.environ,
            )

        response_headers = [
            ("Content-Type", self._rpc_content_type),
            ("Content-Length", str(len(response_body))),
        ]
        env_response_headers = self.environ.get("response", {}).get("headers")
        if isinstance(env_response_headers, list):
            response_headers.extend(env_response_headers)

        self.start_response(response_status, response_headers)

        return (response_body,)

    def options(self) -> WSGIResponse:
        response_headers = [
            ("Allow", self._allowed_methods),
            ("Content-Length", "0"),
        ]
        self.start_response("200 OK", response_headers)
        yield b""

    def _not_found(self) -> WSGIResponse:
        response_headers = []
        self.start_response("404 Not Found", response_headers)
        yield b""

    def _method_not_allowed(self) -> WSGIResponse:
        response_headers = [("Allow", self._allowed_methods)]
        self.start_response("405 Method Not Allowed", response_headers)
        yield b""

    def add_middleware(
        self,
        middleware: type[BaseMiddleware] | partial[BaseMiddleware],
        **kwargs,
    ) -> None:
        """Add middleware to the end of middleware stack.

        :param middleware: Middleware class or partial to add
        :param kwargs: Additional keyword arguments to pass to middleware
        """
        kw = {"is_async": False, **kwargs}
        
        if (isinstance(middleware, partial) and issubclass(middleware.func, BaseMiddleware)) or issubclass(middleware, BaseMiddleware):
            self._middlewares_chain = middleware(self._middlewares_chain, **kw)
        else:
            self._middlewares_chain = middleware(self._middlewares_chain)
