import datetime as dt
import os
from typing import ClassVar

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    HISTORY_MAX_TURNS: int = Field(..., description="Maximum number of turns to keep in chat history")
    HISTORY_CLEANUP_SECONDS: int = Field(..., description="Seconds after which to clean up old sessions")
    OPENAI_API_KEY: str = Field(..., description="API key for OpenAI access")

    @classmethod
    def from_env(cls) -> "Settings":
        env_dict = {
            "HISTORY_MAX_TURNS": int(os.getenv("HISTORY_MAX_TURNS")),
            "HISTORY_CLEANUP_SECONDS": int(os.getenv("HISTORY_CLEANUP_SECONDS")),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        }
        return cls(**env_dict)


class Logger:
    COLORS: ClassVar[dict[str, str]] = {
        "INFO": "\033[94m",  # Blue
        "WARN": "\033[93m",  # Yellow
        "EXCEPTION": "\033[95m",  # Magenta
        "ERROR": "\033[91m",  # Red
        "RESET": "\033[0m",
    }

    def __init__(self, location: str) -> None:
        self.location = location

    def _log(self, level: str, message: str) -> None:
        timestamp = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M:%S")
        color = self.COLORS.get(level, "")
        reset = self.COLORS["RESET"]
        print(f"{color}[{timestamp}] [{level}] [{self.location}] {message}{reset}")  # noqa: T201

    def info(self, message: str) -> None:
        self._log("INFO", message)

    def warning(self, message: str) -> None:
        self._log("WARN", message)

    def exception(self, message: str) -> None:
        self._log("EXCEPTION", message)

    def error(self, message: str) -> None:
        self._log("ERROR", message)
