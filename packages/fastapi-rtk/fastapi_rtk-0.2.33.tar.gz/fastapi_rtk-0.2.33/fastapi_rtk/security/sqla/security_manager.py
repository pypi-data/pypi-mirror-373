import json
import typing
from datetime import datetime

import fastapi_users.exceptions
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ...const import logger
from ...globals import g
from ...setting import Setting
from ...utils import merge_schema, safe_call
from .models import Api, Permission, PermissionApi, Role, User

__all__ = ["SecurityManager"]

from ...db import UserDatabase, db

if typing.TYPE_CHECKING:
    from ...fastapi_react_toolkit import FastAPIReactToolkit


class SecurityManager:
    """
    The SecurityManager class provides functions to manage users, roles, permissions, and APIs.
    """

    toolkit: typing.Optional["FastAPIReactToolkit"]

    def __init__(self, toolkit: typing.Optional["FastAPIReactToolkit"] = None) -> None:
        self.toolkit = toolkit

    """
    -----------------------------------------
         USER MANAGER FUNCTIONS
    -----------------------------------------
    """

    async def get_user(
        self,
        email_or_username: str,
        *,
        session: AsyncSession | Session = None,
    ):
        """
        Gets the user with the specified email or username.

        Args:
            email_or_username (str): The email or username of the user.
            session (AsyncSession | Session, optional): The database session to use. If not given, a new session will be created. Defaults to None.

        Returns:
            User | None: The user object if found, else None.
        """
        try:
            if not session:
                async with db.session() as session:
                    return await self.get_user(email_or_username, session=session)

            manager = next(g.auth.get_user_manager(UserDatabase(session, User)))
            try:
                return await manager.get_by_email(email_or_username)
            except fastapi_users.exceptions.UserNotExists:
                return await manager.get_by_username(email_or_username)
        except fastapi_users.exceptions.UserNotExists:
            return None

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        roles: list[str] | str | None = None,
        *,
        session: AsyncSession | Session = None,
        raise_exception: bool | typing.Literal["user_exists"] = True,
        **kwargs,
    ):
        """
        Creates a new user with the given information.

        Args:
            username (str): The username of the user.
            email (str): The email address of the user.
            password (str): The password of the user.
            first_name (str, optional): The first name of the user. Defaults to "".
            last_name (str, optional): The last name of the user. Defaults to "".
            roles (list[str] | str | None, optional): The roles assigned to the user. Defaults to None.
            session (AsyncSession | Session, optional): The database session to use. If not given, a new session will be created. Defaults to None.
            raise_exception (bool | Literal["user_exists"], optional): When set to True, raises an exception if an error occurs, otherwise returns None. If set to `user_exists`, raises an exception if the user with the given email or username already exists. Defaults to True.
            **kwargs: Additional keyword arguments to be given to the user manager.

        Returns:
            User | None: The created user object if successful, else None.

        Raises:
            SomeException: Description of the exception raised, if any.
        """

        try:
            if not session:
                async with db.session() as session:
                    return await self.create_user(
                        username,
                        email,
                        password,
                        first_name,
                        last_name,
                        roles,
                        session=session,
                        raise_exception=raise_exception,
                        **kwargs,
                    )

            manager = next(g.auth.get_user_manager(UserDatabase(session, User)))
            return await manager.create(
                {
                    "email": email,
                    "username": username,
                    "password": password,
                    "first_name": first_name,
                    "last_name": last_name,
                    **kwargs,
                },
                roles,
            )
        except Exception as e:
            if not raise_exception:
                return
            if raise_exception == "user_exists":
                if isinstance(e, fastapi_users.exceptions.UserAlreadyExists):
                    raise e
            else:
                raise e

    async def update_user(
        self,
        user_update: BaseModel | dict[str, typing.Any],
        user: User,
        roles: list[str] | str | None = None,
        *,
        session: AsyncSession | Session = None,
        raise_exception: bool | typing.Literal["user_exists"] = True,
    ):
        """
        Updates the specified user with the given information.

        Args:
            update_dict (UserUpdate, dict[str, typing.Any]): The information to update.
            user (User): The user to update.
            roles (list[str] | str | None, optional): The roles to assign to the user. Defaults to None.
            session (AsyncSession | Session, optional): The database session to use. If not given, a new session will be created. Defaults to None.
            raise_exception (bool | Literal["user_exists"], optional): When set to True, raises an exception if an error occurs, otherwise returns None. If set to `user_exists`, raises an exception if the user with the given email or username already exists. Defaults to True.

        Returns:
            User | None: The updated user object if successful, else None.

        Raises:
            SomeException: Description of the exception raised, if any.
        """
        try:
            if not session:
                async with db.session() as session:
                    return await self.update_user(
                        user_update,
                        user,
                        roles,
                        session=session,
                        raise_exception=raise_exception,
                    )

            manager = next(g.auth.get_user_manager(UserDatabase(session, User)))
            return await manager.update(user_update, user, roles)
        except Exception as e:
            if not raise_exception:
                return
            if raise_exception == "user_exists":
                if isinstance(e, fastapi_users.exceptions.UserAlreadyExists):
                    raise e
            else:
                raise e

    async def get_roles(
        self,
        roles: list[str] | str,
        *,
        session: AsyncSession | Session = None,
        raise_exception: bool | typing.Literal["roles_mismatch"] = True,
    ):
        """
        Retrieves the roles with the specified names.

        Args:
            roles (list[str] | str): The names of the roles to retrieve.
            session (AsyncSession | Session, optional): The database session to use. If not given, a new session will be created. Defaults to None.
            raise_exception (bool | Literal['roles_mismatch'], optional): When set to True, raises an exception if an error occurs, otherwise returns None. If set to `roles_mismatch`, raises an exception only when the roles do not match the expected roles. Defaults to True.


        Returns:
            list[Role] | None: The list of role objects if found, else None.

        Raises:
            SomeException: Description of the exception raised, if any.
        """
        try:
            if not session:
                async with db.session() as session:
                    return await self.get_roles(
                        roles, session=session, raise_exception=raise_exception
                    )

            manager = next(g.auth.get_user_manager(UserDatabase(session, User)))
            return await manager.get_roles_by_names(
                roles,
                raise_exception_when_mismatch=raise_exception is True
                or raise_exception == "roles_mismatch",
            )
        except Exception as e:
            if not raise_exception:
                return
            raise e

    async def create_role(
        self,
        name: str,
        *,
        session: AsyncSession | Session = None,
        raise_exception: bool = True,
    ):
        """
        Creates a new role with the given name.

        Args:
            name (str): The name of the role to create.
            session (AsyncSession | Session, optional): The database session to use. If not given, a new session will be created. Defaults to None.
            raise_exception (bool, optional): When set to True, raises an exception if an error occurs, otherwise returns None. Defaults to True.

        Returns:
            Role | None: The created role object if successful, else None.

        Raises:
            SomeException: Description of the exception raised, if any.
        """
        try:
            if not session:
                async with db.session() as session:
                    return await self.create_role(
                        name, session=session, raise_exception=raise_exception
                    )

            role = Role(name=name)
            session.add(role)
            await safe_call(session.commit())
            return role
        except Exception as e:
            if not raise_exception:
                return
            raise e

    async def reset_password(
        self,
        user: User,
        new_password: str,
        *,
        session: AsyncSession | Session = None,
        raise_exception: bool | typing.Literal["user_inactive"] = True,
    ):
        """
        Resets the password of the specified user.

        Args:
            user (User): The user whose password is to be reset.
            new_password (str): The new password to set.
            session (AsyncSession | Session, optional): The database session to use. If not given, a new session will be created. Defaults to None.
            raise_exception (bool | Literal["user_inactive"], optional): When set to True, raises an exception if an error occurs, otherwise returns None. If set to `user_inactive`, raises an exception if the user is inactive. Defaults to True.

        Returns:
            User | None: The user object with the updated password if successful, else None.

        Raises:
            SomeException: Description of the exception raised, if any.
        """
        try:
            if not session:
                async with db.session() as session:
                    return await self.reset_password(
                        user,
                        new_password,
                        session=session,
                        raise_exception=raise_exception,
                    )

            manager = next(g.auth.get_user_manager(UserDatabase(session, User)))
            token = await manager.forgot_password(user)
            return await manager.reset_password(token, new_password)
        except Exception as e:
            if not raise_exception:
                return
            if raise_exception == "user_inactive":
                if isinstance(e, fastapi_users.exceptions.UserInactive):
                    raise e
            else:
                raise e

    async def export_data(
        self,
        data: typing.Literal["users", "roles"],
        type: typing.Literal["json", "csv"] = "json",
        *,
        session: AsyncSession | Session = None,
    ):
        """
        Exports the specified data to a file.

        Args:
            data (typing.Literal["users", "roles"]): The data to export (users or roles).
            type (typing.Literal["json", "csv"], optional): The type of file to export the data to. Defaults to "json".
            session (AsyncSession | Session, optional): The database session to use. If not given, a new session will be created. Defaults to None.

        Returns:
            str: The exported data in JSON or CSV format.

        Raises:
            SomeException: Description of the exception raised, if any.
        """
        if not session:
            async with db.session() as session:
                return await self.export_data(data, type, session=session)

        match data:
            case "users":
                from ...schemas import generate_user_get_schema

                user_schema = generate_user_get_schema(User)
                user_schema = merge_schema(
                    user_schema, {"password": (str, Field())}, name="ExportUserSchema"
                )
                stmt = select(User)
                users = await safe_call(session.scalars(stmt))
                user_dict = {}
                for user in users:
                    validated_user = user_schema.model_validate(user)
                    validated_dict = validated_user.model_dump()
                    for key, value in validated_dict.items():
                        if isinstance(value, datetime):
                            validated_dict[key] = value.isoformat()
                    user_dict[user.username] = validated_dict
                if type == "json":
                    return json.dumps(user_dict, indent=4)

                csv_data = "Username,Data\n"
                for username, data in user_dict.items():
                    csv_data += f"{username},{data}\n"
                return csv_data
            case "roles":
                from ...backends.sqla.interface import SQLAInterface

                role_schema = SQLAInterface(Role).generate_schema(
                    ["id", "name"],
                    with_id=False,
                    with_name=False,
                    name="ExportRoleSchema",
                )
                stmt = select(Role)
                roles = await safe_call(session.scalars(stmt))
                role_dict = {}
                for role in roles:
                    # TODO: Change result
                    role_dict[role.name] = role_schema.model_validate(role).model_dump()
                if type == "json":
                    return json.dumps(role_dict, indent=4)

                csv_data = "Role,Data\n"
                for role, data in role_dict.items():
                    csv_data += f"{role},{','.join(data)}\n"
                return csv_data

    """
    -----------------------------------------
         SECURITY FUNCTIONS
    -----------------------------------------
    """

    async def cleanup(self, *, session: AsyncSession | Session = None):
        """
        Cleanup unused permissions from apis and roles.

        Args:
            session (AsyncSession | Session, optional): The database session to use. If not given, a new session will be created. Defaults to None.

        Raises:
            Exception: If the FastAPIReactToolkit instance is not provided.
        """
        if not session:
            async with db.session() as session:
                await self.cleanup(session=session)

        if not self.toolkit:
            raise Exception(
                "FastAPIReactToolkit instance not provided, you must provide it to use this function."
            )

        api_permission_tuples = (Setting.ROLES).values()
        apis = [api.__class__.__name__ for api in self.toolkit.apis]
        permissions = self.toolkit.total_permissions()
        for api_permission_tuple in api_permission_tuples:
            for api, permission in api_permission_tuple:
                apis.append(api)
                permissions.append(permission)

        # Clean up unused permissions
        unused_permissions = await safe_call(
            session.scalars(select(Permission).where(~Permission.name.in_(permissions)))
        )
        for permission in unused_permissions:
            logger.info(f"DELETING PERMISSION {permission} AND ITS ASSOCIATIONS")
            await safe_call(session.delete(permission))

        # Clean up unused apis
        unused_apis = await safe_call(
            session.scalars(select(Api).where(~Api.name.in_(apis)))
        )
        for api in unused_apis:
            logger.info(f"DELETING API {api} AND ITS ASSOCIATIONS")
            await safe_call(session.delete(api))

        roles = Setting.ROLES.keys()
        roles = list(roles) + [g.admin_role]

        # Clean up existing permission-apis, that are no longer connected to any roles
        unused_permission_apis = await safe_call(session.scalars(select(PermissionApi)))
        for permission_api in unused_permission_apis:
            for role in list(permission_api.roles) or []:
                if role.name not in roles:
                    permission_api.roles.remove(role)
                    logger.info(
                        f"DISASSOCIATING ROLE {role} FROM PERMISSION API {permission_api}"
                    )

        await safe_call(session.commit())
