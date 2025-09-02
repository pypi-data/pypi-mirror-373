import random
from datetime import date, datetime

from fastapi_rtk import db, g
from fastapi_rtk.utils import safe_call
from fastapi_rtk.utils.async_task_runner import AsyncTaskRunner

from .models import Application, Asset, Unit


async def add_base_data():
    async with AsyncTaskRunner():
        await g.current_app.security.create_user(
            username="admin",
            email="admin@test.com",
            password="admin",
            first_name="Admin",
            last_name="Admin",
            roles=[g.admin_role],
            raise_exception=False,
        )

        async with db.session("assets") as session:
            applications = [
                Application(name=f"application_{i}", description=f"info_{i}")
                for i in range(20)
            ]
            units = [Unit(name=f"unit_{i}") for i in range(10)]
            assets = [
                Asset(
                    name=f"asset_{i}",
                    date_time=datetime.now(),
                    date=date.today(),
                    owner=units[random.randint(0, len(units) - 1)],
                    applications=[
                        applications[random.randint(0, len(applications) - 1)]
                        for _ in range(5)
                    ],
                )
                for i in range(100)
            ]
            session.add_all(applications)
            session.add_all(units)
            session.add_all(assets)
            await safe_call(session.commit())
