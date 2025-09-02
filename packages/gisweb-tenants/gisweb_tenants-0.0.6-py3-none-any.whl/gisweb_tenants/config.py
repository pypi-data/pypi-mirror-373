# gisweb_tenants/config.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
from sqlalchemy.engine import make_url
from pathlib import Path

Mode = Literal["development", "testing", "production"]

@dataclass(frozen=True)
class TenantSettings:
    # Ambiente
    MODE: Mode = "development"

    # Multitenant HTTP
    TENANT_HEADER: str = "X-Tenant"
    DEFAULT_TENANT: str = "istanze"

    # DB di base (host, porta, driver, utente/password di default)
    # Il nome database verrà sovrascritto per-tenant dal registry quando presente.
    ASYNC_DATABASE_URI: str = "postgresql+asyncpg://postgres:postgres@localhost:6432/postgres"

    # SQLAlchemy
    ECHO_SQL: bool = False
    POOL_SIZE: int = 10

    # Verrà usato come application_name: "<APP_NAME_PREFIX>:<tenant>"
    APP_NAME_PREFIX: str = "fastapi"

    def drivername(self) -> str:
        """
        Ritorna lo scheme del driver, es.:
        - 'postgresql+asyncpg'
        - 'postgresql+psycopg'
        Serve a scegliere dove mettere application_name (server_settings vs connect_args).
        """
        return make_url(self.ASYNC_DATABASE_URI).drivername


@dataclass(frozen=True, slots=True)
class AuthConfig:
    access_secret: str
    refresh_secret: str
    issuer: str = "istanzeonline"
    algorithm: str = "HS256"
    access_exp_minutes: int = 60
    refresh_exp_minutes: int = 60 * 24 * 30
    leeway_seconds: int = 10
    require_tenant_claim: bool = True

@dataclass(frozen=True, slots=True)
class TenantsConfig:
    tenants_file: Path                 # path a tenants.yml
    tenant_header: str = "X-Tenant"
    default_tenant: str = "istanze"
    allowed_tenants_csv: str = ""      # "a,b,c"
    strict_whitelist: bool = False     # se True -> 403 se non in allowed

@dataclass(frozen=True, slots=True)
class CryptoConfig:
    encrypt_key: bytes  # 32 bytes
    
@dataclass(frozen=True, slots=True)
class DbDefaults:
    scheme: str = "postgresql+asyncpg"
    host: str = "localhost"
    port: int = 6432