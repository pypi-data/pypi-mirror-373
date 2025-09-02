from datetime import datetime
from typing import Any, Dict, Generic, Optional, Type

from fastapi import Depends
from fastapi_users.authentication.strategy.db import (
    AP,
    AccessTokenDatabase,
    DatabaseStrategy,
)
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyBaseAccessTokenTable,
)
from sqlalchemy import ForeignKey, Integer, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, Session, declared_attr, mapped_column

from ...backends.sqla.model import Model
from ...const import ACCESSTOKEN_TABLE
from ...db import get_session_factory
from ...utils import generate_schema_from_typed_dict, safe_call, smart_run
from .config import DatabaseStrategyConfig

__all__ = ["get_database_strategy_generator"]


class SQLAlchemyAccessTokenDatabase(Generic[AP], AccessTokenDatabase[AP]):
    """
    Modified version of the SQLAlchemyAccessTokenDatabase class from fastapi_users_db_sqlalchemy.access_token.
    - Allow the use of both async and sync database connections.

    Access token database adapter for SQLAlchemy.

    :param session: SQLAlchemy session instance.
    :param access_token_table: SQLAlchemy access token model.
    """

    session: AsyncSession | Session

    def __init__(
        self,
        session: AsyncSession | Session,
        access_token_table: Type[AP],
    ):
        self.session = session
        self.access_token_table = access_token_table

    async def get_by_token(
        self, token: str, max_age: Optional[datetime] = None
    ) -> Optional[AP]:
        statement = select(self.access_token_table).where(
            self.access_token_table.token == token  # type: ignore
        )
        if max_age is not None:
            statement = statement.where(
                self.access_token_table.created_at >= max_age  # type: ignore
            )

        results = await smart_run(self.session.execute, statement)
        return results.scalar_one_or_none()

    async def create(self, create_dict: Dict[str, Any]) -> AP:
        access_token = self.access_token_table(**create_dict)
        self.session.add(access_token)
        await safe_call(self.session.commit())
        await safe_call(self.session.refresh(access_token))
        return access_token

    async def update(self, access_token: AP, update_dict: Dict[str, Any]) -> AP:
        for key, value in update_dict.items():
            setattr(access_token, key, value)
        self.session.add(instance=access_token)
        await safe_call(coro=self.session.commit())
        await safe_call(self.session.refresh(access_token))
        return access_token

    async def delete(self, access_token: AP) -> None:
        await safe_call(self.session.delete(access_token))
        await safe_call(coro=self.session.commit())


class AccessToken(SQLAlchemyBaseAccessTokenTable[int], Model):
    __tablename__ = ACCESSTOKEN_TABLE

    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(
            Integer, ForeignKey("ab_user.id", ondelete="cascade"), nullable=False
        )


async def get_access_token_db(
    session: AsyncSession | Session = Depends(
        get_session_factory(AccessToken.__bind_key__)
    ),
):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)


def get_database_strategy_generator(params: dict[str, Any]):
    schema = generate_schema_from_typed_dict(DatabaseStrategyConfig)
    params = schema.model_validate(params).model_dump(exclude_unset=True)

    def get_database_strategy(
        access_token_db: SQLAlchemyAccessTokenDatabase[AccessToken] = Depends(
            get_access_token_db
        ),
    ) -> DatabaseStrategy:
        return DatabaseStrategy(access_token_db, **params)

    return get_database_strategy
