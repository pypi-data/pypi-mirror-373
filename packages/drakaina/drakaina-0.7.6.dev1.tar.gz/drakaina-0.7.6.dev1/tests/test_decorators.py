from inspect import iscoroutinefunction

import pytest

from drakaina import rpc_registry
from drakaina.constants import ENV_AUTH_SCOPES
from drakaina.constants import ENV_IS_AUTHENTICATED
from drakaina.decorators import _get_request
from drakaina.decorators import _get_scopes
from drakaina.decorators import _is_authenticated
from drakaina.decorators import check_permissions
from drakaina.decorators import login_required
from drakaina.decorators import match_all
from drakaina.decorators import match_any
from drakaina.decorators import remote_procedure
from drakaina.exceptions import ForbiddenError
from drakaina.registries import is_rpc_procedure
from drakaina.registries import RPC_META
from drakaina.registries import RPC_NAME
from drakaina.registries import RPC_PROVIDE_REQUEST
from drakaina.registries import RPC_REGISTERED
from drakaina.registries import RPC_REGISTRY
from drakaina.registries import RPC_SCHEMA
from drakaina.registries import RPCRegistry
from drakaina.types import ProxyRequest


def test_simple_decorator():
    # We use a predefined procedure with an unparameterized decorator
    from tests.rpc_methods import subtract

    assert is_rpc_procedure(subtract)
    assert getattr(subtract, RPC_REGISTRY) is rpc_registry
    assert getattr(subtract, RPC_REGISTERED) is True
    assert getattr(subtract, RPC_NAME) == "subtract"
    assert getattr(subtract, RPC_PROVIDE_REQUEST) is None
    assert isinstance(getattr(subtract, RPC_SCHEMA), dict)
    assert getattr(subtract, RPC_META) == {}
    assert callable(getattr(subtract, "__wrapped__"))


def test_parametrized_decorator():
    registry = RPCRegistry()

    @remote_procedure(
        name="func",
        registry=registry,
        provide_request=True,
        metadata={"meta_option": 123},
        meta_arg=321,
    )
    def proc(request):
        return "ok"

    assert is_rpc_procedure(proc)
    assert getattr(proc, RPC_REGISTRY) is registry
    assert getattr(proc, RPC_REGISTERED) is True
    assert getattr(proc, RPC_NAME) == "func"
    assert getattr(proc, RPC_PROVIDE_REQUEST) is True
    assert isinstance(getattr(proc, RPC_SCHEMA), dict)
    assert getattr(proc, RPC_META) == {
        "meta_option": 123,
        "meta_arg": 321,
    }
    assert callable(getattr(proc, "__wrapped__"))

    @remote_procedure(
        name="async_func",
        registry=registry,
        provide_request=True,
        metadata={"meta_option": 123},
        meta_arg=321,
    )
    async def async_proc(request):
        return "ok"

    assert iscoroutinefunction(async_proc)
    assert iscoroutinefunction(getattr(async_proc, "__wrapped__"))
    assert is_rpc_procedure(async_proc)
    assert getattr(async_proc, RPC_REGISTRY) is registry
    assert getattr(async_proc, RPC_REGISTERED) is True
    assert getattr(async_proc, RPC_NAME) == "async_func"
    assert getattr(async_proc, RPC_PROVIDE_REQUEST) is True
    assert isinstance(getattr(async_proc, RPC_SCHEMA), dict)
    assert getattr(async_proc, RPC_META) == {
        "meta_option": 123,
        "meta_arg": 321,
    }
    assert callable(getattr(async_proc, "__wrapped__"))


@pytest.mark.parametrize(
    "required, provided, result_any, result_all",
    (
        ([], [], True, True),
        ("A", "C", False, False),
        (["A", "B"], "C", False, False),
        (["A", "B"], ["C"], False, False),
        (("A", "B"), "B", True, False),
        (("A", "B"), ("B",), True, False),
        ("A", "A", True, True),
        (("A", "B"), ("A", "B"), True, True),
        (("A", "B"), ("A", "B", "C"), True, True),
    ),
)
def test_match_functions(required, provided, result_any, result_all):
    assert match_any(required, provided) is result_any
    assert match_all(required, provided) is result_all


def test_get_request():
    request = ProxyRequest({})

    assert _get_request(request, "A", "B") is request
    assert _get_request(request, "A", "B", c="C") is request
    assert _get_request(request=request, a="A", b="B", c="C") is request


def test_is_authenticated():
    # For environments
    assert _is_authenticated({ENV_IS_AUTHENTICATED: True})
    assert not _is_authenticated({ENV_IS_AUTHENTICATED: False})
    assert not _is_authenticated({})

    # For objects
    assert _is_authenticated(type("Request", (), {ENV_IS_AUTHENTICATED: True}))
    assert not _is_authenticated(
        type("Request", (), {ENV_IS_AUTHENTICATED: False}),
    )
    assert not _is_authenticated(type("Request", (), {}))


def test_get_scopes():
    # For environments
    assert _get_scopes({ENV_AUTH_SCOPES: " A "}) == ("A",)
    assert _get_scopes({ENV_AUTH_SCOPES: "A,B"}) == ("A", "B")
    assert _get_scopes({ENV_AUTH_SCOPES: ["A", "B"]}) == ("A", "B")
    assert _get_scopes({ENV_AUTH_SCOPES: None}) == ()
    assert _get_scopes({}) == ()

    # For objects
    assert _get_scopes(type("Request", (), {ENV_AUTH_SCOPES: " A "})) == ("A",)
    assert _get_scopes(type("Request", (), {ENV_AUTH_SCOPES: "A,B"})) == (
        "A",
        "B",
    )
    assert _get_scopes(type("Request", (), {ENV_AUTH_SCOPES: ["A", "B"]})) == (
        "A",
        "B",
    )
    assert _get_scopes(type("Request", (), {ENV_AUTH_SCOPES: None})) == ()
    assert _get_scopes(type("Request", (), {})) == ()


def test_login_required():
    registry = RPCRegistry()

    def proc_invalid():
        return "ok"

    with pytest.raises(TypeError):
        _ = login_required("error")
    with pytest.raises(TypeError):
        _ = login_required()("error")
    with pytest.raises(TypeError):
        _ = login_required(proc_invalid)
    with pytest.raises(TypeError):
        _ = login_required("error")(proc_invalid)

    @login_required
    @remote_procedure(registry=registry)
    def proc():
        return "ok"

    @login_required()
    @remote_procedure(registry=registry)
    async def async_proc():
        return "ok"

    assert proc(ProxyRequest({ENV_IS_AUTHENTICATED: True})) == "ok"
    # assert async_proc(ProxyRequest({ENV_IS_AUTHENTICATED: True}))
    with pytest.raises(ForbiddenError):
        proc(ProxyRequest({ENV_IS_AUTHENTICATED: False}))
    with pytest.raises(ForbiddenError):
        proc(ProxyRequest({}))


def test_check_permissions():
    registry = RPCRegistry()

    @remote_procedure(registry=registry)
    def proc_valid():
        return "ok"

    def proc_invalid():
        return "ok"

    with pytest.raises(TypeError):
        _ = check_permissions(proc_valid)
    with pytest.raises(TypeError):
        _ = check_permissions()(proc_valid)
    with pytest.raises(TypeError):
        _ = check_permissions(("A", 1234))(proc_valid)
    with pytest.raises(TypeError):
        _ = check_permissions(("A", "B"), None)(proc_valid)
    with pytest.raises(TypeError):
        _ = check_permissions(("A", "B"), match_all)(proc_invalid)

    @check_permissions("A")
    @remote_procedure(registry=registry)
    def proc():
        return "ok"

    @check_permissions("A, B")
    @remote_procedure(registry=registry)
    async def async_proc():
        return "ok"

    assert (
        proc(
            ProxyRequest({ENV_IS_AUTHENTICATED: True, ENV_AUTH_SCOPES: ("A",)}),
        )
        == "ok"
    )
    # assert async_proc(ProxyRequest({ENV_IS_AUTHENTICATED: True}))
    with pytest.raises(ForbiddenError):
        proc(
            ProxyRequest(
                {ENV_IS_AUTHENTICATED: False, ENV_AUTH_SCOPES: ("A",)},
            ),
        )
    with pytest.raises(ForbiddenError):
        proc(
            ProxyRequest({ENV_IS_AUTHENTICATED: True, ENV_AUTH_SCOPES: ("C",)}),
        )
    with pytest.raises(ForbiddenError):
        proc(ProxyRequest({}))
