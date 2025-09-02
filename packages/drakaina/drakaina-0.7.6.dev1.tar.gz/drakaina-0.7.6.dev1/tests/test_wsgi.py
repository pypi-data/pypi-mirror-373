import pytest
from httpx import Client
from httpx import WSGITransport

from drakaina.serializers import JsonSerializer
from drakaina.wsgi import WSGIHandler


URL = "/jrpc"
RPC_SCHEMA = "/openrpc.json"
OAI_SCHEMA = "/openapi.json"
app = WSGIHandler(
    route=URL,
    openapi_url=OAI_SCHEMA,
    openrpc_url=RPC_SCHEMA,
)
json = JsonSerializer()


@pytest.fixture(scope="module")
def client(rpc_procedures):
    headers = {"Content-Type": "application/json"}
    with Client(
        transport=WSGITransport(app, remote_addr="testserver"),
        base_url="http://testserver",
        headers=headers,
    ) as httpx_client:
        yield httpx_client


def test_jrpc_over_wsgi(client, jrpc_spec_example):
    # Prepare example data
    request, response_expected = jrpc_spec_example
    request_data = (
        request.encode()
        if isinstance(request, str)
        else json.serialize(request)
    )
    expected_data = (
        response_expected.encode()
        if isinstance(response_expected, str)
        else json.serialize(response_expected)
    )

    # Make test "request" to wsgi application
    r = client.post(URL, content=request_data)

    assert r.status_code == 200
    assert r.content == expected_data


@pytest.mark.parametrize(
    "url, code, content_type",
    (
        (RPC_SCHEMA, 200, "application/json"),
        (OAI_SCHEMA, 200, "application/json"),
        ("/some_path.html", 404, None),
    ),
)
def test_schemas(client, url, code, content_type):
    r = client.get(url)
    print(r.content)

    assert r.status_code == code
    assert r.headers.get("Content-Type") == content_type

    schema = None
    if url in (RPC_SCHEMA, OAI_SCHEMA):
        assert r.content
        schema = json.deserialize(r.content)
        assert schema["info"]

    if url == RPC_SCHEMA:
        assert schema["openrpc"]

    if url == OAI_SCHEMA:
        assert schema["openapi"]


class TestMiddleware:
    def __init__(self, app, **kwargs):
        self.app = app
        self.kwargs = kwargs
        self.called = False

    def __call__(self, environ, start_response):
        self.called = True
        return self.app(environ, start_response)


def test_add_middleware():
    """Test adding middleware after WSGIHandler initialization."""
    handler = WSGIHandler(route="/test")
    
    # Add first middleware
    mw1 = TestMiddleware
    handler.add_middleware(mw1)
    assert isinstance(handler._middlewares_chain, TestMiddleware)
    
    # Add second middleware
    mw2 = TestMiddleware
    handler.add_middleware(mw2, custom_param=True)
    assert isinstance(handler._middlewares_chain, TestMiddleware)
    assert handler._middlewares_chain.kwargs["custom_param"] is True
    
    # Test middleware execution order
    def start_response(status, headers):
        pass
    
    environ = {"REQUEST_METHOD": "POST", "wsgi.input": None}
    handler(environ, start_response)
    
    # Both middlewares should be called
    assert handler._middlewares_chain.called  # mw2 was called
    assert handler._middlewares_chain.app.called  # mw1 was called


def test_add_middleware_with_partial():
    """Test adding middleware using functools.partial."""
    from functools import partial
    
    handler = WSGIHandler(route="/test")
    mw = partial(TestMiddleware, custom_param="from_partial")
    
    handler.add_middleware(mw)
    assert isinstance(handler._middlewares_chain, TestMiddleware)
    assert handler._middlewares_chain.kwargs["custom_param"] == "from_partial"
