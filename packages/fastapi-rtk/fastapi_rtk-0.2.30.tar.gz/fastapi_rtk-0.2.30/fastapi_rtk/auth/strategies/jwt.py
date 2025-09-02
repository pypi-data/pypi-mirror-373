from typing import Any

from fastapi_users.authentication import JWTStrategy

from ...utils import generate_schema_from_typed_dict
from .config import JWTStrategyConfig

__all__ = ["get_jwt_strategy_generator"]


def get_jwt_strategy_generator(params: dict[str, Any]):
    schema = generate_schema_from_typed_dict(JWTStrategyConfig)
    params = schema.model_validate(params).model_dump(exclude_unset=True)

    def get_jwt_strategy() -> JWTStrategy:
        return JWTStrategy(**params)

    return get_jwt_strategy
