import typing

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import models, schemas
from fastapi_users.authentication import AuthenticationBackend, Authenticator, Strategy
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users.jwt import SecretType, decode_jwt
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel
from fastapi_users.router.oauth import STATE_TOKEN_AUDIENCE, generate_state_token
from httpx_oauth.integrations.fastapi import (
    OAuth2AuthorizeCallback as BaseOAuth2AuthorizeCallback,
)
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallbackError
from httpx_oauth.oauth2 import BaseOAuth2, OAuth2Token

from .globals import g
from .utils import smart_run

__all__ = ["get_oauth_router", "get_oauth_associate_router", "get_auth_router"]

HTML_SUCCESS_RESPONSE = """
<html>
    <body>
        <h1>You have successfully logged in!</h1>
        <script>
            window.onload = function() {
                window.close();
            }
        </script>
    </body>
</html>
"""


class OAuth2AuthorizeCallback(BaseOAuth2AuthorizeCallback):
    """
    Modified version of the `OAuth2AuthorizeCallback` from `httpx_oauth.integrations.fastapi`.
    - Adds `state_secret` parameter to support for decoding `state` JWT to get `redirect_url`.
    """

    state_secret: SecretType | None

    def __init__(
        self,
        client,
        route_name=None,
        redirect_url=None,
        state_secret: SecretType | None = None,
    ):
        self.state_secret = state_secret
        # Use `redirect_url` from `state`
        if self.state_secret:
            route_name = None
            redirect_url = ""
        super().__init__(client, route_name, redirect_url)

    async def __call__(
        self, request, code=None, code_verifier=None, state=None, error=None
    ):
        original_redirect_url = self.redirect_url
        if self.state_secret:
            # Try to decode JWT
            try:
                state_data = decode_jwt(
                    state, self.state_secret, [STATE_TOKEN_AUDIENCE]
                )
                request.state.state_data = state_data
                self.redirect_url = state_data.get(
                    "redirect_url", original_redirect_url
                )
            except jwt.PyJWTError:
                raise OAuth2AuthorizeCallbackError(
                    status.HTTP_400_BAD_REQUEST,
                    "Invalid state token",
                )

        try:
            return await super().__call__(request, code, code_verifier, state, error)
        finally:
            self.redirect_url = original_redirect_url


def get_oauth_router(
    oauth_client: BaseOAuth2,
    backend: AuthenticationBackend[models.UP, models.ID],
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    state_secret: SecretType,
    redirect_url: typing.Optional[str] = None,
    redirect_url_factory: typing.Optional[
        typing.Callable[[Request, list[str]], str]
    ] = None,
    redirect_url_after_callback: typing.Optional[str] = None,
    associate_by_email: bool = False,
    is_verified_by_default: bool = False,
    **kwargs: dict[str, typing.Any],
) -> APIRouter:
    """
    Modified version of the `get_oauth_router` from `fastapi_users.router.oauth`.
    - Updates the `login` to redirect to `authorization_url` directly instead of returning a JSONResponse with key `authorization_url`.
    - Adds `redirect_url_factory` to allow dynamic generation of the redirect URL.
    - Adds `redirect_url_after_callback` to redirect user to the application after OAuth callback.
    - Adds `**kwargs` to provide additional arguments for the user manager's `oauth_callback` method.

    Generate a router with the OAuth routes.
    """
    router = APIRouter()
    callback_route_name = f"oauth:{oauth_client.name}.{backend.name}.callback"

    if redirect_url is not None:
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            oauth_client,
            redirect_url=redirect_url,
        )
    elif redirect_url_factory is not None:
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            oauth_client,
            state_secret=state_secret,
        )
    else:
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            oauth_client,
            route_name=callback_route_name,
        )

    @router.get(
        f"/login/{oauth_client.name}",
        name=f"oauth:{oauth_client.name}.{backend.name}.authorize",
    )
    async def authorize(request: Request, scopes: list[str] = Query(None)):
        if redirect_url is not None:
            authorize_redirect_url = redirect_url
        elif redirect_url_factory is not None:
            authorize_redirect_url = await smart_run(
                redirect_url_factory, request, scopes
            )
        else:
            authorize_redirect_url = str(request.url_for(callback_route_name))

        state_data = dict[str, str]()
        if redirect_url_factory:
            state_data["redirect_url"] = authorize_redirect_url
        if (
            request.query_params.get("popup") == "1"
            or request.query_params.get("popup") == "true"
        ):
            state_data["popup"] = "true"
        state = generate_state_token(state_data, state_secret)
        authorization_url = await oauth_client.get_authorization_url(
            authorize_redirect_url,
            state,
            scopes,
        )

        return RedirectResponse(authorization_url)

    @router.get(
        f"/oauth-authorized/{oauth_client.name}",
        name=callback_route_name,
        description="The response varies based on the authentication backend used.",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            "INVALID_STATE_TOKEN": {
                                "summary": "Invalid state token.",
                                "value": None,
                            },
                            ErrorCode.LOGIN_BAD_CREDENTIALS: {
                                "summary": "User is inactive.",
                                "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                            },
                        }
                    }
                },
            },
        },
    )
    async def callback(
        request: Request,
        access_token_state: tuple[OAuth2Token, str] = Depends(
            oauth2_authorize_callback
        ),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        token, state = access_token_state
        account_id, account_email = await oauth_client.get_id_email(
            token["access_token"]
        )

        if account_email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.OAUTH_NOT_AVAILABLE_EMAIL,
            )

        # Try to use existing state data from request.state
        state_data = getattr(request.state, "state_data", None)
        if state_data is None:
            try:
                state_data = decode_jwt(state, state_secret, [STATE_TOKEN_AUDIENCE])
            except jwt.DecodeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        try:
            user = await user_manager.oauth_callback(
                oauth_client.name,
                token["access_token"],
                account_id,
                account_email,
                token.get("expires_at"),
                token.get("refresh_token"),
                request,
                associate_by_email=associate_by_email,
                is_verified_by_default=is_verified_by_default,
                oauth_token=token,
                **kwargs,
            )
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.OAUTH_USER_ALREADY_EXISTS,
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )

        # Authenticate
        response = await backend.login(strategy, user)
        await user_manager.on_after_login(user, request, response)

        # Check if the request is from a popup
        if state_data.get("popup") == "true":
            return HTMLResponse(
                content=HTML_SUCCESS_RESPONSE,
                headers=response.headers,
            )

        if redirect_url_after_callback:
            return RedirectResponse(
                redirect_url_after_callback, headers=response.headers
            )

        return response

    return router


def get_oauth_associate_router(
    oauth_client: BaseOAuth2,
    authenticator: Authenticator[models.UP, models.ID],
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    user_schema: type[schemas.U],
    state_secret: SecretType,
    redirect_url: typing.Optional[str] = None,
    redirect_url_factory: typing.Optional[
        typing.Callable[[Request, list[str]], str]
    ] = None,
    redirect_url_after_callback: typing.Optional[str] = None,
    requires_verification: bool = False,
) -> APIRouter:
    """
    Modified version of the `get_oauth_associate_router` from `fastapi_users.router.oauth`.
    - Updates the `login` to redirect to `authorization_url` directly instead of returning a JSONResponse with key `authorization_url`.
    - Adds `redirect_url_factory` to allow dynamic generation of the redirect URL.
    - Adds `redirect_url_after_callback` to redirect user to the application after OAuth callback.

    Generate a router with the OAuth routes to associate an authenticated user.
    """
    router = APIRouter()

    get_current_active_user = authenticator.current_user(
        active=True, verified=requires_verification
    )

    callback_route_name = f"oauth-associate:{oauth_client.name}.callback"

    if redirect_url is not None:
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            oauth_client,
            redirect_url=redirect_url,
        )
    elif redirect_url_factory is not None:
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            oauth_client,
            state_secret=state_secret,
        )
    else:
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            oauth_client,
            route_name=callback_route_name,
        )

    @router.get(
        f"/login/{oauth_client.name}",
        name=f"oauth-associate:{oauth_client.name}.authorize",
    )
    async def authorize(
        request: Request,
        scopes: list[str] = Query(None),
        user: models.UP = Depends(get_current_active_user),
    ):
        if redirect_url is not None:
            authorize_redirect_url = redirect_url
        elif redirect_url_factory is not None:
            authorize_redirect_url = await smart_run(
                redirect_url_factory, request, scopes
            )
        else:
            authorize_redirect_url = str(request.url_for(callback_route_name))

        state_data = {"sub": str(user.id)}
        if redirect_url_factory:
            state_data["redirect_url"] = authorize_redirect_url
        state = generate_state_token(state_data, state_secret)
        authorization_url = await oauth_client.get_authorization_url(
            authorize_redirect_url,
            state,
            scopes,
        )

        return RedirectResponse(authorization_url)

    @router.get(
        f"/oauth-authorized/{oauth_client.name}",
        name=callback_route_name,
        description="The response varies based on the authentication backend used.",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            "INVALID_STATE_TOKEN": {
                                "summary": "Invalid state token.",
                                "value": None,
                            },
                        }
                    }
                },
            },
        },
    )
    async def callback(
        request: Request,
        user: models.UP = Depends(get_current_active_user),
        access_token_state: tuple[OAuth2Token, str] = Depends(
            oauth2_authorize_callback
        ),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    ):
        token, state = access_token_state
        account_id, account_email = await oauth_client.get_id_email(
            token["access_token"]
        )

        if account_email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.OAUTH_NOT_AVAILABLE_EMAIL,
            )

        # Try to use existing state data from request.state
        state_data = getattr(request.state, "state_data", None)
        if state_data is None:
            try:
                state_data = decode_jwt(state, state_secret, [STATE_TOKEN_AUDIENCE])
            except jwt.DecodeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        if state_data["sub"] != str(user.id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        user = await user_manager.oauth_associate_callback(
            user,
            oauth_client.name,
            token["access_token"],
            account_id,
            account_email,
            token.get("expires_at"),
            token.get("refresh_token"),
            request,
        )

        if redirect_url_after_callback:
            return RedirectResponse(redirect_url_after_callback)

        return schemas.model_validate(user_schema, user)

    return router


def get_auth_router(
    backend: AuthenticationBackend[models.UP, models.ID],
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    authenticator: Authenticator[models.UP, models.ID],
    requires_verification: bool = False,
) -> APIRouter:
    """
    Modified version of the `get_auth_router` from `fastapi_users.router.auth`.
    - Sets `g.user` to `None` after logout.

    Generate a router with login/logout routes for an authentication backend.
    """
    router = APIRouter()
    get_current_user_token = authenticator.current_user_token(
        active=True, verified=requires_verification
    )

    login_responses: OpenAPIResponseType = {
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.LOGIN_BAD_CREDENTIALS: {
                            "summary": "Bad credentials or the user is inactive.",
                            "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                        },
                        ErrorCode.LOGIN_USER_NOT_VERIFIED: {
                            "summary": "The user is not verified.",
                            "value": {"detail": ErrorCode.LOGIN_USER_NOT_VERIFIED},
                        },
                    }
                }
            },
        },
        **backend.transport.get_openapi_login_responses_success(),
    }

    @router.post(
        "/login",
        name=f"auth:{backend.name}.login",
        responses=login_responses,
    )
    async def login(
        request: Request,
        credentials: OAuth2PasswordRequestForm = Depends(),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user = await user_manager.authenticate(credentials)

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )
        if requires_verification and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
            )
        response = await backend.login(strategy, user)
        await user_manager.on_after_login(user, request, response)
        return response

    logout_responses: OpenAPIResponseType = {
        **{
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user."
            }
        },
        **backend.transport.get_openapi_logout_responses_success(),
    }

    @router.post(
        "/logout", name=f"auth:{backend.name}.logout", responses=logout_responses
    )
    async def logout(
        request: Request,
        user_token: tuple[models.UP, str] = Depends(get_current_user_token),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user, token = user_token
        response = await backend.logout(strategy, user, token)
        await user_manager.on_after_logout(user, request, response)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            g.user = None
        return response

    return router
