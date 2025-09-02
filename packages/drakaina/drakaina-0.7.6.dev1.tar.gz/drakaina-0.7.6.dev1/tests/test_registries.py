import pytest

from drakaina import remote_procedure
from drakaina import rpc_registry


@remote_procedure()
def proc_1():
    return 1


@remote_procedure(name="proc_2")
def proc():
    return 2


def test_register_errors():
    with pytest.raises(AssertionError):
        _ = remote_procedure()("Not a function")

    with pytest.raises(TypeError):

        @remote_procedure(name=123)
        def func():
            ...


def test_registry_items():
    assert rpc_registry["proc_1"] == proc_1
    assert rpc_registry["proc_2"] == proc
