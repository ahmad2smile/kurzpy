from sqlmodel import Field, SQLModel

from app.decorators.rest_api_decorator import rest_api


@rest_api
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
