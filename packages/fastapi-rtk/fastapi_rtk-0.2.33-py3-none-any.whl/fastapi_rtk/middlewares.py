import base64
import hashlib
import os
from typing import Callable

from bs4 import BeautifulSoup
from fastapi import FastAPI, Request, Response
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .globals import g
from .setting import Setting

__all__ = ["ProfilerMiddleware"]


class ProfilerMiddleware(BaseHTTPMiddleware):
    """Middleware to profile the current request using pyinstrument."""

    def __init__(self, app: ASGIApp) -> None:
        os.makedirs(Setting.PROFILER_FOLDER, exist_ok=True)
        super().__init__(app, profiler_middleware_dispatch)


class SecWebPatchDocsMiddleware(BaseHTTPMiddleware):
    """Middleware to patch the `docs` issue due to `SecWeb` CSP using sec_web_patch_docs_middleware_dispatch()."""

    def __init__(self, app: ASGIApp, fastapi: FastAPI) -> None:
        super().__init__(
            app,
            get_sec_web_patch_docs_middleware_dispatch(
                get_swagger_ui_script_hash(fastapi)
            ),
        )


class SecWebPatchReDocMiddleware(BaseHTTPMiddleware):
    """Middleware to patch the `redoc` issue due to `SecWeb` CSP using sec_web_patch_docs_middleware_dispatch()."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app, sec_web_patch_redoc_middleware_dispatch)


async def profiler_middleware_dispatch(
    request: Request,
    call_next: Callable,
) -> Response:
    """
    Profile the current request

    Taken from https://pyinstrument.readthedocs.io/en/latest/guide.html#profile-a-web-request-in-fastapi
    with small improvements.
    """
    profile_type = Setting.PROFILER_TYPE
    renderer_name = Setting.PROFILER_RENDERER
    if not g.renderer_cache:
        g.renderer_cache = {}
    renderer = g.renderer_cache.get(renderer_name)
    if not renderer:
        renderer = getattr(g.pyinstrument.renderers, renderer_name)()
        g.renderer_cache[renderer_name] = renderer

    # we profile the request along with all additional middlewares, by interrupting
    # the program every 1ms1 and records the entire stack at that point
    with g.pyinstrument.Profiler(
        interval=0.0001, async_mode="enabled", use_timing_thread=True
    ) as profiler:
        response = await call_next(request)

    # we dump the profiling into a file
    folder_name = Setting.PROFILER_FOLDER + request.url.path
    os.makedirs(
        folder_name,
        exist_ok=True,
    )
    file_name = folder_name + f"/{request.method}.{profile_type}"
    with open(file_name, "w") as out:
        out.write(profiler.output(renderer=renderer))
    return response


def patch_csp_string(
    csp: str, patch: dict[str, list[str] | None], *, override: list[str] | None = None
):
    """
    Patch a Content Security Policy (CSP) string with additional directives.

    Args:
        csp (str): The original CSP string.
        patch (dict): A dictionary where keys are CSP directives and values are lists of sources to add.
        override (list[str] | None): A list of CSP directives to override the existing ones instead of appending. Defaults to None.

    Returns:
        str: The patched CSP string.
    """
    csp_dict = csp_string_to_dict(csp)
    for key, values in patch.items():
        if values is None:
            # If the value is None, remove the key from the dictionary
            csp_dict.pop(key, None)
            continue

        if key in csp_dict:
            if override is not None and key in override:
                # If the key is in override, replace the existing values
                csp_dict[key] = values
            else:
                csp_dict[key].extend(values)
        else:
            csp_dict[key] = values
    return csp_dict_to_string(csp_dict)


def csp_string_to_dict(csp: str):
    """
    Convert a Content Security Policy (CSP) string to a dictionary.

    Args:
        csp (str): The CSP string to convert.

    Returns:
        dict[str, list[str]]: A dictionary where keys are CSP directives and values are lists of sources.
    """
    csp_dict: dict[str, list[str]] = {}
    directives = csp.split(";")
    for directive in directives:
        if directive.strip():
            parts = directive.split()
            key = parts[0].strip()
            values = [v.strip() for v in parts[1:]]
            csp_dict[key] = values
    return csp_dict


def csp_dict_to_string(csp_dict: dict[str, list[str]]):
    """
    Convert a Content Security Policy (CSP) dictionary to a string.

    Args:
        csp_dict (dict): A dictionary where keys are CSP directives and values are lists of sources.

    Returns:
        str: The CSP string representation.
    """
    parts = []
    for key, values in csp_dict.items():
        if values:
            parts.append(f"{key} {' '.join(values)}")
        else:
            parts.append(key)
    return "; ".join(parts) + ";"


def get_sec_web_patch_docs_middleware_dispatch(script_hash: str):
    """
    Get a middleware function to patch the Swagger UI documentation with security headers, specifically for the Swagger UI script.

    Args:
        script_hash (str): The hash of the Swagger UI script to be included in the CSP.
    """

    async def sec_web_patch_docs_middleware_dispatch(
        request: Request,
        call_next: Callable,
    ) -> Response:
        """
        Middleware to patch the Swagger UI documentation with security headers.

        Args:
            request (Request): The incoming request object.
            call_next (Callable): A callable to process the request and return a response.

        Returns:
            Response: The response object with patched Content Security Policy (CSP) headers.
        """
        response = await call_next(request)
        if request.url.path == request.app.docs_url:
            csp = response.headers.get("Content-Security-Policy", "")
            if csp:
                patched_csp = patch_csp_string(
                    csp,
                    {
                        "img-src": ["https://fastapi.tiangolo.com/img/favicon.png"],
                        "script-src-elem": [
                            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
                            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
                            script_hash,
                        ],
                        "require-trusted-types-for": None,
                    },
                )
                response.headers["Content-Security-Policy"] = patched_csp

        return response

    return sec_web_patch_docs_middleware_dispatch


def get_swagger_ui_script_hash(app: FastAPI):
    """
    Get the hash of the Swagger UI script to be used in the Content Security Policy (CSP).
    This function extracts the script content from the Swagger UI HTML page generated by FastAPI
    and computes its SHA-256 hash, which is then base64 encoded to be used in the CSP.

    This is necessary to allow the Swagger UI script to be executed in the browser
    without violating the Content Security Policy (CSP) set by the application.

    Args:
        app (FastAPI): The FastAPI application instance.

    Raises:
        ValueError: If no SwaggerUIBundle script is found in the HTML.

    Returns:
        str: The base64 encoded SHA-256 hash of the Swagger UI script content,
             formatted as 'sha256-{hash}' to be used in the CSP.
    """
    #! Function that taken from the `FastApi.setup` to generate the OpenAPI HTML page
    root_path = app.root_path.rstrip("/")
    openapi_url = root_path + app.openapi_url
    oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url
    if oauth2_redirect_url:
        oauth2_redirect_url = root_path + oauth2_redirect_url
    html = get_swagger_ui_html(
        openapi_url=openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=oauth2_redirect_url,
        init_oauth=app.swagger_ui_init_oauth,
        swagger_ui_parameters=app.swagger_ui_parameters,
    ).body.decode("utf-8")

    # Get the script content from the HTML
    script_content = None
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script")
    for script in scripts:
        if script.string and "SwaggerUIBundle" in script.string:
            script_content = script.string
            break

    if not script_content:
        raise ValueError("No SwaggerUIBundle script found in the HTML")

    # Hash the script content for Content Security Policy (CSP)
    # This is needed to allow the script to be executed in the browser
    # and to prevent CSP violations.
    script_bytes = script_content.encode("utf-8")
    hash_bytes = hashlib.sha256(script_bytes).digest()
    hash_b64 = base64.b64encode(hash_bytes).decode()
    return f"'sha256-{hash_b64}'"


async def sec_web_patch_redoc_middleware_dispatch(
    request: Request,
    call_next: Callable,
) -> Response:
    """
    Middleware to patch the ReDoc documentation with security headers.

    Args:
        request (Request): The incoming request object.
        call_next (Callable): A callable to process the request and return a response.

    Returns:
        Response: The response object with patched Content Security Policy (CSP) headers.
    """
    response = await call_next(request)
    if request.url.path == request.app.redoc_url:
        csp = response.headers.get("Content-Security-Policy", "")
        if csp:
            patched_csp = patch_csp_string(
                csp,
                {
                    "img-src": [
                        "https://fastapi.tiangolo.com/img/favicon.png",
                        "https://cdn.redoc.ly/redoc/logo-mini.svg",
                    ],
                    "script-src-elem": [
                        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
                    ],
                    "worker-src": [
                        "blob:",
                    ],
                    "style-src": ["'self'", "https:", "'unsafe-inline'"],
                    "require-trusted-types-for": None,
                },
                override=["style-src"],
            )
            response.headers["Content-Security-Policy"] = patched_csp

    return response
