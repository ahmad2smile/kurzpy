from sqlmodel import Field, SQLModel

from app.decorators.kurzpy_decorator import kurzpy


@kurzpy.rest_api
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
