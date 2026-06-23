from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

# TODO: Fix this. Not great setup with global especially
_session_handle = None


def kurzpy_init(engine: AsyncEngine):
    LocalSession = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

    async def get_session() -> AsyncGenerator[AsyncSession]:
        async with LocalSession() as session:
            yield session

    global _session_handle
    _session_handle = get_session


async def get_session() -> AsyncGenerator[AsyncSession]:
    if _session_handle is None:
        raise RuntimeError(
            "Please initialize kurzpy_init(engine), as its required for @kurzpy.rest_api"
        )

    async for session in _session_handle():
        yield session
