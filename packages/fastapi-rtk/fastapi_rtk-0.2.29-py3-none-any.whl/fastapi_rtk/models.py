from .const import logger
from .security.sqla.models import *

logger.warning(
    "module 'fastapi_rtk.models' is deprecated, use 'fastapi_rtk.security.sqla.models' instead."
)
