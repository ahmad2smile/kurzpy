from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from app.core.config import config
from app.core.session import engine
from app.models.user import User
from lib import kurzpy_init


@asynccontextmanager
async def app_lifespan(_: FastAPI):
    if config.environment == "dev":
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    yield


kurzpy_init(engine=engine)

app = FastAPI(lifespan=app_lifespan)

app.include_router(User.router)
