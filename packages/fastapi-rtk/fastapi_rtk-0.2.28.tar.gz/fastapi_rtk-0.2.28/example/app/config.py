import os
from typing import Any, Dict, cast

from fastapi_rtk.security.sqla.models import User
from httpx_oauth.clients.google import PROFILE_ENDPOINT, GoogleOAuth2
from httpx_oauth.exceptions import HTTPXOAuthError

basedir = os.path.abspath(os.path.dirname(__file__))

# Your App secret key
SECRET_KEY = "hf45hf8578h5n487hv487h474584"

UPLOAD_FOLDER = os.path.join("./", "uploads")
IMG_UPLOAD_FOLDER = os.path.join("./", "img_uploads")

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = "sqlite+aiosqlite:///" + os.path.join(basedir, "app.db")
SQLALCHEMY_BINDS = {
    "assets": "sqlite:///" + os.path.join(basedir, "assets.db"),
}
# SQLALCHEMY_DATABASE_URI = (
#     "postgresql+asyncpg://fastapi_rtk:fastapi_rtk@localhost:5433/fastapi_rtk"
# )
# SQLALCHEMY_BINDS = {
#     "assets": "postgresql+asyncpg://fastapi_rtk:fastapi_rtk@localhost:5433/fastapi_rtk_assets"
# }
# SQLALCHEMY_DATABASE_URI = 'mysql://myapp@localhost/myapp'
# SQLALCHEMY_DATABASE_URI = 'postgresql://root:password@localhost/myapp'

google_oauth_client = GoogleOAuth2(
    "client_id",
    "client_secret",
)


async def on_after_register_google(user: User, access_token: str):
    async with google_oauth_client.get_httpx_client() as client:
        response = await client.get(
            PROFILE_ENDPOINT,
            params={"personFields": "names"},
            headers={
                **google_oauth_client.request_headers,
                "Authorization": f"Bearer {access_token}",
            },
        )

        if response.status_code >= 400:
            raise HTTPXOAuthError(response.json())

        data = cast(Dict[str, Any], response.json())
        names = data.get("names", [])

        if names:
            user.first_name = names[0].get("givenName")
            user.last_name = names[0].get("familyName")


OAUTH_PROVIDERS = [
    {
        "oauth_client": google_oauth_client,
        "on_after_register": on_after_register_google,
    }
]
OAUTH_REDIRECT_URI = "http://localhost:6006"

# General roles, that everyone should be able to read
GENERAL_READ = [
    "AssetApi|UnitApi",
    "can_info|can_get",
]

FAB_ROLES = {
    "Operator": [GENERAL_READ],
    "Reporter": [GENERAL_READ],
}
