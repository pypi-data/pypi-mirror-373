"""Base exceptions module"""


class RPCError(Exception):
    """Base error class for RPC protocols"""

    message: str = None

    def __init__(self, *args):
        super().__init__(*args)
        if len(args) > 0:
            self.message = str(args[0])

    def __str__(self) -> str:
        if self.message:
            return f"{self.__class__.__name__} ({self.message})"
        return f"{self.__class__.__name__}"

    def __repr__(self) -> str:
        if self.message:
            return f"<{self.__class__.__name__} ({self.message})>"
        return f"<{self.__class__.__name__}>"

    def as_dict(self) -> dict[str, str]:
        return {
            "error": self.__class__.__name__,
            "message": self.message or "",
        }


class SerializationError(RPCError):
    """Serialization error"""


class DeserializationError(RPCError):
    """Deserialization error"""


class InternalServerError(RPCError):
    """Server error"""


class BadRequestError(RPCError):
    """Bad request error"""


class NotFoundError(BadRequestError):
    """Not found error"""


class InvalidParametersError(BadRequestError):
    """Invalid parameters error"""


class AuthenticationFailedError(RPCError):
    """Authentication failed"""


class InvalidTokenError(AuthenticationFailedError):
    """Invalid token error"""


class ForbiddenError(AuthenticationFailedError):
    """Forbidden error"""


class InvalidPermissionsError(BadRequestError):
    """Invalid permissions error"""
