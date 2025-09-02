import typing
from datetime import UTC, datetime
from typing import Any, Callable, Coroutine, Dict, Optional, overload

from fastapi import HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, exceptions
from fastapi_users.db import BaseUserDatabase
from fastapi_users.jwt import generate_jwt
from fastapi_users.password import PasswordHelperProtocol
from pydantic import BaseModel
from sqlalchemy import select

from .db import UserDatabase
from .exceptions import RolesMismatchException
from .schemas import (
    generate_user_create_schema,
    generate_user_update_schema,
)
from .security.sqla.models import Role, User
from .setting import Setting
from .utils import call_with_valid_kwargs, safe_call

__all__ = ["UserManager"]


class IDParser:
    def parse_id(self, value: Any) -> int:
        if isinstance(value, int):
            return value
        try:
            return int(value)
        except ValueError as e:
            raise exceptions.InvalidID() from e


class UserManager(IDParser, BaseUserManager[User, int]):
    user_db: UserDatabase[User, int]

    def __init__(
        self,
        user_db: BaseUserDatabase[User, int],
        secret_key: str,
        password_helper: PasswordHelperProtocol | None = None,
    ):
        super().__init__(user_db, password_helper)
        self.reset_password_token_secret = secret_key
        self.verification_token_secret = secret_key

    async def get_by_username(self, username: str) -> User:
        """
        Get a user by its username.

        :param username: The username of the user.
        :raises UserNotExists: The user does not exist.
        :return: A user.
        """
        user = await self.user_db.get_by_username(username)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def get_roles_by_names(
        self, roles: list[str] | str, *, raise_exception_when_mismatch=True
    ):
        """
        Get roles by their names.

        Args:
            roles (list[str] | str): A list of role names or a single role name to look up.
            raise_exception_when_mismatch (bool, optional): If True, raises `RolesMismatchException` when the number of roles found in the database does not match the number of role names provided. Defaults to True.

        Raises:
            RolesMismatchException: If raise_exception_when_mismatch is True and the expected and retrieved role counts do not match.

        Returns:
            list[Role]: A list of Role objects that match the given role names.
        """
        if isinstance(roles, str):
            roles = [roles]
        statement = select(Role).where(Role.name.in_(roles))
        result = await safe_call(self.user_db.session.scalars(statement))
        roles_from_db = list(result.all())
        if raise_exception_when_mismatch and len(roles) != len(roles_from_db):
            raise RolesMismatchException(
                f"Expected roles {roles} do not match the found roles {[r.name for r in roles_from_db]}."
            )
        return roles_from_db

    async def authenticate(self, credentials: OAuth2PasswordRequestForm) -> User | None:
        """
        Override the default authenticate method to search by username instead of email.

        Args:
            credentials (OAuth2PasswordRequestForm): The credentials to authenticate the user.

        Returns:
            User | None: The user if the credentials are valid, None otherwise.
        """
        try:
            user = await self.get_by_username(credentials.username)
        except exceptions.UserNotExists:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            await self.user_db.update(
                user, {"fail_login_count": (user.fail_login_count or 0) + 1}
            )
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        await self.user_db.update(user, {"fail_login_count": 0})
        return user

    async def create(
        self,
        user_create: BaseModel | dict[str, Any],
        roles: list[str] | str | None = None,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> User:
        """
        Modified version of the default `create` method.
        - Allows `user_create` to be a dict.
        - Adds `roles` parameter to allow specifying roles during user creation.
        - `safe` parameter is kept for compatibility but is unused.

        Create a user in database.

        Triggers the on_after_register handler on success.

        :param user_create: The UserCreate model to create. Can be a dict.
        :param roles: Optional list of roles to add to the user.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the creation, defaults to False.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserAlreadyExists: A user already exists with the same e-mail.
        :return: A new user.
        """
        if isinstance(user_create, dict):
            user_create = generate_user_create_schema(User, True)(**user_create)

        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(
            user_create.email
        ) or await self.user_db.get_by_username(user_create.username)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = user_create.model_dump(exclude_unset=True)
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        role_names = roles
        if role_names is None:
            if request:
                from .setting import Setting

                role_names = Setting.AUTH_USER_REGISTRATION_ROLE

        # Get the roles if they exist
        if role_names:
            if isinstance(role_names, str):
                role_names = [role_names]
            user_dict["roles"] = await self.get_roles_by_names(role_names)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def update(
        self,
        user_update: BaseModel | dict[str, Any],
        user: User,
        roles: list[str] | str | None = None,
        safe: bool = False,
        request: Request | None = None,
    ) -> User:
        """
        Modified version of the default `update` method.
        - Allows `user_update` to be a dict.
        - Adds `roles` parameter to allow specifying roles during user update.
        - `safe` parameter is kept for compatibility but is unused.

        Update a user.

        Triggers the on_after_update handler on success

        :param user_update: The UserUpdate model containing
        the changes to apply to the user.
        :param user: The current user to update.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the update, defaults to False
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :return: The updated user.
        """
        updated_user_data = (
            user_update.model_dump(exclude_unset=True)
            if isinstance(user_update, BaseModel)
            else generate_user_update_schema(User, True)(**user_update).model_dump(
                exclude_unset=True
            )
        )
        if roles is not None:
            if isinstance(roles, str):
                roles = [roles]
            updated_user_data["roles"] = await self.get_roles_by_names(roles)
        updated_user = await self._update(user, updated_user_data)
        await self.on_after_update(updated_user, updated_user_data, request)
        return updated_user

    async def oauth_callback(
        self,
        oauth_name: str,
        access_token: str,
        account_id: str,
        account_email: str,
        expires_at: int | None = None,
        refresh_token: str | None = None,
        request: Request | None = None,
        *,
        associate_by_email: bool = False,
        is_verified_by_default: bool = False,
        oauth_token: Optional[dict[str, Any]] = None,
        on_before_register: Optional[
            Callable[..., None] | Coroutine[None, None, None]
        ] = None,
        on_after_register: Optional[
            Callable[..., None] | Coroutine[None, None, None]
        ] = None,
        on_before_login: Optional[
            Callable[..., None] | Coroutine[None, None, None]
        ] = None,
    ) -> User:
        """
        Modified version of the default `oauth_callback` method:
        - `oauth_token` to pass the OAuth token to the callbacks.
        - `on_before_register` callback that is triggered before a new user is registered.
        - `on_after_register` callback that is triggered after a new user is registered.
        - `on_before_login` callback that is triggered after a user logs in.

        Handle the callback after a successful OAuth authentication.

        If the user already exists with this OAuth account, the token is updated.

        If a user with the same e-mail already exists and `associate_by_email` is True,
        the OAuth account is associated to this user.
        Otherwise, the `UserNotExists` exception is raised.

        If the user does not exist, it is created and the on_after_register handler
        is triggered.

        :param oauth_name: Name of the OAuth client.
        :param access_token: Valid access token for the service provider.
        :param account_id: models.ID of the user on the service provider.
        :param account_email: E-mail of the user on the service provider.
        :param expires_at: Optional timestamp at which the access token expires.
        :param refresh_token: Optional refresh token to get a
        fresh access token from the service provider.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None
        :param associate_by_email: If True, any existing user with the same
        e-mail address will be associated to this user. Defaults to False.
        :param is_verified_by_default: If True, the `is_verified` flag will be
        set to `True` on newly created user. Make sure the OAuth Provider you're
        using does verify the email address before enabling this flag.
        Defaults to False.
        :param oauth_token: Optional OAuth token from the OAuth provider.
        :param on_before_register: Optional callback to be executed before a new user is registered.
        :param on_after_register: Optional callback to be executed after a new user is registered.
        :param on_before_login: Optional callback to be executed before a user logs in.
        :return: A user.
        """
        oauth_account_dict = {
            "oauth_name": oauth_name,
            "access_token": access_token,
            "account_id": account_id,
            "account_email": account_email,
            "expires_at": expires_at,
            "refresh_token": refresh_token,
        }
        oauth_callback_params = {
            **oauth_account_dict,
            "user_dict": {},
            "oauth_token": oauth_token,
            "user_manager": self,
            "session": self.user_db.session,
        }

        try:
            user = await self.get_by_oauth_account(oauth_name, account_id)
        except exceptions.UserNotExists:
            try:
                # Associate account
                user = await self.get_by_email(account_email)
                if not associate_by_email:
                    raise exceptions.UserAlreadyExists()
                user = await self.user_db.add_oauth_account(user, oauth_account_dict)
            except exceptions.UserNotExists:
                # Create account
                password = self.password_helper.generate()
                oauth_callback_params["user_dict"] = {
                    "email": account_email,
                    "hashed_password": self.password_helper.hash(password),
                    "is_verified": is_verified_by_default,
                }

                if on_before_register:
                    result = await safe_call(
                        call_with_valid_kwargs(
                            on_before_register, oauth_callback_params
                        )
                    )
                    if result:
                        oauth_callback_params["user_dict"].update(result)
                    oauth_callback_params["user_dict"] = await self._handle_role_keys(
                        oauth_callback_params["user_dict"],
                        oauth_callback_params["user_dict"].pop("role_keys", None),
                    )
                user = await self.user_db.create(oauth_callback_params["user_dict"])
                user = await self.user_db.add_oauth_account(user, oauth_account_dict)
                oauth_callback_params["user"] = user
                if on_after_register:
                    result = await safe_call(
                        call_with_valid_kwargs(on_after_register, oauth_callback_params)
                    )
                    if result:
                        oauth_callback_params["user_dict"].update(result)
                    user = await self._handle_role_keys(
                        user, oauth_callback_params["user_dict"].pop("role_keys", None)
                    )
                await self.on_after_register(user, request)
        else:
            # Update oauth
            for existing_oauth_account in user.oauth_accounts:
                if (
                    existing_oauth_account.account_id == account_id
                    and existing_oauth_account.oauth_name == oauth_name
                ):
                    user = await self.user_db.update_oauth_account(
                        user, existing_oauth_account, oauth_account_dict
                    )

        if on_before_login:
            oauth_callback_params["user"] = user
            result = await safe_call(
                call_with_valid_kwargs(on_before_login, oauth_callback_params)
            )
            if result:
                oauth_callback_params["user_dict"].update(result)
            user = await self._handle_role_keys(
                user, oauth_callback_params["user_dict"].pop("role_keys", None)
            )
        return user

    @overload
    async def forgot_password(self, user: User, request: Request) -> None: ...
    @overload
    async def forgot_password(
        self, user: User, request: Optional[Request] = None
    ) -> str: ...
    async def forgot_password(self, user: User, request: Optional[Request] = None):
        """
        Modified version of the default `forgot_password` method to return the token when it is not in a request context.

        Start a forgot password request.

        Triggers the on_after_forgot_password handler on success.

        :param user: The user that forgot its password.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserInactive: The user is inactive.
        """
        if not user.is_active:
            raise exceptions.UserInactive()

        token_data = {
            "sub": str(user.id),
            "password_fgpt": self.password_helper.hash(user.hashed_password),
            "aud": self.reset_password_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.reset_password_token_secret,
            self.reset_password_token_lifetime_seconds,
        )
        await self.on_after_forgot_password(user, token, request)

        if not request:
            return token

    async def on_after_login(
        self,
        user: User,
        request: Request | None = None,
        response: Response | None = None,
    ) -> None:
        """
        Perform logic after user login.

        Please call await super().on_after_login(user, request, response) to keep the default behavior.

        *You should overload this method to add your own logic.*

        :param user: The user that is logging in
        :param request: Optional FastAPI request
        :param response: Optional response built by the transport.
        Defaults to None
        """
        update_fields = {
            "last_login": datetime.now(UTC).replace(tzinfo=None),
            "login_count": (user.login_count or 0) + 1,
        }
        await self.user_db.update(user, update_fields)

    async def on_after_logout(
        self,
        user: User,
        request: Request | None = None,
        response: Response | None = None,
    ) -> None:
        """
        Custom `on_after_logout` method to handle user logout.

        Perform logic after user logout.

        *You should overload this method to add your own logic.*

        :param user: The user that is logging out
        :param request: Optional FastAPI request
        :param response: Optional response built by the transport.
        Defaults to None
        """
        return

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        if request:
            raise HTTPException(status_code=501, detail="Not implemented")

    async def on_after_reset_password(
        self, user: User, request: Request | None = None
    ) -> None:
        if request:
            raise HTTPException(status_code=501, detail="Not implemented")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        if request:
            raise HTTPException(status_code=501, detail="Not implemented")

    async def _update(self, user: User, update_dict: Dict[str, Any]) -> User:
        """
        Modified version of the default `_update` method to also check for existing users with the same username.
        """
        validated_update_dict = {}
        for field, value in update_dict.items():
            if field == "email" and value != user.email:
                try:
                    await self.get_by_email(value)
                    raise exceptions.UserAlreadyExists()
                except exceptions.UserNotExists:
                    validated_update_dict["email"] = value
                    validated_update_dict["is_verified"] = False
            elif field == "username" and value != user.username:
                try:
                    await self.get_by_username(value)
                    raise exceptions.UserAlreadyExists()
                except exceptions.UserNotExists:
                    validated_update_dict["username"] = value
            elif field == "password" and value is not None:
                await self.validate_password(value, user)
                validated_update_dict["hashed_password"] = self.password_helper.hash(
                    value
                )
            else:
                validated_update_dict[field] = value
        return await self.user_db.update(user, validated_update_dict)

    @typing.overload
    async def _handle_role_keys(
        self, user_or_user_dict: User, role_keys: list[str] | None = None
    ) -> User: ...
    @typing.overload
    async def _handle_role_keys(
        self, user_or_user_dict: dict[str, Any], role_keys: list[str] | None = None
    ) -> dict[str, Any]: ...
    async def _handle_role_keys(
        self,
        user_or_user_dict: User | dict[str, Any],
        role_keys: list[str] | None = None,
    ):
        """
        Handle the role keys for a user or user dictionary.

        This method retrieves the roles based on the provided role keys and updates
        the user or user dictionary with the corresponding roles.

        Args:
            user_or_user_dict (User | dict[str, Any]): The user or user dictionary to update.
            role_keys (list[str] | None, optional): The role keys to retrieve roles for.

        Returns:
            User | dict[str, Any]: The updated user or user dictionary with roles.
        """
        if not role_keys:
            return user_or_user_dict
        role_names = [Setting.AUTH_ROLES_MAPPING.get(key, []) for key in role_keys]
        role_names = [name for sublist in role_names for name in sublist]
        role_names = list(dict.fromkeys(role_names).keys())
        if not role_names:
            return user_or_user_dict
        if isinstance(user_or_user_dict, User):
            user_or_user_dict = await self.update({}, user_or_user_dict, role_names)
        else:
            user_or_user_dict["roles"] = await self.get_roles_by_names(role_names)
        return user_or_user_dict
