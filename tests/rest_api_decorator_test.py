from httpx2 import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field, SQLModel

from lib import kurzpy
from tests.conftest import setup_mock_app


@kurzpy.rest_api
class MockModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


async def test_integrity_err(session: AsyncSession):
    client = setup_mock_app(session, [MockModel.router])

    response = client.post("/mockmodels/", json={"name": "Deadpond"})

    id = response.json()["id"]

    response = client.post("/mockmodels/", json={"id": id, "name": "Deadpond"})

    assert (
        response.json()["detail"]
        == "Failed to create MockModel with error: UNIQUE constraint failed: mockmodel.id"
    )


async def test_crud(session: AsyncSession):
    client = setup_mock_app(session, [MockModel.router])

    # Create
    response = client.post("/mockmodels/", json={"name": "Deadpond"})
    assert_response(response)

    id = response.json()["id"]

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


def assert_response(response: Response, name="Deadpond"):
    data = response.json()

    if response.status_code < 400:
        assert data["name"] == name
        assert data["id"] is not None
    else:
        # Essentially throw error message
        assert data == ""
