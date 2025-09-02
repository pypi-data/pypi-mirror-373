from __future__ import annotations

from collections import OrderedDict
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import MutableMapping
from collections.abc import MutableSequence
from collections.abc import Sequence
from sys import version_info
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Literal
from typing import Protocol
from typing import Tuple
from typing import Type
from typing import TypedDict
from typing import Union

if version_info < (3, 10):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias

if version_info < (3, 11):
    from enum import Enum
    from typing_extensions import NotRequired

    # Copied from python 3.11

    class ReprEnum(Enum):
        """
        Only changes the repr(), leaving str() and format()
        to the mixed-in type.
        """

    class StrEnum(str, ReprEnum):
        """
        Enum where members are also (and must be) strings
        """

        def __new__(cls, *values):
            "values must already be of type `str`"
            if len(values) > 3:
                raise TypeError("too many arguments for str(): %r" % (values,))
            if len(values) == 1:
                # it must be a string
                if not isinstance(values[0], str):
                    raise TypeError("%r is not a string" % (values[0],))
            if len(values) >= 2:
                # check that encoding argument is a string
                if not isinstance(values[1], str):
                    raise TypeError(
                        "encoding must be a string, not %r" % (values[1],),
                    )
            if len(values) == 3:
                # check that errors argument is a string
                if not isinstance(values[2], str):
                    raise TypeError(
                        "errors must be a string, not %r" % (values[2]),
                    )
            value = str(*values)
            member = str.__new__(cls, value)
            member._value_ = value
            return member

        def _generate_next_value_(name, start, count, last_values):
            """
            Return the lower-cased version of the member name.
            """
            return name.lower()

else:
    from enum import StrEnum
    from typing import NotRequired


"""
JSON-RPC types definitions
"""

JSONSimpleTypes: TypeAlias = Union[str, int, float, bool, None]
JSONTypes: TypeAlias = Union[
    JSONSimpleTypes,
    Mapping[str, JSONSimpleTypes],
    Sequence[JSONSimpleTypes],
]


class JSONRPCRequestObject(TypedDict):
    jsonrpc: Literal["2.0"]
    method: str
    params: NotRequired[list[JSONTypes] | dict[str, JSONTypes]]
    id: NotRequired[str | int | None]


class JSONRPCErrorObject(TypedDict):
    code: int
    message: str
    data: NotRequired[JSONTypes]


class JSONRPCResponseObject(TypedDict):
    jsonrpc: Literal["2.0"]
    result: NotRequired[JSONTypes]
    error: NotRequired[JSONRPCErrorObject]
    id: str | int | None


JSONRPCBatchRequestObject: TypeAlias = Sequence[JSONRPCRequestObject]
JSONRPCRequest: TypeAlias = Union[
    JSONRPCRequestObject,
    JSONRPCBatchRequestObject,
]
JSONRPCBatchResponseObject: TypeAlias = Sequence[JSONRPCResponseObject]
JSONRPCResponse: TypeAlias = Union[
    JSONRPCResponseObject,
    JSONRPCBatchResponseObject,
]


"""
Schema types
"""

json_schema_type_mapping = {
    None: "null",
    type(None): "null",
    "None": "null",
    "NoneType": "null",
    bool: "boolean",
    "bool": "boolean",
    int: "integer",  # number?
    "int": "integer",
    float: "number",
    "float": "number",
    str: "string",
    "str": "string",
    list: "array",
    "list": "array",
    dict: "object",
    "dict": "object",
}


def get_json_schema_type(t: type | str) -> str:
    result = json_schema_type_mapping.get(t)
    if result is None:
        result = str(t)
    return result
    # if isinstance(t, type):
    #     result = json_schema_type_mapping.get(t)
    #     if result is None:
    #         result = str(t)
    #     return result


_JSONSchema = TypedDict(
    "_JSONSchema",
    {
        "$id": NotRequired[str],
        "$ref": NotRequired[str],
        "$dynamicRef": NotRequired[str],
        "$dynamicAnchor": NotRequired[str],
        "$schema": NotRequired[str],
    },
)


class JSONSchema(_JSONSchema):
    """JSON schema.

    https://datatracker.ietf.org/doc/html/draft-bhutton-json-schema-00

    """

    base: NotRequired[str]
    type: NotRequired[str | Sequence[str]]
    description: NotRequired[str]
    format: NotRequired[str]
    required: NotRequired[list[str]]
    default: NotRequired[str]
    properties: NotRequired[Mapping[str, JSONSchema]]


Reference = TypedDict(
    "Reference",
    {
        "$ref": str,  # noqa
        "summary": NotRequired[str],
        "description": NotRequired[str],
    },
)


class ParameterSchema(TypedDict):
    name: NotRequired[str]
    short_description: NotRequired[str]
    description: NotRequired[str]
    type: NotRequired[str]
    default: NotRequired[Any]
    required: NotRequired[bool]
    """Default: False"""
    deprecated: NotRequired[bool]
    """Default: False"""


class MethodSchema(TypedDict):
    name: NotRequired[str]
    short_description: NotRequired[str]
    description: NotRequired[str]
    parameters: NotRequired[OrderedDict[str, ParameterSchema]]
    result: NotRequired[ParameterSchema]
    notification: NotRequired[bool]
    deprecated: NotRequired[bool]
    errors: NotRequired[dict[str, str]]
    example: NotRequired[Any]
    examples: NotRequired[Sequence[Any]]
    # tags: NotRequired[list[ORPCTag | Reference]]
    # paramStructure: NotRequired[Literal["by-name", "by-position", "either"]]
    # TODO: **MethodSchema(errors, examples, tags, )


"""
Schema types - OpenRPC
https://spec.open-rpc.org/
"""

SUPPORTED_OPENRPC_VERSION = "1.3.1"


class OpenRPC(TypedDict):
    openrpc: Literal["1.3.1"]
    info: ORPCInfo
    methods: list[ORPCMethod | Reference]
    servers: NotRequired[list[ORPCServer]]
    components: NotRequired[ORPCComponents]
    externalDocs: NotRequired[ORPCExtDoc]


class ORPCInfo(TypedDict):
    title: str
    version: str
    description: NotRequired[str]
    termsOfService: NotRequired[str]
    contact: NotRequired[ORPCContact]
    license: NotRequired[ORPCLicense]


class ORPCContact(TypedDict):
    name: NotRequired[str]
    url: NotRequired[str]
    email: NotRequired[str]


class ORPCLicense(TypedDict):
    name: str
    url: NotRequired[str]


class ORPCServer(TypedDict):
    name: str
    url: str
    """Runtime Expression"""
    summary: NotRequired[str]
    description: NotRequired[str]
    variables: NotRequired[Mapping[str, ORPCServerVar]]


class ORPCServerVar(TypedDict):
    default: str
    enum: NotRequired[list[str]]
    description: NotRequired[str]


class ORPCMethod(TypedDict):
    name: str
    params: list[ORPCContentDescriptor | Reference]
    result: NotRequired[ORPCContentDescriptor | Reference]
    tags: NotRequired[list[ORPCTag | Reference]]
    summary: NotRequired[str]
    description: NotRequired[str]
    externalDocs: NotRequired[ORPCExtDoc]
    deprecated: NotRequired[bool]
    """Default: False"""
    servers: NotRequired[list[ORPCServer]]
    errors: NotRequired[list[JSONRPCErrorObject | Reference]]
    links: NotRequired[list[ORPCLink | Reference]]
    paramStructure: NotRequired[Literal["by-name", "by-position", "either"]]
    examples: NotRequired[list[ORPCExamplePairing]]


class ORPCContentDescriptor(TypedDict):
    name: str
    schema: JSONSchema
    summary: NotRequired[str]
    description: NotRequired[str]
    required: NotRequired[bool]
    """Default: False"""
    deprecated: NotRequired[bool]
    """Default: False"""


class ORPCExamplePairing(TypedDict):
    name: NotRequired[str]
    summary: NotRequired[str]
    description: NotRequired[str]
    params: NotRequired[list[ORPCExample | Reference]]
    result: NotRequired[ORPCExample | Reference]


class ORPCExample(TypedDict):
    name: NotRequired[str]
    summary: NotRequired[str]
    description: NotRequired[str]
    value: NotRequired[Any]
    externalValue: NotRequired[str]


class ORPCLink(TypedDict):
    name: str
    summary: NotRequired[str]
    description: NotRequired[str]
    method: NotRequired[str]
    params: NotRequired[Mapping[str, Any | str]]
    """Mapping[str, Any | 'Runtime Expression']"""
    server: NotRequired[ORPCServer]


class ORPCComponents(TypedDict):
    contentDescriptors: NotRequired[Mapping[str, ORPCContentDescriptor]]
    schemas: NotRequired[Mapping[str, JSONSchema]]
    examples: NotRequired[Mapping[str, ORPCExample]]
    links: NotRequired[Mapping[str, ORPCLink]]
    errors: NotRequired[Mapping[str, JSONRPCErrorObject]]
    examplePairingObjects: NotRequired[Mapping[str, ORPCExamplePairing]]
    tags: NotRequired[Mapping[str, ORPCTag]]


class ORPCTag(TypedDict):
    name: str
    summary: NotRequired[str]
    description: NotRequired[str]
    externalDocs: NotRequired[ORPCExtDoc]


class ORPCExtDoc(TypedDict):
    url: str
    description: NotRequired[str]


class ORPC:
    SUPPORTED_VERSION = SUPPORTED_OPENRPC_VERSION
    OpenRPC = OpenRPC
    Info = ORPCInfo
    Contact = ORPCContact
    License = ORPCLicense
    Server = ORPCServer
    ServerVar = ORPCServerVar
    Method = ORPCMethod
    ContentDescriptor = ORPCContentDescriptor
    Schema = JSONSchema
    ExamplePairing = ORPCExamplePairing
    Example = ORPCExample
    Link = ORPCLink
    Components = ORPCComponents
    Tag = ORPCTag
    ExtDoc = ORPCExtDoc
    Reference = Reference

    type_mapping = get_json_schema_type

    @classmethod
    def method_by_schema(
        cls,
        method_schema: MethodSchema,
        default_name: str | None = None,
    ) -> ORPCMethod:
        if default_name is None:
            default_name = method_schema["name"]
        method = ORPCMethod(
            name=default_name,
            params=[],
            result=ORPCContentDescriptor(),
            deprecated=method_schema.get("deprecated", False),
        )
        if "short_description" in method_schema:
            method["summary"] = method_schema["short_description"]
        if "description" in method_schema:
            method["description"] = method_schema["description"]

        # Fill parameters schema
        parameters = method_schema.get("parameters", {})
        for parameter_name, parameter in parameters.items():
            method["params"].append(
                cls.content_descriptor_by_parameter(
                    parameter,
                    default_name=parameter_name,
                ),
            )

        # Fill result schema
        if "result" in method_schema:
            method["result"] = cls.content_descriptor_by_result(
                method_schema["result"],
            )

        return method

    @staticmethod
    def content_descriptor_by_parameter(
        parameter: ParameterSchema,
        default_name: str | None = None,
    ) -> ORPCContentDescriptor:
        cd = ORPCContentDescriptor(
            name=parameter.get("name", default_name),
            schema=JSONSchema(),
            required=parameter.get("required", False),
            deprecated=parameter.get("deprecated", False),
        )
        if "type" in parameter:
            cd["schema"]["type"] = get_json_schema_type(
                parameter["type"],
            )
        if "default" in parameter:
            cd["schema"]["default"] = parameter["default"]
        if "short_description" in parameter:
            cd["summary"] = parameter["short_description"]
        if "description" in parameter:
            cd["description"] = parameter["description"]

        return cd

    @staticmethod
    def content_descriptor_by_result(
        result_schema: dict,
        default_name: str = "result",
    ) -> ORPCContentDescriptor:
        cd = ORPC.ContentDescriptor(
            name=result_schema.get("name", default_name),
            schema=ORPC.Schema(),
        )
        if "type" in result_schema:
            cd["schema"]["type"] = get_json_schema_type(
                result_schema["type"],
            )
        if "description" in result_schema:
            cd["summary"] = result_schema["description"]
            cd["description"] = result_schema["description"]

        return cd


"""
Schema types - OpenAPI
https://github.com/OAI/OpenAPI-Specification
"""

SUPPORTED_OPENAPI_VERSION = "3.0.0"


class OpenAPI(TypedDict):
    openapi: Literal["3.1.0"]
    info: OASInfo
    jsonSchemaDialect: NotRequired[str]
    """URI"""
    servers: NotRequired[list[OASServer]]
    paths: NotRequired[OASPaths]
    """OASPaths["/{path}", OASPathItem]"""
    webhooks: NotRequired[Mapping[str, OASPathItem | Reference]]
    components: NotRequired[OASComponents]
    security: NotRequired[list[OASSecurityRequirement]]
    tags: NotRequired[list[OASTag]]
    externalDocs: NotRequired[OASExtDoc]


class OASInfo(TypedDict):
    title: str
    version: str
    summary: NotRequired[str]
    description: NotRequired[str]
    termsOfService: NotRequired[str]
    contact: NotRequired[OASContact]
    license: NotRequired[OASLicense]


class OASContact(TypedDict):
    name: NotRequired[str]
    url: NotRequired[str]
    email: NotRequired[str]


class OASLicense(TypedDict):
    name: str
    identifier: NotRequired[str]
    url: NotRequired[str]


class OASServer(TypedDict):
    url: str
    description: NotRequired[str]
    variables: NotRequired[Mapping[str, OASServerVar]]


class OASServerVar(TypedDict):
    default: str
    enum: NotRequired[list[str]]
    description: NotRequired[str]


class OASComponents(TypedDict):
    schemas: NotRequired[Mapping[str, OASSchema]]
    responses: NotRequired[Mapping[str, OASResponse | Reference]]
    parameters: NotRequired[Mapping[str, OASParameter | Reference]]
    examples: NotRequired[Mapping[str, OASExample | Reference]]
    requestBodies: NotRequired[Mapping[str, OASRequestBody | Reference]]
    headers: NotRequired[Mapping[str, OASHeader | Reference]]
    securitySchemes: NotRequired[Mapping[str, OASSecurityScheme | Reference]]
    links: NotRequired[Mapping[str, OASLink | Reference]]
    callbacks: NotRequired[Mapping[str, OASCallback | Reference]]
    pathItems: NotRequired[Mapping[str, OASPathItem | Reference]]


OASPathItemRef = TypedDict(
    "OASPathItemRef",
    {"$ref": NotRequired[str]},
)


class OASPathItem(OASPathItemRef):
    summary: NotRequired[str]
    description: NotRequired[str]
    get: NotRequired[OASOperation]
    put: NotRequired[OASOperation]
    post: NotRequired[OASOperation]
    delete: NotRequired[OASOperation]
    options: NotRequired[OASOperation]
    head: NotRequired[OASOperation]
    patch: NotRequired[OASOperation]
    trace: NotRequired[OASOperation]
    servers: NotRequired[OASServer]
    parameters: NotRequired[OASParameter | Reference]


OASPaths = TypedDict("OASPaths", {"/{path}": OASPathItem})


class OASOperation(TypedDict):
    tags: NotRequired[list[str]]
    summary: NotRequired[str]
    description: NotRequired[str]
    externalDocs: NotRequired[OASExtDoc]
    operationId: NotRequired[str]
    parameters: NotRequired[Sequence[OASParameter | Reference]]
    requestBody: NotRequired[OASRequestBody | Reference]
    responses: NotRequired[OASResponses]
    callbacks: NotRequired[Mapping[str, OASCallback | Reference]]
    deprecated: NotRequired[bool]
    security: NotRequired[Sequence[OASSecurityRequirement]]
    servers: NotRequired[Sequence[OASServer]]


class OASExtDoc(TypedDict):
    url: str
    description: NotRequired[str]


class OASParameterLocation(StrEnum):
    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    COOKIE = "cookie"


OASParameterIn = TypedDict(
    "OASParameterIn",
    {"in": OASParameterLocation},
)


class OASParameter(OASParameterIn):
    name: str
    # in: str
    description: NotRequired[str]
    required: NotRequired[bool]
    """required = True if `in` == 'path'"""
    deprecated: NotRequired[bool]
    allowEmptyValue: NotRequired[bool]
    style: NotRequired[str]
    explode: NotRequired[bool]
    allowReserved: NotRequired[bool]
    schema: NotRequired[OASSchema]
    example: NotRequired[Any]
    examples: NotRequired[Mapping[str, OASExample | Reference]]
    content: NotRequired[Mapping[str, OASMediaType]]
    """A parameter MUST contain either a schema property, or
    a content property, but not both."""


class OASRequestBody(TypedDict):
    content: Mapping[str, OASMediaType]
    description: NotRequired[str]
    required: NotRequired[bool]


class OASMediaType(TypedDict):
    schema: NotRequired[OASSchema]
    example: NotRequired[Any]
    examples: NotRequired[Mapping[str, OASExample | Reference]]
    encoding: NotRequired[Mapping[str, OASEncoding]]


class OASEncoding(TypedDict):
    contentType: NotRequired[str]
    headers: NotRequired[Mapping[str, OASHeader | Reference]]
    style: NotRequired[str]
    explode: NotRequired[bool]
    allowReserved: NotRequired[bool]


class OASResponse(TypedDict):
    description: str
    headers: NotRequired[Mapping[str, OASHeader | Reference]]
    content: NotRequired[Mapping[str, OASMediaType]]
    links: NotRequired[Mapping[str, OASLink | Reference]]


OASResponses = TypedDict(
    "OASResponses",
    {
        "{status_code}": NotRequired[Union[OASResponse, Reference]],
        "default": NotRequired[Union[OASResponse, Reference]],
    },
)


OASCallback = Dict[str, Union[OASPathItem, Reference]]


class OASExample(TypedDict):
    summary: NotRequired[str]
    description: NotRequired[str]
    value: NotRequired[Any]
    externalValue: NotRequired[str]


class OASLink(TypedDict):
    operationRef: NotRequired[str]
    operationId: NotRequired[str]
    parameters: NotRequired[Mapping[str, Any | str]]
    """NotRequired[Mapping[str, Any | {expression}]]"""
    description: NotRequired[str]
    server: NotRequired[OASServer]


class OASHeader(TypedDict):
    description: NotRequired[str]
    required: NotRequired[bool]
    deprecated: NotRequired[bool]
    allowEmptyValue: NotRequired[bool]
    style: NotRequired[str]
    explode: NotRequired[bool]
    allowReserved: NotRequired[bool]
    schema: NotRequired[OASSchema]
    example: NotRequired[Any]
    examples: NotRequired[Mapping[str, OASExample | Reference]]
    content: NotRequired[Mapping[str, OASMediaType]]
    """A parameter MUST contain either a schema property, or
    a content property, but not both."""


class OASTag(TypedDict):
    name: str
    description: NotRequired[str]
    externalDocs: NotRequired[OASExtDoc]


class OASSchema(JSONSchema):
    discriminator: NotRequired[OASDiscriminator]
    xml: NotRequired[OASXML]
    externalDocs: NotRequired[OASExtDoc]
    example: NotRequired[Any]


class OASDiscriminator(TypedDict):
    propertyName: str
    mapping: NotRequired[Mapping[str, str]]


class OASXML(TypedDict):
    name: NotRequired[str]
    namespace: NotRequired[str]
    prefix: NotRequired[str]
    attribute: NotRequired[bool]
    wrapped: NotRequired[bool]


class OASSecuritySchemeType(StrEnum):
    API_KEY = "apiKey"


class OASSecuritySchemeLocation(StrEnum):
    QUERY = "query"
    HEADER = "header"
    COOKIE = "cookie"


OASSecuritySchemeIn = TypedDict(
    "OASSecuritySchemeIn",
    {"in": OASSecuritySchemeLocation},
)


class OASSecurityScheme(OASSecuritySchemeIn):
    type: OASSecuritySchemeType
    name: str
    scheme: str
    flows: OASOAuthFlows
    openIdConnectUrl: str
    description: NotRequired[str]
    bearerFormat: NotRequired[str]


class OASOAuthFlows(TypedDict):
    implicit: NotRequired[OASOAuthFlow]
    password: NotRequired[OASOAuthFlow]
    clientCredentials: NotRequired[OASOAuthFlow]
    authorizationCode: NotRequired[OASOAuthFlow]


class OASOAuthFlow(TypedDict):
    authorizationUrl: str
    tokenUrl: str
    scopes: str
    refreshUrl: NotRequired[str]


OASSecurityRequirement = Dict[str, list[str]]


class OAPI:
    SUPPORTED_VERSION = SUPPORTED_OPENAPI_VERSION
    OpenAPI = OpenAPI
    Info = OASInfo
    Contact = OASContact
    License = OASLicense
    Server = OASServer
    ServerVar = OASServerVar
    Components = OASComponents
    Paths = OASPaths
    PathItem = OASPathItem
    Operation = OASOperation
    ExtDoc = OASExtDoc
    ParameterLocation = OASParameterLocation
    Parameter = OASParameter
    RequestBody = OASRequestBody
    MediaType = OASMediaType
    Encoding = OASEncoding
    Responses = OASResponses
    Response = OASResponse
    Callback = OASCallback
    Example = OASExample
    Link = OASLink
    Header = OASHeader
    Tag = OASTag
    Reference = Reference
    Schema = OASSchema
    Discriminator = OASDiscriminator
    XML = OASXML
    SecurityScheme = OASSecurityScheme
    OAuthFlows = OASOAuthFlows
    OAuthFlow = OASOAuthFlow
    SecurityRequirement = OASSecurityRequirement

    type_mapping = get_json_schema_type

    """
    TODO: Need to refactor and improve the circuit generation
          with these methods.
    """

    @staticmethod
    def operation_by_schema(
        method_schema: MethodSchema,
        default_name: str | None = None,
    ) -> OASOperation:
        operation = OAPI.Operation(
            operationId=default_name or method_schema.get("name"),
            parameters=[],
            deprecated=method_schema.get("deprecated", False),
        )
        if "short_description" in method_schema:
            operation["summary"] = method_schema["short_description"]
        if "description" in method_schema:
            operation["description"] = method_schema["description"]

        # Fill request body
        operation["requestBody"] = OAPI.request_body_by_schema(
            method_schema,
        )

        # Fill result schema
        operation["responses"] = OAPI.responses_by_schema(method_schema)

        return operation

    @staticmethod
    def parameters_by_schema(method_schema: MethodSchema) -> list[OASParameter]:
        result = []
        parameters = method_schema.get("parameters", {})
        for param_name, parameter in parameters.items():
            param = OAPI.Parameter(
                name=parameter.get("name", param_name),
                schema=OAPI.Schema(),
                required=parameter.get("required", False),
                deprecated=parameter.get("deprecated", False),
            )
            if "type" in parameter:
                param["schema"]["type"] = OAPI.type_mapping(
                    parameter["type"],
                )
            if "default" in parameter:
                param["schema"]["default"] = parameter["default"]
            if "short_description" in parameter:
                param["summary"] = parameter["short_description"]
            if "description" in parameter:
                param["description"] = parameter["description"]

            result.append(param)

        return result

    @staticmethod
    def request_body_by_schema(method_schema: MethodSchema) -> OASRequestBody:
        parameters = method_schema.get("parameters", {}).items()
        media = OAPI.MediaType(
            schema=OAPI.Schema(
                type="object",
                properties={
                    "jsonrpc": {
                        "type": "string",
                        "description": "Protocol version",
                    },
                    "method": {
                        "type": "string",
                        "description": "Procedure (method) name",
                    },
                    "params": {
                        "type": "object",
                        "properties": {
                            param_name: {
                                "default": parameter.get("default", ""),
                                "description": parameter.get(
                                    "description",
                                    "",
                                ),
                                "deprecated": parameter.get(
                                    "deprecated",
                                    False,
                                ),
                            }
                            for param_name, parameter in parameters
                        },
                    },
                    "id": {
                        "type": "string",
                    },
                },
                required=["jsonrpc", "method"],
            ),
        )
        if "example" in method_schema:
            media["example"] = method_schema["example"]
        if "examples" in method_schema:
            media["examples"] = method_schema["examples"]
        return OASRequestBody(
            content={"application/json": media},
            description="JSON-RPC 2.0 Request Object",
            required=True,
        )

    @staticmethod
    def responses_by_schema(method_schema: MethodSchema) -> OASResponses:
        if "result" in method_schema:
            result_schema = method_schema["result"]
            jsonrpc_object = {
                "jsonrpc": OASSchema(type="string", default="2.0"),
                "result": OASSchema(),
                "id": OASSchema(type="string"),
            }
            if "type" in result_schema:
                jsonrpc_object["result"]["type"] = get_json_schema_type(
                    result_schema["type"],
                )

            media = OASMediaType(
                schema=OASSchema(type="object", properties=jsonrpc_object),
            )
            if "description" in result_schema:
                media["schema"]["description"] = result_schema["description"]
        else:
            media = OASMediaType(
                schema=OAPI.Schema(
                    type="object",
                    properties=dict(
                        jsonrpc=dict(type="string", default="2.0"),
                        result=dict(type="null"),
                        id=dict(type="string"),
                    ),
                ),
            )
        return OAPI.Responses(
            **{
                "200": OAPI.Response(
                    description="JSON-RPC 2.0 Response Object",
                    content={"application/json": media},
                ),
            },
        )


"""
WSGI types definitions
PEP 3333 – Python Web Server Gateway Interface
https://peps.python.org/pep-3333/
"""

WSGIEnvironmentKeys: TypeAlias = Literal[
    # for CGI
    # https://datatracker.ietf.org/doc/html/draft-coar-cgi-v11-03
    "AUTH_TYPE",
    "CONTENT_LENGTH",
    "CONTENT_TYPE",
    "GATEWAY_INTERFACE",
    "PATH_INFO",
    "PATH_TRANSLATED",
    "QUERY_STRING",
    "REMOTE_ADDR",
    "REMOTE_HOST",
    "REMOTE_IDENT",
    "REMOTE_USER",
    "REQUEST_METHOD",
    "SCRIPT_NAME",
    "SERVER_NAME",
    "SERVER_PORT",
    "SERVER_PROTOCOL",
    "SERVER_SOFTWARE",
    # for WSGI
    "wsgi.errors",
    "wsgi.input",
    "wsgi.multiprocess",
    "wsgi.multithread",
    "wsgi.run_once",
    "wsgi.url_scheme",
    "wsgi.version",
]
# for framework needs
WSGIDrakainaKeys: TypeAlias = Literal[
    "drakaina.app",
    "drakaina.is_authenticated",
]
WSGIEnvironment: TypeAlias = MutableMapping[str, Any]
WSGIExceptionInfo: TypeAlias = Tuple[Type[BaseException], BaseException, Any]


class WSGIStartResponse(Protocol):
    def __call__(
        self,
        status: str,
        headers: MutableSequence[tuple[str, str]],
        exc_info: WSGIExceptionInfo | None = ...,
    ) -> Callable[[bytes], Any]:
        ...


WSGIResponse: TypeAlias = Iterable[bytes]
WSGIApplication: TypeAlias = Callable[
    [WSGIEnvironment, WSGIStartResponse],
    WSGIResponse,
]


class WSGIInputStream(Protocol):
    def read(self, size: int | None = None) -> bytes:
        ...

    def readline(self) -> bytes:
        ...

    def readlines(self, hint: Any | None) -> Iterable[bytes]:
        ...

    def __iter__(self) -> bytes:
        ...


class WSGIErrorsStream(Protocol):
    def flush(self) -> None:
        ...

    def write(self, s: str) -> None:
        ...

    def writelines(self, seq: Sequence[str]) -> None:
        ...


"""
ASGI types definitions
https://asgi.readthedocs.io/en/latest/
"""

ASGIScope: TypeAlias = MutableMapping[str, Any]
ASGIMessage: TypeAlias = MutableMapping[str, Any]

ASGIReceive: TypeAlias = Callable[[], Awaitable[ASGIMessage]]
ASGISend: TypeAlias = Callable[[ASGIMessage], Awaitable[None]]

ASGIApplication: TypeAlias = Callable[
    [ASGIScope, ASGIReceive, ASGISend],
    Awaitable[None],
]


"""
Helpful types
"""


class Comparator(Protocol):
    def __call__(
        self,
        required: Iterable[str],
        provided: Iterable[str],
    ) -> bool:
        ...


class ProxyRequest(MutableMapping):
    """A wrapper class for environment mapping.

    :param environment:

    """

    __slots__ = ("__environment",)

    def __init__(self, environment: ASGIScope | WSGIEnvironment):
        self.__environment = environment

    def __getitem__(self, item):
        return self.__environment[item]

    def __setitem__(self, key, value):
        self.__environment[key] = value

    def __delitem__(self, key):
        del self.__environment[key]

    def __iter__(self):
        return iter(self.__environment.keys())

    def __contains__(self, item):
        return item in self.__environment.keys()

    def __len__(self):
        return len(self.__environment)

    def keys(self):
        return self.__environment.keys()

    def values(self):
        return self.__environment.values()

    def items(self):
        return self.__environment.items()

    def get(self, key, default=None):
        return self.__environment.get(key, default)

    def clear(self):
        self.__environment.clear()

    def setdefault(self, key, default=None):
        self.__environment.setdefault(key, default)

    def pop(self, key, default=None):
        return self.__environment.pop(key, default)

    def popitem(self):
        return self.__environment.popitem()

    def copy(self):
        return self.__class__(self.__environment.copy())

    def update(self, *args, **kwargs):
        return self.__environment.update(*args, **kwargs)

    def __getattr__(self, item):
        if item in ("__environment", "_ProxyRequest__environment"):
            super().__getattribute__(item)
        return self.__environment[item]

    def __setattr__(self, key, value):
        if key in ("__environment", "_ProxyRequest__environment"):
            super().__setattr__(key, value)
        else:
            self.__environment[key] = value

    def __delattr__(self, item):
        del self.__environment[item]


AnyRequest: TypeAlias = Union[
    ASGIScope,
    WSGIEnvironment,
    ProxyRequest,
]
