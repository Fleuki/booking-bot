import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True, slots=True)
class Config:
    bot_token: str
    admin_ids: tuple[int, ...]
    database_path: Path

    @classmethod
    def from_env(cls) -> "Config":
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise ValueError("BOT_TOKEN is not set in environment")

        admin_raw = os.getenv("ADMIN_IDS", "")
        admin_ids = tuple(
            int(item.strip())
            for item in admin_raw.split(",")
            if item.strip().isdigit()
        )

        db_path = Path(os.getenv("DATABASE_PATH", "data/booking.db"))
        if not db_path.is_absolute():
            db_path = BASE_DIR / db_path

        return cls(
            bot_token=token,
            admin_ids=admin_ids,
            database_path=db_path,
        )


config = Config.from_env()
