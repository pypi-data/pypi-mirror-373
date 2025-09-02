import pytest

from drakaina import remote_procedure
from drakaina.exceptions import AuthenticationFailedError
from drakaina.exceptions import BadRequestError
from drakaina.exceptions import DeserializationError
from drakaina.exceptions import ForbiddenError
from drakaina.exceptions import InternalServerError
from drakaina.exceptions import InvalidParametersError
from drakaina.exceptions import InvalidPermissionsError
from drakaina.exceptions import InvalidTokenError
from drakaina.exceptions import NotFoundError
from drakaina.exceptions import RPCError
from drakaina.exceptions import SerializationError
from drakaina.registries import RPCRegistry
from drakaina.rpc_protocols import JsonRPCv2
from drakaina.rpc_protocols.jsonrpc20 import AuthenticationFailedJRPCError
from drakaina.rpc_protocols.jsonrpc20 import ForbiddenJRPCError
from drakaina.rpc_protocols.jsonrpc20 import InternalError
from drakaina.rpc_protocols.jsonrpc20 import InvalidParamsError
from drakaina.rpc_protocols.jsonrpc20 import InvalidPermissionsJRPCError
from drakaina.rpc_protocols.jsonrpc20 import InvalidRequestError
from drakaina.rpc_protocols.jsonrpc20 import InvalidTokenJRPCError
from drakaina.rpc_protocols.jsonrpc20 import JsonRPCError
from drakaina.rpc_protocols.jsonrpc20 import MethodNotFoundError
from drakaina.rpc_protocols.jsonrpc20 import ParseError
from drakaina.serializers import JsonSerializer


custom_registry = RPCRegistry()
json = JsonSerializer()
protocol = JsonRPCv2(registry=custom_registry)


@remote_procedure(name="sum", registry=custom_registry)
def rpc_sum(*args):
    return sum(args)


@remote_procedure(registry=custom_registry)
def subtract(minuend, subtrahend):
    return minuend - subtrahend


@remote_procedure(registry=custom_registry)
def update(*args):
    print(f"Notification `update` called. Your params={args}")


@remote_procedure(registry=custom_registry)
def notify_hello(*args):
    print(f"Hello! Your params={args}")


@remote_procedure(name="get_data", registry=custom_registry)
def get_data():
    print("You called `get_data'.")
    return ["hello", 5]


def test_jrpc_protocol_handle_method(jrpc_spec_example):
    # Prepare example data
    request, response_expected = jrpc_spec_example

    # Skip examples with invalid json string
    if isinstance(request, str):
        return

    # None is empty string in the `handle_raw_request` method
    if response_expected == "":
        response_expected = None

    # Make test "request" to protocol application
    response = protocol.handle(request)

    assert response == response_expected


def test_jrpc_protocol_raw_requests(jrpc_spec_example):
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

    # Make test "request" to protocol application
    response = protocol.handle_raw_request(request_data)

    assert response == expected_data


@pytest.mark.parametrize(
    ("error_class", "expected_error_class"),
    (
        (JsonRPCError, JsonRPCError),
        (ParseError, ParseError),
    ),
)
def test_protocol_errors_handling(error_class, expected_error_class):
    error_obj = protocol.get_raw_error(error_class)
    expected_error = protocol.get_raw_error(expected_error_class)

    assert error_obj == expected_error

    error_obj = protocol.get_raw_error(error_class())
    expected_error = protocol.get_raw_error(expected_error_class)

    assert error_obj == expected_error


@pytest.mark.parametrize(
    ("error_class", "expected_error_class"),
    (
        (Exception, JsonRPCError),
        (RPCError, JsonRPCError),
        (BadRequestError, InvalidRequestError),
        (NotFoundError, MethodNotFoundError),
        (InvalidParametersError, InvalidParamsError),
        (InternalServerError, InternalError),
        (SerializationError, InternalError),
        (DeserializationError, ParseError),
        (AuthenticationFailedError, AuthenticationFailedJRPCError),
        (InvalidTokenError, InvalidTokenJRPCError),
        (ForbiddenError, ForbiddenJRPCError),
        (InvalidPermissionsError, InvalidPermissionsJRPCError),
    ),
)
def test_errors_translation(error_class, expected_error_class):
    error_obj = protocol.get_raw_error(error_class)
    expected_error = protocol.get_raw_error(expected_error_class)

    assert error_obj == expected_error

    error_obj = protocol.get_raw_error(error_class())
    expected_error = protocol.get_raw_error(expected_error_class)

    assert error_obj == expected_error
