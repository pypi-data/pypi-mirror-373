from drakaina.exceptions import DeserializationError
from drakaina.exceptions import RPCError
from drakaina.exceptions import SerializationError
from drakaina.rpc_protocols.jsonrpc20 import InternalError
from drakaina.rpc_protocols.jsonrpc20 import InvalidParamsError
from drakaina.rpc_protocols.jsonrpc20 import InvalidRequestError
from drakaina.rpc_protocols.jsonrpc20 import JsonRPCError
from drakaina.rpc_protocols.jsonrpc20 import MethodNotFoundError
from drakaina.rpc_protocols.jsonrpc20 import ParseError


def test_module_exceptions_as_dict_method():
    assert RPCError().as_dict() == {
        "error": "RPCError",
        "message": "",
    }
    assert SerializationError("message").as_dict() == {
        "error": "SerializationError",
        "message": "message",
    }
    assert DeserializationError("message").as_dict() == {
        "error": "DeserializationError",
        "message": "message",
    }


def test_jrpc_protocol_exceptions_as_dict_method():
    assert JsonRPCError().as_dict() == {
        "jsonrpc": "2.0",
        "error": {"code": -32000, "message": "Server error"},
        "id": None,
    }
    assert InvalidRequestError("message").as_dict() == {
        "jsonrpc": "2.0",
        "error": {
            "code": -32600,
            "message": "Invalid Request",
            "data": "message",
        },
        "id": None,
    }
    assert MethodNotFoundError("message", id=12345).as_dict() == {
        "jsonrpc": "2.0",
        "error": {
            "code": -32601,
            "message": "Method not found",
            "data": "message",
        },
        "id": 12345,
    }
    assert InvalidParamsError(message="message", id=12345).as_dict() == {
        "jsonrpc": "2.0",
        "error": {
            "code": -32602,
            "message": "Invalid params",
            "data": "message",
        },
        "id": 12345,
    }
    assert InternalError(
        id=12345,
        data={"some_detail_key": "detail data"},
    ).as_dict() == {
        "jsonrpc": "2.0",
        "error": {
            "code": -32603,
            "message": "Internal error",
            "data": {"some_detail_key": "detail data"},
        },
        "id": 12345,
    }
    assert ParseError(
        "message",
        data={"some_detail_key": "detail data"},
    ).as_dict() == {
        "jsonrpc": "2.0",
        "error": {
            "code": -32700,
            "message": "Parse error",
            "data": {
                "text": "message",
                "details": {"some_detail_key": "detail data"},
            },
        },
        "id": None,
    }


# todo: implement tests for base auth errors
# todo: implement tests for jrpc auth errors
