from typing import List, NotRequired, TypedDict, Union

from fastapi_users.authentication import JWTStrategy
from fastapi_users.authentication.strategy.db import (
    DatabaseStrategy,
)

__all__ = ["StrategyConfig", "Strategy"]


class DatabaseStrategyConfig(TypedDict):
    lifetime_seconds: NotRequired[int]


class JWTStrategyConfig(TypedDict):
    secret: str
    lifetime_seconds: NotRequired[int]
    token_audience: NotRequired[List[str]]
    algorithm: NotRequired[str]
    public_key: NotRequired[str]


StrategyConfig = Union[DatabaseStrategyConfig, JWTStrategyConfig]
Strategy = Union[JWTStrategy, DatabaseStrategy]
