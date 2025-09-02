import inspect
import logging
from typing import Literal

import Secweb.ContentSecurityPolicy
import Secweb.StrictTransportSecurity

from .utils import deep_merge

__all__ = ["logger"]

USER_TABLE = "ab_user"
USER_SEQUENCE = "ab_user_id_seq"
ROLE_TABLE = "ab_role"
ROLE_SEQUENCE = "ab_role_id_seq"
PERMISSION_TABLE = "ab_permission"
PERMISSION_SEQUENCE = "ab_permission_id_seq"
API_TABLE = "ab_view_menu"
API_SEQUENCE = "ab_view_menu_id_seq"
PERMISSION_API_TABLE = "ab_permission_view"
PERMISSION_API_SEQUENCE = "ab_permission_view_id_seq"
ASSOC_PERMISSION_API_ROLE_TABLE = "ab_permission_view_role"
ASSOC_PERMISSION_API_ROLE_SEQUENCE = "ab_permission_view_role_id_seq"
ASSOC_USER_ROLE_TABLE = "ab_user_role"
ASSOC_USER_ROLE_SEQUENCE = "ab_user_role_id_seq"
OAUTH_TABLE = "ab_oauth_account"
OAUTH_SEQUENCE = "ab_oauth_account_id_seq"
ACCESSTOKEN_TABLE = "ab_accesstoken"

FASTAPI_RTK_TABLES = [
    USER_TABLE,
    ROLE_TABLE,
    PERMISSION_TABLE,
    API_TABLE,
    PERMISSION_API_TABLE,
    ASSOC_PERMISSION_API_ROLE_TABLE,
    ASSOC_USER_ROLE_TABLE,
    OAUTH_TABLE,
    ACCESSTOKEN_TABLE,
]

BASE_APIS = Literal[
    "AuthApi",
    "InfoApi",
    "PermissionsApi",
    "PermissionViewApi",
    "RolesApi",
    "UsersApi",
    "ViewsMenusApi",
]

AVAILABLE_ROUTES = Literal[
    "image",
    "file",
    "info",
    "download",
    "bulk",
    "get_list",
    "get",
    "post",
    "put",
    "delete",
]

PERMISSION_PREFIX = "can_"
DEFAULT_ADMIN_ROLE = "Admin"
DEFAULT_PUBLIC_ROLE = "Public"
DEFAULT_API_MAX_PAGE_SIZE = 25
DEFAULT_TOKEN_URL = "/api/v1/auth/jwt/login"
DEFAULT_SECRET = "SUPERSECRET"
DEFAULT_COOKIE_NAME = "dataTactics"
DEFAULT_BASEDIR = "app"
DEFAULT_STATIC_FOLDER = DEFAULT_BASEDIR + "/static"
DEFAULT_TEMPLATE_FOLDER = DEFAULT_BASEDIR + "/templates"
DEFAULT_PROFILER_FOLDER = DEFAULT_STATIC_FOLDER + "/profiles"
DEFAULT_SECWEB_PARAMS = {
    "Option": {
        "csp": {
            **inspect.signature(
                Secweb.ContentSecurityPolicy.ContentSecurityPolicyMiddleware.ContentSecurityPolicy.__init__
            )
            .parameters["Option"]
            .default
        },
        "hsts": {
            **deep_merge(
                inspect.signature(
                    Secweb.StrictTransportSecurity.StrictTransportSecurityMiddleware.HSTS.__init__
                )
                .parameters["Option"]
                .default,
                {"max-age": 63072000},
            )
        },
        "wshsts": False,
    },
    "script_nonce": True,
    "style_nonce": True,
}
DEFAULT_SECWEB_PARAMS["Option"]["csp"]["style-src"] = [
    x
    for x in DEFAULT_SECWEB_PARAMS["Option"]["csp"]["style-src"]
    if x != "'unsafe-inline'"
]
del DEFAULT_SECWEB_PARAMS["Option"]["csp"]["require-trusted-types-for"]

COOKIE_PREFIX = "COOKIE_"
COOKIE_CONFIG = {
    f"{COOKIE_PREFIX}NAME": f"{COOKIE_PREFIX.lower()}name",
    f"{COOKIE_PREFIX}MAX_AGE": f"{COOKIE_PREFIX.lower()}max_age",
    f"{COOKIE_PREFIX}PATH": f"{COOKIE_PREFIX.lower()}path",
    f"{COOKIE_PREFIX}DOMAIN": f"{COOKIE_PREFIX.lower()}domain",
    f"{COOKIE_PREFIX}SECURE": f"{COOKIE_PREFIX.lower()}secure",
    f"{COOKIE_PREFIX}HTTPONLY": f"{COOKIE_PREFIX.lower()}httponly",
    f"{COOKIE_PREFIX}SAMESITE": f"{COOKIE_PREFIX.lower()}samesite",
}
COOKIE_STRATEGY_CONFIG = {
    f"{COOKIE_PREFIX}LIFETIME_SECONDS": "lifetime_seconds",
    f"{COOKIE_PREFIX}TOKEN_AUDIENCE": "token_audience",
    f"{COOKIE_PREFIX}ALGORITHM": "algorithm",
}

BEARER_PREFIX = "BEARER_"
BEARER_CONFIG = {
    f"{BEARER_PREFIX}TOKEN_URL": "tokenUrl",
}
BEARER_STRATEGY_CONFIG = {
    f"{BEARER_PREFIX}LIFETIME_SECONDS": "lifetime_seconds",
    f"{BEARER_PREFIX}TOKEN_AUDIENCE": "token_audience",
    f"{BEARER_PREFIX}ALGORITHM": "algorithm",
}

AUTH_ROLE_PREFIX = "AUTH_"
AUTH_ROLE_CONFIG = {
    f"{AUTH_ROLE_PREFIX}ADMIN_ROLE": "admin_role",
    f"{AUTH_ROLE_PREFIX}PUBLIC_ROLE": "public_role",
}

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("DT_FASTAPI")
logger.setLevel(logging.INFO)
