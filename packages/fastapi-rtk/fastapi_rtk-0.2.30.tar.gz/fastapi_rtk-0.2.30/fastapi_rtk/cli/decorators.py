from functools import wraps

import typer
from fastapi_cli.discover import get_import_data
from fastapi_cli.exceptions import FastAPICLIException

from ..db import db
from ..globals import g
from .const import logger
from .utils import run_in_current_event_loop


def ensure_fastapi_rtk_tables_exist(f):
    @wraps(f)
    @_set_migrate_mode
    @_check_existing_app
    def wrapper(*args, **kwargs):
        run_in_current_event_loop(db.init_fastapi_rtk_tables())
        return f(*args, **kwargs)

    return wrapper


def _check_existing_app(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            get_import_data(path=g.path)
            return f(*args, **kwargs)
        except FastAPICLIException as e:
            logger.error(str(e))
            raise typer.Exit(code=1) from None

    return wrapper


def _set_migrate_mode(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        g.is_migrate = True
        return f(*args, **kwargs)

    return wrapper
