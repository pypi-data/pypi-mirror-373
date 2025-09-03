from __future__ import annotations
from typing import Dict, AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

from .config import TenantSettings
from .registry import TenantsRegistry, TenantRecord

_engine_registry: Dict[str, AsyncEngine] = {}

def _build_connect_args(settings: TenantSettings, tenant: str) -> dict:
    app_name = f"{settings.APP_NAME_PREFIX}:{tenant}"
    driver = settings.drivername()
    if "+asyncpg" in driver:
        return {"server_settings": {"application_name": app_name}}
    return {"application_name": app_name}

def _engine_args(settings: TenantSettings) -> dict:
    testing = settings.MODE == "testing"
    return {
        "echo": settings.ECHO_SQL,
        "pool_pre_ping": True,
        "pool_size": None if testing else settings.POOL_SIZE,
        "max_overflow": 64 if not testing else 0,
        "poolclass": NullPool if testing else None,
    }

def get_engine(settings: TenantSettings, tenant: str, registry: TenantsRegistry | None = None) -> AsyncEngine:
    
    key = f"{tenant}"
    eng = _engine_registry.get(key)
    if eng is not None:
        return eng

    url = registry.build_dsn(settings.ASYNC_DATABASE_URI, tenant)
    print (str(url))
    connect_args = _build_connect_args(settings, tenant)
    args = {k: v for k, v in _engine_args(settings).items() if v is not None}
    eng = create_async_engine(url, connect_args=connect_args, **args)
    _engine_registry[key] = eng
    return eng

def get_sessionmaker(settings: TenantSettings, tenant: str, registry: TenantsRegistry | None = None) -> async_sessionmaker[AsyncSession]:
    engine = get_engine(settings, tenant, registry)
    return async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def tenant_session(settings: TenantSettings, tenant: str, registry: TenantsRegistry | None = None) -> AsyncIterator[AsyncSession]:
    sm = get_sessionmaker(settings, tenant, registry)
    async with sm() as session:
        yield session


# ------------------------------
# 🔻 gestione shutdown/cleanup
# ------------------------------

async def dispose_engine(tenant: str) -> bool:
    """
    Chiude e rimuove l'engine del tenant (se esiste).
    Ritorna True se c'era qualcosa da chiudere.
    """
    eng = _engine_registry.pop(tenant, None)
    if not eng:
        return False
    try:
        await eng.dispose()
    except Exception:
        # non alziamo in shutdown
        return False
    return True

async def dispose_all_engines() -> dict:
    """
    Chiude tutti gli AsyncEngine creati da questo modulo e svuota la registry.
    Idempotente e sicuro da chiamare più volte.
    Ritorna un report {"closed": [...], "failed": [...]}.
    """
    closed, failed = [], []
    # copia chiavi per evitare modifiche durante l'iterazione
    keys = list(_engine_registry.keys())
    for tenant in keys:
        eng = _engine_registry.pop(tenant, None)
        if not eng:
            continue
        try:
            await eng.dispose()
            closed.append(tenant)
        except Exception:
            failed.append(tenant)
    return {"closed": closed, "failed": failed}