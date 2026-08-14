from collections.abc import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from lib.router_collection import REST_ROUTERS

# TODO: Fix this. Not great setup with global especially
_session_handle = None


def kurzpy_init(app: FastAPI, engine: AsyncEngine):
    LocalSession = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

    async def get_session() -> AsyncGenerator[AsyncSession]:
        async with LocalSession() as session:
            yield session

    global _session_handle
    _session_handle = get_session

    for class_name in REST_ROUTERS:
        router = REST_ROUTERS[class_name]
        app.include_router(router)


async def get_session() -> AsyncGenerator[AsyncSession]:
    if _session_handle is None:
        raise RuntimeError(
            "Please initialize kurzpy_init(engine), as its required for @kurzpy.rest_api"
        )

    async for session in _session_handle():
        yield session
