import enum
from datetime import date, datetime

from fastapi_rtk import Model, db
from fastapi_rtk.types import FileColumn, ImageColumn
from sqlalchemy import (
    JSON,
    Column,
    ForeignKey,
    Integer,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

AssetApplication = Table(
    "AssetApplication",
    db.get_metadata("assets"),
    Column("id", Integer, primary_key=True),
    Column("asset_id", Integer, ForeignKey("Asset.id")),
    Column("application_id", Integer, ForeignKey("Application.id")),
)


class Application(Model):
    __bind_key__ = "assets"
    __tablename__ = "Application"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    assets: Mapped[list["Asset"]] = relationship(
        "Asset", secondary=AssetApplication, back_populates="applications"
    )

    def __repr__(self):
        return self.name


class AssetEnum(enum.Enum):
    ordered: int = 1
    in_delivery: int = 2
    delivered: int = 3


class Asset(Model):
    __bind_key__ = "assets"
    __tablename__ = "Asset"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    my_number: Mapped[int] = mapped_column(default=1)
    my_boolean: Mapped[bool] = mapped_column(default=False)
    my_json: Mapped[dict] = mapped_column(JSON, default={})
    my_enum: Mapped[AssetEnum] = mapped_column(default=AssetEnum.ordered)
    date_time: Mapped[datetime]
    date: Mapped[date]

    owner_id: Mapped[int] = mapped_column(ForeignKey("unit.id"))
    owner: Mapped["Unit"] = relationship("Unit", back_populates="owner")

    applications: Mapped[list["Application"]] = relationship(
        "Application", secondary=AssetApplication, back_populates="assets"
    )

    my_file: Mapped[str | None] = mapped_column(FileColumn)
    my_image: Mapped[str | None] = mapped_column(ImageColumn)

    @property
    async def async_property(self):
        return "This is an async property"

    @property
    def my_property(self):
        return "This is a property"

    def __repr__(self):
        return self.name


class Unit(Model):
    __bind_key__ = "assets"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]

    owner: Mapped[list[Asset]] = relationship("Asset", back_populates="owner")

    def __repr__(self):
        return self.name


class StringPk(Model):
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]

    def __repr__(self):
        return self.name
