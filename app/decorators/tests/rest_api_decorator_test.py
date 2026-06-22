from httpx2 import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field, SQLModel

from app.decorators.rest_api_decorator import rest_api
from app.decorators.tests.conftest import setup_mock_app


@rest_api
class MockModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


def assert_response(response: Response, name="Deadpond"):
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == name
    assert data["id"] is not None


async def test_crud(session: AsyncSession):
    client = setup_mock_app(session, [MockModel.router])

    # Create
    response = client.post("/mockmodels/", json={"name": "Deadpond"})
    id = response.json()["id"]
    assert_response(response)

    # Read
    response = client.get(f"/mockmodels/{id}")
    assert_response(response)

    # Update
    response = client.put("/mockmodels/", json={"id": id, "name": "Deadpool"})
    assert_response(response, "Deadpool")

    # Delete
    response = client.delete(f"/mockmodels/{id}")
    assert_response(response, "Deadpool")

    response = client.get(f"/mockmodels/{id}")
    assert response.status_code == 404
