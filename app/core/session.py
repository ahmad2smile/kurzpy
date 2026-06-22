from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import config

engine = create_async_engine(config.db_url)
LocalSession = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_session():
    async with LocalSession() as session:
        yield session
