from drakaina.constants import ENV_APP
from drakaina.constants import ENV_AUTH_PAYLOAD
from drakaina.constants import ENV_AUTH_SCOPES
from drakaina.constants import ENV_IS_AUTHENTICATED
from drakaina.constants import ENV_USER
from drakaina.constants import ENV_USER_ID
from drakaina.decorators import check_permissions
from drakaina.decorators import login_required
from drakaina.decorators import match_all
from drakaina.decorators import match_any
from drakaina.decorators import remote_procedure
from drakaina.registries import RPCRegistry

__all__ = (
    "RPCRegistry",
    "rpc_registry",
    "remote_procedure",
    "check_permissions",
    "login_required",
    "match_all",
    "match_any",
    "ENV_APP",
    "ENV_IS_AUTHENTICATED",
    "ENV_USER",
    "ENV_USER_ID",
    "ENV_AUTH_PAYLOAD",
    "ENV_AUTH_SCOPES",
)

# General registry
rpc_registry = RPCRegistry()
