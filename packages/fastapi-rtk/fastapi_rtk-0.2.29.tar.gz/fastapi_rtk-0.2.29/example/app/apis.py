import random
from datetime import datetime
from typing import List

from fastapi import HTTPException, Response, UploadFile
from fastapi.responses import FileResponse
from fastapi_rtk import GeneralResponse
from fastapi_rtk.api import (
    BaseApi,
    ModelRestApi,
    SQLAInterface,
)
from fastapi_rtk.backends.generic import (
    GenericColumn,
    GenericInterface,
    GenericModel,
    GenericSession,
)
from fastapi_rtk.decorators import expose, login_required, permission_name, protect
from fastapi_rtk.file_managers import FileManager
from fastapi_rtk.utils import safe_call
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from sqlalchemy.orm import Session, scoped_session

from .app import toolkit
from .models import *


class AssetApi(ModelRestApi):
    resource_name = "assets"
    datamodel = SQLAInterface(Asset)
    page_size = 200
    description_columns = {
        "name": "Name of the asset",
        "owner_id": "ID of the asset owner",
        "owner": "Owner of the asset",
        "date_time": "Date time of the asset",
        "date": "Date of the asset",
    }
    quick_filters = [
        {
            "name": "asset_name",
            "label": "Asset Name",
            "column": "name",
            "type": "multiselect",
            "options": [
                {"value": f"asset&{i}", "label": f"asset&{i}"} for i in range(10)
            ],
        }
    ]

    async def bulk_update_time(
        self,
        body: dict | List,
        query,
        session: async_scoped_session[AsyncSession] | scoped_session[Session],
    ) -> Response:
        try:
            stmt = (
                update(Asset).where(Asset.id.in_(body)).values(date_time=datetime.now())
            )
            result = await safe_call(session.execute(stmt))
            await safe_call(session.commit())
            return GeneralResponse(detail=f"Updated {result.rowcount} records")
        except Exception as e:
            await safe_call(session.rollback())
            print(e)
            raise HTTPException(status_code=500, detail=str(e))


class ApplicationApi(ModelRestApi):
    resource_name = "applications"
    datamodel = SQLAInterface(Application)
    description_columns = {
        "name": "Name of the Application",
        "description": "Description",
    }
    quick_filters = [
        {
            "name": "application_name",
            "label": "Application Name",
            "column": "name",
            "type": "multiselect",
            "options": [
                {"value": f"application_{i}", "label": f"application_{i}"}
                for i in range(10)
            ],
        }
    ]


class UnitApi(ModelRestApi):
    resource_name = "units"
    datamodel = SQLAInterface(Unit)
    description_columns = {"name": "Name of the unit"}
    quick_filters = [
        {
            "name": "unit_name",
            "label": "Unit Name",
            "column": "name",
            "type": "multiselect",
            "options": [
                {"value": f"unit_{i}", "label": f"unit_{i}"} for i in range(10)
            ],
        }
    ]


class StringPkApi(ModelRestApi):
    resource_name = "stringpk"

    datamodel = SQLAInterface(StringPk)

    def pre_add(self, item, params):
        item.id = item.name


class ProtectedApi(BaseApi):
    msg = "Hello, World!"

    @expose("/hello")
    def hello(self):
        return self.msg

    @expose("/hello/login_only")
    @login_required
    def hello_login_only(self):
        return self.msg + " (login only)"

    @expose("/hello/protected")
    @protect()
    @permission_name("hello")
    def hello_protected(self):
        return self.msg + " (protected)"


class UserGenericModel(GenericModel):
    id = GenericColumn(int, primary_key=True, auto_increment=True)
    first_name = GenericColumn(str, nullable=False)
    last_name = GenericColumn(str, nullable=False)
    email = GenericColumn(str, nullable=False)
    logged_in = GenericColumn(bool)


class UserGenericSession(GenericSession):
    def load_data(self):
        # Load 1000 records
        for i in range(1000):
            model = UserGenericModel()
            model.first_name = (
                str(i) + " " + random.choice(["John", "Jane", "Doe", "Alice", "Bob"])
            )
            model.last_name = random.choice(
                ["Doe", "Smith", "Johnson", "Brown", "Williams"]
            )
            model.email = (
                f"{model.first_name.lower()}.{model.last_name.lower()}@example.com"
            )
            model.logged_in = random.choice([True, False])
            self.add(model)


class UserGenericApi(ModelRestApi):
    resource_name = "generic_datasource"
    base_order = ("email", "desc")
    datamodel = GenericInterface(UserGenericModel, UserGenericSession)


class FileApi(BaseApi):
    resource_name = "test"

    @expose("/uploadfile", methods=["POST"])
    def uploadfile(self, file: UploadFile):
        fm = FileManager()
        new_name = fm.generate_name(file)
        return fm.save_file(file, new_name)

    @expose("/downloadfile/{filename}", methods=["GET"])
    def downloadfile(self, filename: str):
        fm = FileManager()
        path = fm.get_path(filename)
        return FileResponse(path, filename=filename)

    @expose("/deletefile/{filename}", methods=["DELETE"])
    def deletefile(self, filename: str):
        fm = FileManager()
        fm.delete_file(filename)
        return GeneralResponse(detail=f"Deleted {filename}")


toolkit.add_api(AssetApi)
toolkit.add_api(ApplicationApi)
toolkit.add_api(UnitApi)
toolkit.add_api(StringPkApi)
toolkit.add_api(ProtectedApi)
toolkit.add_api(UserGenericApi)
toolkit.add_api(FileApi)
