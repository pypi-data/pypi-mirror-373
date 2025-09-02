from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseOAuthAccountTable
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Sequence,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...backends.sqla.model import Model
from ...const import (
    API_SEQUENCE,
    API_TABLE,
    ASSOC_PERMISSION_API_ROLE_SEQUENCE,
    ASSOC_PERMISSION_API_ROLE_TABLE,
    ASSOC_USER_ROLE_SEQUENCE,
    ASSOC_USER_ROLE_TABLE,
    OAUTH_SEQUENCE,
    OAUTH_TABLE,
    PERMISSION_API_SEQUENCE,
    PERMISSION_API_TABLE,
    PERMISSION_SEQUENCE,
    PERMISSION_TABLE,
    ROLE_SEQUENCE,
    ROLE_TABLE,
    USER_SEQUENCE,
    USER_TABLE,
)

__all__ = ["Api", "Permission", "PermissionApi", "Role", "User"]

permission_view_id = f"{PERMISSION_API_TABLE.replace('ab_', '')}_id"
view_menu_id = f"{API_TABLE.replace('ab_', '')}_id"

assoc_user_role = Table(
    ASSOC_USER_ROLE_TABLE,
    Model.metadata,
    Column("id", Integer, Sequence(ASSOC_USER_ROLE_SEQUENCE), primary_key=True),
    Column("user_id", Integer, ForeignKey(f"{USER_TABLE}.id"), nullable=False),
    Column("role_id", Integer, ForeignKey(f"{ROLE_TABLE}.id"), nullable=False),
    UniqueConstraint("user_id", "role_id", name="user_role_unique"),
)

assoc_permission_api_role = Table(
    ASSOC_PERMISSION_API_ROLE_TABLE,
    Model.metadata,
    Column(
        "id", Integer, Sequence(ASSOC_PERMISSION_API_ROLE_SEQUENCE), primary_key=True
    ),
    Column("role_id", Integer, ForeignKey(f"{ROLE_TABLE}.id"), nullable=False),
    Column(
        permission_view_id,
        Integer,
        ForeignKey(f"{PERMISSION_API_TABLE}.id"),
        nullable=False,
    ),
    UniqueConstraint("role_id", permission_view_id, name="role_permission_api_unique"),
)


class PermissionApi(Model):
    __tablename__ = PERMISSION_API_TABLE
    __table_args__ = (UniqueConstraint(view_menu_id, "permission_id"),)
    id: Mapped[int] = mapped_column(
        Integer, Sequence(PERMISSION_API_SEQUENCE), primary_key=True
    )

    api_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{API_TABLE}.id"), name=view_menu_id, nullable=False
    )
    api: Mapped["Api"] = relationship(
        "Api", back_populates="permissions", lazy="selectin"
    )

    permission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{PERMISSION_TABLE}.id"), nullable=False
    )
    permission: Mapped["Permission"] = relationship(
        "Permission", back_populates="apis", lazy="selectin"
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=assoc_permission_api_role,
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"{self.permission} on {self.api}"


class Api(Model):
    __tablename__ = API_TABLE
    id: Mapped[int] = mapped_column(Integer, Sequence(API_SEQUENCE), primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    permissions: Mapped[list[PermissionApi]] = relationship(
        PermissionApi,
        back_populates="api",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __eq__(self, other):
        return (isinstance(other, self.__class__)) and (self.name == other.name)

    def __neq__(self, other):
        return self.name != other.name

    def __repr__(self) -> str:
        return self.name


class Permission(Model):
    __tablename__ = PERMISSION_TABLE
    id: Mapped[int] = mapped_column(
        Integer, Sequence(PERMISSION_SEQUENCE), primary_key=True
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    apis: Mapped[list[PermissionApi]] = relationship(
        PermissionApi,
        back_populates="permission",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return self.name


class Role(Model):
    __tablename__ = ROLE_TABLE
    id: Mapped[int] = mapped_column(Integer, Sequence(ROLE_SEQUENCE), primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(
        "User", secondary=assoc_user_role, back_populates="roles", lazy="selectin"
    )

    permissions: Mapped[list[PermissionApi]] = relationship(
        PermissionApi,
        secondary=assoc_permission_api_role,
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return self.name


class OAuthAccount(SQLAlchemyBaseOAuthAccountTable[int], Model):
    __tablename__ = OAUTH_TABLE
    id: Mapped[int] = mapped_column(Integer, Sequence(OAUTH_SEQUENCE), primary_key=True)
    access_token: Mapped[str] = mapped_column(String(length=4096), nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(
        String(length=4096), nullable=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{USER_TABLE}.id", ondelete="cascade"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="oauth_accounts")

    def __repr__(self) -> str:
        return f"{self.oauth_name} - {self.account_email}"


class User(Model):
    __tablename__ = USER_TABLE
    id: Mapped[int] = mapped_column(Integer, Sequence(USER_SEQUENCE), primary_key=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(1024), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(256))
    last_name: Mapped[str | None] = mapped_column(String(256))
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime)
    login_count: Mapped[int | None] = mapped_column(Integer)
    fail_login_count: Mapped[int | None] = mapped_column(Integer)
    created_on: Mapped[datetime | None] = mapped_column(
        DateTime, default=lambda: datetime.now()
    )
    changed_on: Mapped[datetime | None] = mapped_column(
        DateTime, default=lambda: datetime.now()
    )

    @declared_attr
    def created_by_fk(self):
        return Column(Integer, ForeignKey("ab_user.id"), default=self.get_user_id)

    @declared_attr
    def changed_by_fk(self):
        return Column(Integer, ForeignKey("ab_user.id"), default=self.get_user_id)

    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    roles: Mapped[list[Role]] = relationship(
        Role, secondary=assoc_user_role, back_populates="users", lazy="selectin"
    )

    @classmethod
    def get_user_id(cls):
        try:
            from ...globals import g

            return g.user.id
        except Exception:
            return None

    @property
    def hashed_password(self) -> str:
        return self.password

    @hashed_password.setter
    def hashed_password(self, value: str):
        self.password = value

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self):
        return self.active

    @property
    def is_verified(self) -> bool:
        return getattr(self, "verified", False)

    @is_verified.setter
    def is_verified(self, value: bool):
        if hasattr(self, "verified"):
            self.verified = value

    @property
    def is_superuser(self):
        from ...globals import g

        return any(role.name == g.admin_role for role in self.roles)

    @property
    def is_anonymous(self):
        return False

    def __repr__(self) -> str:
        return self.full_name

    def __init__(self, **kw):
        super().__init__(**kw)
        # Add email as username if username is not provided
        if not self.username:
            self.username = self.email
