from .const import logger
from .security.sqla.apis import *

logger.warning(
    "module 'fastapi_rtk.apis' is deprecated, use 'fastapi_rtk.security.sqla.apis' instead."
)
