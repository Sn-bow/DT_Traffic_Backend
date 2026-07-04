from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

def _bool_env(name:str, default: bool) -> bool:
    raw = os.getenv(name) # raw = 원본값
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    BASE_DIR = BASE_DIR
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", "5001"))
    FLASK_DEBUG = _bool_env("FLASK_DEBUG", True)

