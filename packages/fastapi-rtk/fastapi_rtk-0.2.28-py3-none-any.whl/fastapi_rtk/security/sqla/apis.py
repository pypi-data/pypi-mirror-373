from typing import List

from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ...api import BaseApi, ModelRestApi
from ...backends.sqla.interface import SQLAInterface
from ...db import UserDatabase, get_user_db
from ...decorators import expose, login_required
from ...globals import g
from ...routers import get_auth_router, get_oauth_router
from ...schemas import (
    GeneralResponse,
    InfoResponse,
    generate_user_create_schema,
    generate_user_get_schema,
    generate_user_update_schema,
)
from ...setting import Setting
from ...utils import SelfType, lazy, merge_schema
from .models import Api, Permission, PermissionApi, Role, User

__all__ = [
    "AuthApi",
    "InfoApi",
    "PermissionsApi",
    "PermissionViewApi",
    "RolesApi",
    "UsersApi",
    "ViewsMenusApi",
]


class PermissionViewApi(ModelRestApi):
    resource_name = "permissionview"
    datamodel = SQLAInterface(PermissionApi)
    description = "Allows the view of which roles have which permissions on which APIs."
    max_page_size = 200
    base_permissions = ["can_get", "can_info"]


class ViewsMenusApi(ModelRestApi):
    resource_name = "viewsmenus"
    description = "Allows the view of the permissions of an API."
    datamodel = SQLAInterface(Api)
    max_page_size = 200
    base_permissions = ["can_get", "can_info"]


class PermissionsApi(ModelRestApi):
    resource_name = "permissions"
    description = (
        "Allows the view of the permissions and which APIs they are assigned to."
    )
    datamodel = SQLAInterface(Permission)
    max_page_size = 200
    base_permissions = ["can_get", "can_info"]


class RolesApi(ModelRestApi):
    resource_name = "roles"
    description = "Allows the management of roles, their permissions, and the users assigned to them."
    datamodel = SQLAInterface(Role)
    max_page_size = 200
    extra_list_fetch_columns = ["users.roles"]
    extra_show_fetch_columns = ["users.roles"]


class InfoApi(BaseApi):
    resource_name = "info"
    description = "Provides information about the exposed APIs and their permissions."

    security_level_apis = [
        "PermissionsApi",
        "RolesApi",
        "UsersApi",
        "ViewsMenusApi",
        "PermissionViewApi",
    ]
    excluded_apis = ["InfoApi", "AuthApi"]

    def __init__(self):
        expose("/")(self.get_info)
        login_required(self.get_info)
        super().__init__()

    def get_info(self):
        if not self.toolkit:
            return []

        apis = self.cache.get("get_info", [])
        if apis:
            return apis

        for api in self.toolkit.apis:
            if api.__class__.__name__ in self.excluded_apis:
                continue

            api_info = {}
            api_info["name"] = api.resource_name.capitalize()
            api_info["icon"] = "Table" if hasattr(api, "datamodel") else ""
            api_info["permission_name"] = api.__class__.__name__
            api_info["path"] = api.resource_name
            api_info["type"] = "table" if hasattr(api, "datamodel") else "default"
            api_info["level"] = (
                "security"
                if api.__class__.__name__ in self.security_level_apis
                else "default"
            )
            apis.append(api_info)

        self.cache["get_info"] = apis
        return apis


class UsersApi(ModelRestApi):
    resource_name = "users"
    description = "Allows the management of users and their roles."
    datamodel = SQLAInterface(User)
    list_exclude_columns = ["password", "hashed_password", "oauth_accounts"]
    show_exclude_columns = ["password", "hashed_password", "oauth_accounts"]
    search_exclude_columns = ["password", "hashed_password", "oauth_accounts"]
    add_exclude_columns = [
        "active",
        "last_login",
        "login_count",
        "fail_login_count",
        "created_on",
        "changed_on",
        "oauth_accounts",
    ]
    edit_exclude_columns = [
        "username",
        "last_login",
        "login_count",
        "fail_login_count",
        "created_on",
        "changed_on",
        "oauth_accounts",
    ]
    label_columns = {"password": "Password"}

    def post_schema(self):
        self.add_schema = merge_schema(self.add_schema, {"email": (EmailStr, Field())})
        self.edit_schema = merge_schema(
            self.edit_schema,
            {"email": (EmailStr | None, Field(None))},
            only_update=True,
        )

    def pre_info(
        self,
        info: InfoResponse,
        permissions: List[str],
        session: AsyncSession | Session,
    ):
        for col in info.edit_columns:
            if col.name == "password":
                col.required = False

    async def post_add(self, item, params):
        await g.current_app.security.update_user(
            user_update={"password": item.password},
            user=item,
            session=params.session,
        )
        await self.datamodel.add(params.session, item)

    async def post_update(self, item, params):
        if params.body.password:
            await g.current_app.security.update_user(
                user_update={"password": params.body.password},
                user=item,
                session=params.session,
            )
        await self.datamodel.add(params.session, item)


class AuthApi(BaseApi):
    resource_name = "auth"
    description = "Provides authentication and authorization for the application."
    datamodel = SQLAInterface(User)
    get_user_schema = lazy(lambda: generate_user_get_schema(User))
    update_user_schema = lazy(lambda: generate_user_update_schema(User, True))

    def __init__(self):
        self._init_routes()
        super().__init__()
        if Setting.AUTH_LOGIN_COOKIE:
            self.router.include_router(
                get_auth_router(
                    g.auth.cookie_backend,
                    g.auth.fastapi_users.get_user_manager,
                    g.auth.fastapi_users.authenticator,
                )
            )
        if Setting.AUTH_LOGIN_JWT:
            self.router.include_router(
                get_auth_router(
                    g.auth.bearer_backend,
                    g.auth.fastapi_users.get_user_manager,
                    g.auth.fastapi_users.authenticator,
                ),
                prefix="/jwt",
            )
        if Setting.AUTH_USER_REGISTRATION:
            self.router.include_router(
                g.auth.fastapi_users.get_register_router(
                    generate_user_get_schema(User),
                    generate_user_create_schema(User, True),
                ),
            )
        if Setting.AUTH_USER_RESET_PASSWORD:
            self.router.include_router(
                g.auth.fastapi_users.get_reset_password_router(),
            )
        if Setting.AUTH_USER_VERIFY:
            self.router.include_router(
                g.auth.fastapi_users.get_verify_router(generate_user_get_schema(User)),
            )

        oauth_clients = Setting.OAUTH_CLIENTS
        for client in oauth_clients:
            oauth_client = client["oauth_client"]
            associate_by_email = client.get("associate_by_email", False)
            on_before_register = client.get("on_before_register", None)
            on_after_register = client.get("on_after_register", None)
            on_before_login = client.get("on_before_login", None)

            self.router.include_router(
                get_oauth_router(
                    oauth_client=oauth_client,
                    backend=g.auth.cookie_backend,
                    get_user_manager=g.auth.fastapi_users.get_user_manager,
                    state_secret=g.auth.secret_key,
                    redirect_url=Setting.OAUTH_REDIRECT_URI,
                    associate_by_email=associate_by_email,
                    on_before_register=on_before_register,
                    on_after_register=on_after_register,
                    on_before_login=on_before_login,
                ),
            )

    def _init_routes(self):
        expose(
            "/user",
            methods=["GET"],
            response_model=self.get_user_schema,
            responses={
                status.HTTP_401_UNAUTHORIZED: {
                    "description": "Missing token or inactive user.",
                }
            },
        )(self.get_user)
        expose(
            "/user",
            methods=["PUT"],
            responses={
                status.HTTP_401_UNAUTHORIZED: {
                    "description": "Missing token or inactive user.",
                }
            },
        )(self.update_user)

    def get_user(self):
        if not g.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing token or inactive user.",
            )
        return g.user

    async def update_user(
        self,
        request: Request,
        user_update: BaseModel = SelfType().update_user_schema,
        user_db: UserDatabase = Depends(get_user_db),
    ):
        if not g.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing token or inactive user.",
            )
        user_manager = next(g.auth.get_user_manager(user_db))
        await user_manager.update(user_update, g.user, safe=True, request=request)
        return GeneralResponse(detail="User updated successfully.")
