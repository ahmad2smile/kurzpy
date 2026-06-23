from sqlmodel import Field, SQLModel

from lib import kurzpy


@kurzpy.rest_api
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
