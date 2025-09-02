from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession
from sqlalchemy.orm import Session

# This file is just to keep the folder structure consistent.

__all__ = [
    "Session",
    "AsyncSession",
    "Connection",
    "AsyncConnection",
    "SQLASession",
    "SQLAConnection",
]

SQLASession = Session | AsyncSession
SQLAConnection = Connection | AsyncConnection
