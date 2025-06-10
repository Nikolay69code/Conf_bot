from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str = "7641107074:AAE1Nf4O8JIdu_P3ZQ2QrnLNjxeioixT97g"
    ADMIN_ID: int = 1557542470
    DATABASE_URL: str = "sqlite+aiosqlite:///bot.db"

    class Config:
        env_file = ".env"

settings = Settings() 