from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    environment: str = "dev"
    db_user: str = ""
    db_password: str = ""
    db_name: str = "kurzdb"

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@127.0.0.1:5432/{self.db_name}"


config = Config()
