from __future__ import annotations
import os
from pathlib import Path

def read_secret_file(path: str | None, *, required: bool = True) -> str:
    if not path:
        if required:
            raise RuntimeError("Secret file path non impostato")
        return ""
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except Exception as e:
        if required:
            raise RuntimeError(f"Impossibile leggere secret file {path}: {e}") from e
        return ""

def env_bool(name: str, default: bool = False) -> bool:
    v = str(os.getenv(name, str(default))).strip().lower()
    return v in ("1", "true", "yes", "on")

def build_base_dsn(host: str, port: int, driver: str = "postgresql+asyncpg") -> str:
    # user/pass vuoti; saranno sovrascritti dal registry per-tenant
    return f"{driver}://@{host}:{port}/postgres"
