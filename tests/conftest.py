from typing import List

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, StaticPool

from app.core.session import get_session
from main import app


@pytest.fixture(name="session")
async def session_fixture():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    LocalSession = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    async with LocalSession() as session:
        yield session


def setup_mock_app(session: AsyncSession, mock_routes: List[APIRouter]) -> TestClient:
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    for r in mock_routes:
        app.include_router(r)

    return TestClient(app)
