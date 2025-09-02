from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Iterator
from collections.abc import KeysView
from collections.abc import Mapping
from collections.abc import ValuesView
from inspect import cleandoc
from inspect import Parameter
from inspect import Signature
from inspect import signature
from typing import Any

from drakaina.constants import RPC_META
from drakaina.constants import RPC_NAME
from drakaina.constants import RPC_PROVIDE_REQUEST
from drakaina.constants import RPC_REGISTERED
from drakaina.constants import RPC_REGISTRY
from drakaina.constants import RPC_SCHEMA
from drakaina.types import MethodSchema
from drakaina.types import ParameterSchema
from drakaina.utils import short_description_by_name
from drakaina.utils import unwrap_func

try:
    from docstring_parser import parse as parse_doc
except ImportError:
    parse_doc = None

__all__ = (
    "is_rpc_procedure",
    "RPCRegistry",
)

# Reserved procedure argument names
RESERVED_KWARGS = ("cls", "self", "request")


def is_rpc_procedure(func: Callable) -> bool:
    return hasattr(unwrap_func(func), RPC_REGISTERED)


class RPCRegistry(Mapping[str, Callable[..., Any]]):
    """Registry of remote procedures."""

    _remote_procedures: dict[str, Callable[..., Any]]

    def __init__(self):
        self._remote_procedures = {}

    def register_procedure(
        self,
        procedure: Callable[..., Any],
        name: str | None = None,
        provide_request: bool | None = None,
        metadata: dict | None = None,
    ):
        """Register a function as a remote procedure.

        :param procedure: Registered procedure.
        :param name: Procedure name. Default as function name.
        :param provide_request:
            If `True`, then the request object or context can be supplied to
            the procedure as a `request` argument.
        :param metadata:
            Metadata that can be processed by middleware or an extension.

        """
        assert callable(procedure)

        procedure_name = procedure.__name__ if name is None else name
        if procedure_name.startswith("rpc."):
            raise ValueError(
                "Method names that begin with 'rpc.' are reserved for "
                "rpc internal methods and extensions and MUST NOT be used "
                "for anything else.",
            )

        # Inspection of the procedure interface and its documentation.
        schema = self.inspect_procedure(procedure, metadata)
        schema["name"] = procedure_name

        self.__register_callable(
            func=procedure,
            name=procedure_name,
            provide_request=provide_request,
            schema=schema,
            metadata=metadata,
        )

    def register_rpc_extension(
        self,
        extension_procedure: Callable[..., Any],
        extension_name: str,
        provide_request: bool | None = None,
        metadata: dict | None = None,
    ):
        """Register a function as an RPC extension.

        :param extension_procedure: Registered RPC extension.
        :param extension_name: Procedure name.
        :param provide_request:
            If `True`, then the request object or context can be supplied to
            the procedure as a `request` argument.
        :param metadata:
            Metadata that can be processed by middleware or an extension.
        """
        assert callable(extension_procedure)
        assert extension_name and extension_name.startswith("rpc.")

        self.__register_callable(
            func=extension_procedure,
            name=extension_name,
            provide_request=provide_request,
            metadata=metadata,
        )

    @staticmethod
    def inspect_procedure(
        procedure: Callable[..., Any],
        metadata: dict = None,
    ) -> MethodSchema:
        """Inspects the signature and generates a schematic of the function.

        :param procedure:
            Procedure for inspection.
        :param metadata:
            The metadata specified when registering the procedure.
            May contain additional information about the signature or
            documentation about the procedure.
        :return:
            Returns the schema for the given procedure filled with
            the found data.

        """
        if "method_schema" in metadata:
            schema = metadata["method_schema"]
        else:
            schema = MethodSchema(parameters=OrderedDict(), result={})

        if callable(parse_doc):
            docstring = parse_doc(getattr(procedure, "__doc__", ""))
            docstring.params_dict = {p.arg_name: p for p in docstring.params}
            if docstring.short_description:
                schema.setdefault(
                    "short_description",
                    docstring.short_description,
                )
            if docstring.long_description:
                schema.setdefault("description", docstring.long_description)
        else:
            docstring = None
            schema.setdefault(
                "short_description",
                short_description_by_name(procedure.__name__),
            )
            schema.setdefault(
                "description",
                metadata.get("description")
                or cleandoc(getattr(procedure, "__doc__", None) or ""),
            )

        proc_signature = signature(procedure)
        # Get parameters info from signature
        for parameter in proc_signature.parameters.values():
            if parameter.name in RESERVED_KWARGS:
                # Skip all reserved args
                continue

            if parameter.name in schema["parameters"]:
                param_schema = schema["parameters"][parameter.name]
            else:
                param_schema = ParameterSchema(
                    name=parameter.name,
                    kind=parameter.kind,  # noqa
                )

            # Set type
            if parameter.annotation is not Parameter.empty:
                if isinstance(parameter.annotation, type):
                    _type = parameter.annotation.__name__
                else:
                    _type = parameter.annotation
                param_schema.setdefault("type", _type)

            # Set default value
            if parameter.default is not Parameter.empty:
                param_schema.setdefault("default", parameter.default)
                param_schema.setdefault("required", False)
            else:
                param_schema.setdefault("required", True)

            # Get values from docstring
            if docstring and parameter.name in docstring.params_dict:
                param_doc = docstring.params_dict[parameter.name]
                param_schema.setdefault("type", param_doc.type_name)
                param_schema.setdefault("description", param_doc.description)

            # Add in method schema
            schema["parameters"].setdefault(parameter.name, param_schema)

        # Get return info from signature
        if proc_signature.return_annotation is not Signature.empty:
            # Set return type
            if isinstance(proc_signature.return_annotation, type):
                _type = proc_signature.return_annotation.__name__
            else:
                _type = proc_signature.return_annotation
            schema["result"].setdefault("type", _type)

        # Get values from docstring
        if docstring:
            # Return info
            returns = docstring.returns
            if returns and returns.return_name:
                schema["result"].setdefault("name", returns.return_name)
            if returns and returns.type_name:
                schema["result"].setdefault("type", returns.type_name)
            if returns and returns.description:
                schema["result"].setdefault("description", returns.description)
            # Exceptions info
            raises = docstring.raises
            if raises:
                schema["errors"] = []
                for exc in raises:
                    exc_schema = {"type": exc.type_name}
                    if exc.description:
                        exc_schema["description"] = exc.description
                    schema["errors"].append(exc_schema)
            # Deprecation info
            if docstring.deprecation:
                ...
            if docstring.examples:
                ...

        return schema

    def __register_callable(
        self,
        func: Callable[..., Any],
        name: str,
        provide_request: bool = False,
        schema: MethodSchema | dict | None = None,
        metadata: dict | None = None,
    ):
        """Placing the function in the registry with the specified name.

        :param func: Placed function.
        :param name: Name of function.
        :param provide_request:
            If `True`, then the request object or context can be supplied to
            the procedure as a `request` argument.
        :param schema: The function schema needed to create the documentation.
        :param metadata:
            Metadata that can be processed by middleware or an extension.

        """
        if name in self._remote_procedures:
            raise ValueError(
                "A procedure with this name is already registered.",
            )

        # The loop is for applying attributes to wrapped functions.
        # If the provided function is not wrapped, the attributes will be
        # applied once
        _func = func
        while _func is not None:
            setattr(_func, RPC_REGISTRY, self)
            setattr(_func, RPC_REGISTERED, True)
            setattr(_func, RPC_NAME, name)
            setattr(_func, RPC_PROVIDE_REQUEST, provide_request)
            setattr(_func, RPC_SCHEMA, schema or {})
            setattr(_func, RPC_META, metadata or {})
            # If it's a wrapped function
            _func = getattr(_func, "__wrapped__", None)

        self._remote_procedures[name] = func

    def replace(
        self,
        procedure: Callable[..., Any],
        new_procedure: Callable[..., Any],
    ):
        """Special method for use in cases where
        a decorator wrap procedure is required.

        :param procedure:
        :param new_procedure:

        """
        procedure_name = getattr(procedure, RPC_NAME, None)
        if procedure_name is None:
            raise TypeError(f"Callable {procedure} is not an rpc procedure.")
        self._remote_procedures[procedure_name] = new_procedure

    def __getitem__(self, key: str) -> Callable[..., Any] | None:
        # Intentionally suppress the rise of the exception,
        # and simply return None if there is no specified procedure.
        return self._remote_procedures.get(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self._remote_procedures)

    def __len__(self) -> int:
        return len(self._remote_procedures)

    def __contains__(self, item: str) -> bool:
        if not isinstance(item, str):
            raise TypeError(
                f"The procedure name must be a str, not {type(item)}.",
            )
        return item in self._remote_procedures.__contains__()

    def keys(self) -> KeysView[str]:
        return self._remote_procedures.keys()

    def items(self) -> Iterable[tuple[str, Callable[..., Any]]]:
        return self._remote_procedures.items()

    def values(self) -> ValuesView[Callable[..., Any]]:
        return self._remote_procedures.values()

    def get(
        self,
        key: str,
        default: Callable[..., Any] | None = None,
    ) -> Callable[..., Any] | None:
        if not isinstance(key, str):
            raise TypeError(
                f"The procedure name must be a str, not {type(key)}.",
            )
        if default is not None and not callable(default):
            raise TypeError("The default argument must be a callable.")
        return self._remote_procedures.get(key, default)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, self.__class__)
            and self._remote_procedures == other._remote_procedures
        )

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
