from .backends.sqla.filters import *
from .const import logger

logger.warning(
    "module 'fastapi_rtk.filters' is deprecated, use 'fastapi_rtk.backends.sqla.filters' instead."
)
