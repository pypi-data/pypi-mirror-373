from typing import Callable, Literal, NotRequired, Optional, Tuple, Type, TypedDict

from fastapi import Depends, HTTPException
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
)
from fastapi_users.authentication import Authenticator as BaseAuthenticator
from fastapi_users.authentication.authenticator import EnabledBackendsDependency
from fastapi_users.models import ID, UP
from fastapi_users.password import PasswordHelperProtocol
from makefun import with_signature

from ..const import DEFAULT_COOKIE_NAME, DEFAULT_SECRET, DEFAULT_TOKEN_URL, logger
from ..db import User, UserDatabase, get_user_db
from ..manager import UserManager
from .strategies import Strategy, StrategyConfig
from .strategies.jwt import get_jwt_strategy_generator

__all__ = ["Authenticator", "AuthConfigurator"]


class CookieConfig(TypedDict):
    cookie_name: str
    cookie_max_age: NotRequired[int]
    cookie_path: NotRequired[str]
    cookie_domain: NotRequired[str]
    cookie_secure: NotRequired[bool]
    cookie_httponly: NotRequired[bool]
    cookie_samesite: NotRequired[Literal["lax", "strict", "none"]]


class BearerConfig(TypedDict):
    tokenUrl: str


class Auth(TypedDict):
    password_helper: NotRequired[PasswordHelperProtocol]
    cookie_config: NotRequired[CookieConfig]
    bearer_config: NotRequired[BearerConfig]
    cookie_strategy_config: NotRequired[StrategyConfig]
    bearer_strategy_config: NotRequired[StrategyConfig]
    secret_key: NotRequired[str]
    user_manager: NotRequired[Type[UserManager]]
    cookie_transport: NotRequired[CookieTransport]
    bearer_transport: NotRequired[BearerTransport]
    cookie_backend: NotRequired[AuthenticationBackend]
    bearer_backend: NotRequired[AuthenticationBackend]
    authenticator: NotRequired["Authenticator"]
    fastapi_users: NotRequired[FastAPIUsers[User, int]]
    strategy_backend: NotRequired[Callable[[StrategyConfig], Callable[[], Strategy]]]


class Authenticator(BaseAuthenticator):
    """
    Modified version of the default `Authenticator` class. This adds permissions to the user.

    Provides dependency callables to retrieve authenticated user.

    It performs the authentication against a list of backends
    defined by the end-developer. The first backend yielding a user wins.
    If no backend yields a user, an HTTPException is raised.

    :param backends: List of authentication backends.
    :param get_user_manager: User manager dependency callable.
    """

    def current_user(
        self,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        get_enabled_backends: Optional[EnabledBackendsDependency] = None,
        default_to_none: bool = False,
    ):
        """
        Modified version of the default `current_user` function. This adds `default_to_none` parameter.

        Return a dependency callable to retrieve currently authenticated user.

        :param optional: If `True`, `None` is returned if there is no authenticated user
        or if it doesn't pass the other requirements.
        Otherwise, throw `401 Unauthorized`. Defaults to `False`.
        Otherwise, an exception is raised. Defaults to `False`.
        :param active: If `True`, throw `401 Unauthorized` if
        the authenticated user is inactive. Defaults to `False`.
        :param verified: If `True`, throw `401 Unauthorized` if
        the authenticated user is not verified. Defaults to `False`.
        :param superuser: If `True`, throw `403 Forbidden` if
        the authenticated user is not a superuser. Defaults to `False`.
        :param get_enabled_backends: Optional dependency callable returning
        a list of enabled authentication backends.
        :param default_to_none: If `True`, return `None` if there is no authenticated user instead of raising a HTTPException.
        Useful if you want to dynamically enable some authentication backends
        based on external logic, like a configuration in database.
        By default, all specified authentication backends are enabled.
        Please not however that every backends will appear in the OpenAPI documentation,
        as FastAPI resolves it statically.
        """
        signature = self._get_dependency_signature(get_enabled_backends)

        @with_signature(signature)
        async def current_user_dependency(*args, **kwargs):
            user, _ = await self._authenticate(
                *args,
                optional=optional,
                active=active,
                verified=verified,
                superuser=superuser,
                default_to_none=default_to_none,
                **kwargs,
            )
            return user

        return current_user_dependency

    async def _authenticate(
        self,
        *args,
        user_manager: BaseUserManager[UP, ID],
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        default_to_none: bool = False,
        **kwargs,
    ) -> Tuple[UP | None, str | None]:
        user, token = None, None
        try:
            user, token = await super()._authenticate(
                *args,
                user_manager=user_manager,
                optional=optional,
                active=active,
                verified=verified,
                superuser=superuser,
                **kwargs,
            )
        except HTTPException as e:
            if not default_to_none:
                raise e

        # Retrieve list of apis, that user has access to
        if user:
            user.permissions = []
            for role in user.roles:
                for permission_api in role.permissions:
                    user.permissions.append(permission_api.api.name)
            user.permissions = list(set(user.permissions))

        return user, token


class AuthConfigurator:
    password_helper: PasswordHelperProtocol | None = None
    """
    Password helper used for password hashing. Set this to use a custom password helper.

    **Set this before any dependencies are created. Otherwise, the settings will not be applied. (E.g. set it somewhere before `fastapi_rtk.dependencies` get imported or the routes get created)**
    """

    _cookie_config: CookieConfig | None = None
    _bearer_config: BearerConfig | None = None
    _cookie_strategy_config: StrategyConfig | None = None
    _bearer_strategy_config: StrategyConfig | None = None

    _secret_key = DEFAULT_SECRET
    _is_using_default_secret_key = False
    _user_manager: Type[UserManager] | None = None
    _cookie_transport: CookieTransport | None = None
    _bearer_transport: BearerTransport | None = None
    _cookie_backend: AuthenticationBackend | None = None
    _bearer_backend: AuthenticationBackend | None = None
    _authenticator: Authenticator | None = None
    _fastapi_users: FastAPIUsers | None = None
    _strategy_backend: Callable[[StrategyConfig], Callable[[], Strategy]] | None = None

    __default_cookie_transport_class = CookieTransport
    __default_bearer_transport_class = BearerTransport
    __default_cookie_backend_class = AuthenticationBackend
    __default_bearer_backend_class = AuthenticationBackend
    __default_authenticator_class = Authenticator
    __default_fastapi_users_class = FastAPIUsers

    @property
    def secret_key(self):
        """
        Get the secret key. Default is `fastapi_rtk.const.DEFAULT_SECRET`.

        Returns:
            The secret key.

        **A WARNING will be logged if the secret key is the default value.**
        """
        if self._secret_key == DEFAULT_SECRET and not self._is_using_default_secret_key:
            self._is_using_default_secret_key = True
            logger.warning(
                "You are using the default secret key. Please change it in production."
            )
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value: str):
        """
        Set the secret key.

        Args:
            value (str): The secret key value.

        **Set this before any dependencies are created. Otherwise, the settings will not be applied. (E.g. set it somewhere before `fastapi_rtk.dependencies` get imported or the routes get created)**
        """
        self._secret_key = value

    @property
    def user_manager(self):
        """
        Get the user manager.

        if the user manager is not set, it will default to the UserManager class.

        Returns:
            The user manager.
        """
        if self._user_manager is None:
            self._user_manager = UserManager
        return self._user_manager

    @user_manager.setter
    def user_manager(self, value: Type[UserManager]):
        """
        Set the user manager.

        Use this to use a custom user manager.

        Args:
            value (Type[UserManager]): The user manager value.
        """
        self._user_manager = value

    @property
    def cookie_transport(self):
        """
        Get the cookie transport.

        if the cookie transport is not set, it will default to the cookie_transport global variable.

        Returns:
            The cookie transport.
        """
        if self._cookie_transport is None:
            self._cookie_transport = self.__default_cookie_transport_class(
                **self.cookie_config
            )
        return self._cookie_transport

    @cookie_transport.setter
    def cookie_transport(self, value: CookieTransport):
        """
        Set the cookie transport.

        Use this to use a custom cookie transport.

        Args:
            value (CookieTransport): The cookie transport value.
        """
        self._cookie_transport = value
        if value:
            self.__default_cookie_transport_class = type(value)

        # Clear dependent cookie backend
        self.cookie_backend = None

    @property
    def bearer_transport(self):
        """
        Get the bearer transport.

        if the bearer transport is not set, it will default to the bearer_transport global variable.

        Returns:
            The bearer transport.
        """
        if self._bearer_transport is None:
            self._bearer_transport = self.__default_bearer_transport_class(
                **self.bearer_config
            )
        return self._bearer_transport

    @bearer_transport.setter
    def bearer_transport(self, value: BearerTransport):
        """
        Set the bearer transport.

        Use this to use a custom bearer transport.

        Args:
            value (BearerTransport): The bearer transport value.
        """
        self._bearer_transport = value
        if value:
            self.__default_bearer_transport_class = type(value)

        # Clear dependent bearer backend
        self.bearer_backend = None

    @property
    def cookie_backend(self):
        """
        Get the cookie backend.

        if the cookie backend is not set, it will default to the cookie_backend global variable.

        Returns:
            The cookie backend.
        """
        if self._cookie_backend is None:
            self._cookie_backend = self.__default_cookie_backend_class(
                name="cookie",
                transport=self.cookie_transport,
                get_strategy=self.get_cookie_strategy(),
            )
        return self._cookie_backend

    @cookie_backend.setter
    def cookie_backend(self, value: AuthenticationBackend):
        """
        Set the cookie backend.

        Use this to use a custom cookie backend.

        Args:
            value (AuthenticationBackend): The cookie backend value.
        """
        self._cookie_backend = value
        if value:
            self.__default_cookie_backend_class = type(value)

        # Clear dependent authenticator
        self.authenticator = None

    @property
    def bearer_backend(self):
        """
        Get the bearer backend.

        if the bearer backend is not set, it will default to the bearer_backend global variable.

        Returns:
            The bearer backend.
        """
        if self._bearer_backend is None:
            self._bearer_backend = self.__default_bearer_backend_class(
                name="jwt",
                transport=self.bearer_transport,
                get_strategy=self.get_bearer_strategy(),
            )
        return self._bearer_backend

    @bearer_backend.setter
    def bearer_backend(self, value: AuthenticationBackend):
        """
        Set the bearer backend.

        Use this to use a custom bearer backend.

        Args:
            value (AuthenticationBackend): The bearer backend value.
        """
        self._bearer_backend = value
        if value:
            self.__default_bearer_backend_class = type(value)

        # Clear dependent authenticator
        self.authenticator = None

    @property
    def authenticator(self):
        """
        Get the authenticator.

        if the authenticator is not set, it will default to the authenticator global variable.

        Returns:
            The authenticator.
        """
        if self._authenticator is None:
            self._authenticator = self.__default_authenticator_class(
                [self.cookie_backend, self.bearer_backend], self.get_user_manager
            )
        return self._authenticator

    @authenticator.setter
    def authenticator(self, value: Authenticator):
        """
        Set the authenticator.

        Use this to use a custom authenticator.

        Args:
            value (Authenticator): The authenticator value.
        """
        self._authenticator = value
        if value:
            self.__default_authenticator_class = type(value)

        # Clear dependent FastAPIUsers instance
        self.fastapi_users = None

    @property
    def fastapi_users(self):
        """
        Get the FastAPIUsers instance.

        if the FastAPIUsers instance is not set, it will default to the fastapi_users global variable.

        Returns:
            The FastAPIUsers instance.
        """
        if self._fastapi_users is None:
            self._fastapi_users = self.__default_fastapi_users_class[User, int](
                self.get_user_manager, [self.cookie_backend, self.bearer_backend]
            )
            self._fastapi_users.authenticator = self.authenticator
            self._fastapi_users.current_user = self.authenticator.current_user
        return self._fastapi_users

    @fastapi_users.setter
    def fastapi_users(self, value: FastAPIUsers):
        """
        Set the FastAPIUsers instance.

        Use this to use a custom FastAPIUsers instance.

        Args:
            value (FastAPIUsers): The FastAPIUsers instance value.
        """
        self._fastapi_users = value
        if value:
            self.__default_fastapi_users_class = type(value)

    @property
    def strategy_backend(self):
        """
        Get the strategy backend generator.

        if the strategy backend generator is not set, it will default to the get_jwt_strategy_generator function.

        Returns:
            The strategy backend generator.
        """
        if self._strategy_backend is None:
            self._strategy_backend = get_jwt_strategy_generator
        return self._strategy_backend

    @strategy_backend.setter
    def strategy_backend(
        self,
        value: Callable[[StrategyConfig], Callable[[], Strategy]]
        | Literal["JWT", "DB"],
    ):
        """
        Set the strategy backend generator.

        Use this to use a custom strategy backend generator, such as where the token is stored in the database.

        Args:
            value (Callable[[StrategyConfig], Callable[[], Strategy]] | str): The strategy backend generator value or the name of the strategy generator function.
        """
        if value == "JWT":
            self._strategy_backend = get_jwt_strategy_generator
        elif value == "DB":
            from .strategies.db import get_database_strategy_generator

            self._strategy_backend = get_database_strategy_generator
        else:
            self._strategy_backend = value

    def get_user_manager(self, user_db: UserDatabase = Depends(get_user_db)):
        """
        Get the user manager as a dependency.

        Args:
            user_db: The user database.

        Returns:
            The user manager generator.
        """
        yield self.user_manager(user_db, self.secret_key, self.password_helper)

    def get_cookie_strategy(self):
        """
        Get the cookie strategy as a dependency.

        Returns:
            The cookie strategy generator.
        """
        return self.strategy_backend(
            {**self.cookie_strategy_config, "secret": self.secret_key}
        )

    def get_bearer_strategy(self):
        """
        Get the bearer strategy as a dependency.

        Returns:
            The bearer strategy generator.
        """
        return self.strategy_backend(
            {**self.bearer_strategy_config, "secret": self.secret_key}
        )

    def auth_config(self):
        """
        Generates a dictionary with keys as uppercase attribute names and values as original attribute names
        from the Auth class annotations.

        Returns:
            dict: A dictionary where each key is an uppercase attribute name from the Auth class annotations,
                  and each value is the original attribute name.
        """
        return {k.upper(): k for k in Auth.__annotations__.keys()}

    """
    -----------------------------------------
         CONFIG SETTER FUNCTIONS
    -----------------------------------------
    """

    @property
    def cookie_config(self):
        """
        Cookie configuration. Set this to use a custom cookie configuration. Or you can also set the cookie transport directly. Default is `{"cookie_name": "dataTactics"}`.

        **Set this before any dependencies are created. Otherwise, the settings will not be applied. (E.g. set it somewhere before `fastapi_rtk.dependencies` get imported or the routes get created)**
        """
        if not self._cookie_config:
            self._cookie_config = {"cookie_name": DEFAULT_COOKIE_NAME}
        return self._cookie_config

    @cookie_config.setter
    def cookie_config(self, value: CookieConfig):
        self._cookie_config = value

        # Clear dependent cookie transport
        self.cookie_transport = None

    @property
    def bearer_config(self):
        """
        Bearer configuration. Set this to use a custom bearer configuration. Or you can also set the bearer transport directly. Default is `{"tokenUrl": "/api/v1/auth/jwt/login"}`.

        **Set this before any dependencies are created. Otherwise, the settings will not be applied. (E.g. set it somewhere before `fastapi_rtk.dependencies` get imported or the routes get created)**
        """
        if not self._bearer_config:
            self._bearer_config = {"tokenUrl": DEFAULT_TOKEN_URL}
        return self._bearer_config

    @bearer_config.setter
    def bearer_config(self, value: BearerConfig):
        self._bearer_config = value

        # Clear dependent bearer transport
        self.bearer_transport = None

    @property
    def cookie_strategy_config(self):
        """
        Cookie strategy configuration. Set this to use a custom cookie strategy configuration for the Cookie backend. Default is `{"lifetime_seconds": 3600 * 24} # 1 day`.

        **Set this before any dependencies are created. Otherwise, the settings will not be applied. (E.g. set it somewhere before `fastapi_rtk.dependencies` get imported or the routes get created)**
        """
        if not self._cookie_strategy_config:
            self._cookie_strategy_config = {"lifetime_seconds": 3600 * 24}
        return self._cookie_strategy_config

    @cookie_strategy_config.setter
    def cookie_strategy_config(self, value: StrategyConfig):
        self._cookie_strategy_config = value

        # Clear dependent cookie backend
        self.cookie_backend = None

    @property
    def bearer_strategy_config(self):
        """
        Bearer strategy configuration. Set this to use a custom bearer strategy configuration for the bearer backend. Default is `{"lifetime_seconds": 3600}`.

        **Set this before any dependencies are created. Otherwise, the settings will not be applied. (E.g. set it somewhere before `fastapi_rtk.dependencies` get imported or the routes get created)**
        """
        if not self._bearer_strategy_config:
            self._bearer_strategy_config = {"lifetime_seconds": 3600}
        return self._bearer_strategy_config

    @bearer_strategy_config.setter
    def bearer_strategy_config(self, value: StrategyConfig):
        self._bearer_strategy_config = value

        # Clear dependent bearer backend
        self.bearer_backend = None
