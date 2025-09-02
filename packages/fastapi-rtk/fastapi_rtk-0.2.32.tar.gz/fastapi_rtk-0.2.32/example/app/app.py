import logging

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi_rtk import FastAPIReactToolkit, User
from fastapi_rtk.manager import UserManager

from .base_data import add_base_data

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.INFO)


class CustomUserManager(UserManager):
    async def on_after_login(
        self,
        user: User,
        request: Request | None = None,
        response: Response | None = None,
    ) -> None:
        await super().on_after_login(user, request, response)
        print("User logged in: ", user)


async def on_startup(app: FastAPI):
    await add_base_data()
    print("base data added")
    pass


app = FastAPI(docs_url="/openapi/v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:6006", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

toolkit = FastAPIReactToolkit(
    auth={
        "user_manager": CustomUserManager,
        # "password_helper": FABPasswordHelper(),  #! Add this line to use old password hash
    },
    create_tables=True,
    on_startup=on_startup,
)
toolkit.config.from_pyfile("./app/config.py")
toolkit.initialize(app)

from .apis import *
