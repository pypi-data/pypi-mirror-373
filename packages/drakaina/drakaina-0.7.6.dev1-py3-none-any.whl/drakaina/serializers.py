import json
from collections.abc import Callable
from functools import partial
from io import RawIOBase
from typing import Any
from typing import Optional
from typing import Type
from typing import Union

try:
    import msgpack
except ImportError:
    msgpack = None

try:
    import orjson
except ImportError:
    orjson = None

try:
    import ujson
except ImportError:
    ujson = None

from drakaina.exceptions import DeserializationError
from drakaina.exceptions import SerializationError


class BaseSerializer:
    content_type: str

    def serialize(self, obj: Any) -> bytes:
        raise NotImplementedError

    def deserialize(self, s: Union[bytes, str]) -> Any:
        raise NotImplementedError


class BaseJsonSerializer(BaseSerializer):
    dumps: Callable
    loads: Callable
    DecodeError: Type[Exception]
    content_type: str = "application/json"

    def serialize(self, obj: Any) -> bytes:
        try:
            return self.dumps(obj=obj).encode(encoding="utf-8")
        except (RecursionError, TypeError, ValueError) as exc:
            raise SerializationError from exc

    def deserialize(self, s: Union[bytes, str]) -> Any:
        try:
            return self.loads(s)
        except (self.DecodeError, ValueError) as exc:
            raise DeserializationError from exc


class JsonSerializer(BaseJsonSerializer):
    def __init__(
        self,
        encode_kw: Optional[dict] = None,
        decode_kw: Optional[dict] = None,
        encoder: Optional[Type[json.JSONEncoder]] = None,
        decoder: Optional[Type[json.JSONDecoder]] = None,
    ):
        super().__init__()
        self.dumps = partial(
            json.dumps,
            cls=encoder,
            ensure_ascii=False,
            separators=(",", ":"),
            **encode_kw or {},
        )
        self.loads = partial(json.loads, cls=decoder, **decode_kw or {})
        self.DecodeError = json.JSONDecodeError


class ORJsonSerializer(BaseJsonSerializer):
    def __init__(
        self,
        encode_kw: Optional[dict] = None,
        decode_kw: Optional[dict] = None,
    ):
        if orjson is None:
            raise ModuleNotFoundError(
                "To use `ORJsonSerializer` you must install "
                "the `orjson` package",
            )

        super().__init__()
        self.dumps = partial(orjson.dumps, **encode_kw or {})
        self.loads = partial(orjson.loads, **decode_kw or {})
        self.DecodeError = orjson.JSONDecodeError

    def serialize(self, obj: Any) -> bytes:
        try:
            return self.dumps(obj)
        except (
            orjson.JSONEncodeError,
            RecursionError,
            TypeError,
            ValueError,
        ) as exc:
            raise SerializationError from exc


class UJsonSerializer(BaseJsonSerializer):
    def __init__(
        self,
        encode_kw: Optional[dict] = None,
        decode_kw: Optional[dict] = None,
    ):
        if ujson is None:
            raise ModuleNotFoundError(
                "To use `UJsonSerializer` you must install the `ujson` package",
            )

        super().__init__()
        self.dumps = partial(ujson.dumps, ensure_ascii=False, **encode_kw or {})
        self.loads = partial(ujson.loads, **decode_kw or {})
        self.DecodeError = ujson.JSONDecodeError


class MSGPackSerializer(BaseSerializer):
    content_type: str = "application/x-msgpack"

    def __init__(
        self,
        packer: Optional[Type["msgpack.Packer"]] = None,
        unpacker: Optional[Type["msgpack.Unpacker"]] = None,
        pack_kw: Optional[dict] = None,
        unpack_kw: Optional[dict] = None,
    ):
        if msgpack is None:
            raise ModuleNotFoundError(
                "To use `MSGPackSerializer` you must install "
                "the `msgpack` package",
            )

        self.packer = packer or msgpack.Packer
        self.unpacker = unpacker
        self.pack_kw = pack_kw or {}
        self.unpack_kw = unpack_kw or {}

    def serialize(self, obj: Any) -> bytes:
        try:
            return self.packer(**self.pack_kw).pack(obj)
        except (OverflowError, TypeError, ValueError) as exc:
            raise SerializationError from exc

    def deserialize(self, s: Union[bytes, str, RawIOBase]) -> Any:
        try:
            if self.unpacker is not None:
                return self.unpacker(s, **self.unpack_kw)
            return msgpack.unpackb(s, **self.unpack_kw)
        except (
            msgpack.UnpackException,
            msgpack.ExtraData,
            TypeError,
            ValueError,
        ) as exc:
            raise DeserializationError from exc
