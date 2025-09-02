import pytest

from drakaina.exceptions import DeserializationError
from drakaina.exceptions import SerializationError
from drakaina.serializers import JsonSerializer
from drakaina.serializers import MSGPackSerializer
from drakaina.serializers import ORJsonSerializer
from drakaina.serializers import UJsonSerializer


test_data = {
    "none": None,
    "bool": False,
    "int": 24109,
    "float": 2624362.5,
    "str": "abcdefghijklmnopqrstuvwxyz:;?\n\t//\\t_ABC-XYZ",
    "array": [123, 321.5, True, "xyz_", None],
    "object": {
        "some_int": 123,
        "some_list": ["one", "two"],
    },
    "сyr_str": "Этот текст на кириллице",
}

serializers = (
    JsonSerializer,
    UJsonSerializer,
    ORJsonSerializer,
    MSGPackSerializer,
)


@pytest.mark.parametrize("serializer_class", serializers)
def test_correct_data_deserialization(serializer_class):
    serializer = serializer_class()
    raw_data = serializer.serialize(test_data)
    deserialized_data = serializer.deserialize(raw_data)
    assert test_data == deserialized_data


@pytest.mark.parametrize("serializer_class", serializers)
def test_serialization_errors(serializer_class):
    serializer = serializer_class()

    var = object()

    with pytest.raises(SerializationError):
        serializer.serialize(var)


@pytest.mark.parametrize("serializer_class", serializers[:-1])
def test_deserialization_errors(serializer_class):
    serializer = serializer_class()
    with pytest.raises(DeserializationError):
        serializer.deserialize(b"{")


def test_deserialization_errors_msgpack():
    serializer = MSGPackSerializer()
    with pytest.raises(DeserializationError):
        serializer.deserialize(b"\xd9\x97#DL_")
