# gisweb_tenants/runtime_config.py
from __future__ import annotations
from typing import Any, Optional, Dict
from fastapi import Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
import json
import time

from .config import CryptoConfig
from .crypto import is_encrypted, decrypt_secret

class TenantRuntimeConfig(BaseModel):
    # esempi, metti i tuoi
    feature_x_enabled: bool = False
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    timeout_seconds: int = 30
    
# gisweb_tenants/runtime_config.py (continua)
class TenantConfigProvider:
    def __init__(self, *, crypto: CryptoConfig | None = None,
                 redis: Redis | None = None, ttl_seconds: int = 60,
                 cache_prefix: str = "tenants:cfg"):
        self.crypto = crypto
        self.redis = redis
        self.ttl = ttl_seconds
        self.prefix = cache_prefix
        self._mem: Dict[str, tuple[float, dict]] = {}  # tenant -> (expires_at, data)

    def _cache_key(self, tenant: str) -> str:
        return f"{self.prefix}:{tenant}"

    async def _get_cached(self, tenant: str) -> dict | None:
        # Redis
        if self.redis:
            raw = await self.redis.get(self._cache_key(tenant))
            if raw:
                return json.loads(raw)
        # In-memory
        now = time.time()
        item = self._mem.get(tenant)
        if item and item[0] > now:
            return item[1]
        return None

    async def _set_cached(self, tenant: str, data: dict):
        if self.redis:
            await self.redis.set(self._cache_key(tenant), json.dumps(data), ex=self.ttl)
        self._mem[tenant] = (time.time() + self.ttl, data)

    async def _load_from_db_kv(self, session: AsyncSession, tenant: str) -> dict:
        """
        Variante key-value: SELECT key, value, is_secret FROM app_config WHERE tenant=:tenant
        'value' può essere testo o json. Se is_secret ed è cifrato, decripta.
        """
        rows = await session.execute(
            # adatta al tuo ORM; qui SQL testuale per chiarezza
            # key TEXT, value JSONB/TEXT, is_secret BOOL
            # NB: se usi ORM, fai model e query ORM.
            """SELECT key, value, is_secret FROM app_config WHERE tenant = :t""",
            {"t": tenant},
        )
        cfg: dict[str, Any] = {}
        for key, value, is_secret in rows.fetchall():
            val = value
            # se è stringa JSON, parse
            if isinstance(val, str):
                try:
                    val = json.loads(val)
                except Exception:
                    pass
            if is_secret:
                if is_encrypted(val):
                    if not self.crypto:
                        raise RuntimeError("Valore segreto cifrato ma CryptoConfig assente")
                    val = decrypt_secret(val, f"{tenant}|cfg|{key}", self.crypto)
            cfg[key] = val
        return cfg

    async def _load_from_db_json(self, session: AsyncSession, tenant: str) -> dict:
        """
        Variante JSON unico: SELECT data FROM app_config WHERE tenant=:t
        Dove 'data' è un JSON con eventuali campi cifrati.
        """
        row = await session.execute(
            """SELECT data FROM app_config WHERE tenant = :t""",
            {"t": tenant},
        )
        r = row.first()
        data = r[0] if r else {}
        data = dict(data or {})

        # opzionale: decripta i campi che sai essere segreti
        for key in ("webhook_secret",):
            v = data.get(key)
            if is_encrypted(v):
                if not self.crypto:
                    raise RuntimeError("Valore segreto cifrato ma CryptoConfig assente")
                data[key] = decrypt_secret(v, f"{tenant}|cfg|{key}", self.crypto)
        return data

    async def get(self, tenant: str, session: AsyncSession) -> TenantRuntimeConfig:
        # 1) cache
        cached = await self._get_cached(tenant)
        if cached is not None:
            return TenantRuntimeConfig(**cached)

        # 2) carica dal DB (scegli KV o JSON)
        data = await self._load_from_db_kv(session, tenant)
        # data = await self._load_from_db_json(session, tenant)

        # 3) merge con default tipizzati
        cfg = TenantRuntimeConfig(**data)

        # 4) cache
        await self._set_cached(tenant, cfg.model_dump())
        return cfg
    


    # async def get_tenant_config(
    #     session: AsyncSession = Depends(get_session),
    #     tenant: str = Depends(get_tenant_name),
    # ) -> TenantRuntimeConfig:
    #     if not _provider:
    #         raise RuntimeError("TenantConfigProvider non inizializzato")
    #     return await _provider.get(tenant, session)