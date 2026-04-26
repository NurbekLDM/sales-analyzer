from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    database_url: str
    openai_api_key: str
    openai_model: str

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            database_url=os.getenv("DATABASE_URL", "sqlite:///sales_analyzer.db"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        )

    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key.strip())
