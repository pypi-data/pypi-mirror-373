from __future__ import annotations
import json
from pathlib import Path
import os
from typing import Callable, Awaitable, Iterable, Optional
from fastapi import Depends, Request, HTTPException, status
from redis.asyncio import Redis

from .exceptions import TenantNotFound

from .config import TenantSettings
from .db import tenant_session
from .http import get_tenant_from_request
from .security import TenantSecurity, AuthConfig, TokenType
from .registry import TenantsRegistry

# ---------- Bootstrap da ENV (facoltativo ma comodo) ----------
# def bootstrap_from_env(
#     *,
#     driver: str = "postgresql+asyncpg",
#     default_mode: str = "development",
#     default_header: str = "X-Tenant",
#     default_tenant: str = "istanze",
# ) -> tuple[TenantSettings, TenantsRegistry, Redis, AuthConfig]:
#     TENANTS_FILE = os.getenv("TENANTS_FILE")
#     ACCESS_TOKEN_SECRET_FILE = os.getenv("ACCESS_TOKEN_SECRET_FILE")
#     REFRESH_TOKEN_SECRET_FILE = os.getenv("REFRESH_TOKEN_SECRET_FILE")
#     ENCRYPT_KEY_FILE = os.getenv("ENCRYPT_KEY_FILE")

#     DB_HOST = os.getenv("DATABASE_HOST", "localhost")
#     DB_PORT = int(os.getenv("DATABASE_PORT", "5432"))
#     ECHO_SQL = env_bool("ECHO_SQL", False)

#     REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
#     REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

#     base_dsn = build_base_dsn(DB_HOST, DB_PORT, driver=driver)
#     settings = TenantSettings(
#         MODE=default_mode, TENANT_HEADER=default_header, DEFAULT_TENANT=default_tenant,
#         ASYNC_DATABASE_URI=base_dsn, ECHO_SQL=ECHO_SQL, POOL_SIZE=10, APP_NAME_PREFIX="fastapi"
#     )

#     tenants_yaml = Path(TENANTS_FILE).read_text(encoding="utf-8")
#     tenants_aead_key = read_secret_file(ENCRYPT_KEY_FILE, required=False) or None
#     registry = TenantsRegistry.from_yaml_text(tenants_yaml, aead_key=tenants_aead_key)

#     access_secret = read_secret_file(ACCESS_TOKEN_SECRET_FILE)
#     refresh_secret = read_secret_file(REFRESH_TOKEN_SECRET_FILE)
#     auth_cfg = AuthConfig(
#         issuer="istanzeonline",
#         algorithm="HS256",
#         access_secret=access_secret,
#         refresh_secret=refresh_secret,
#         access_exp_minutes=60,
#         refresh_exp_minutes=60 * 24 * 30,
#         leeway_seconds=10,
#         require_tenant_claim=True,
#     )

#     redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)
#     return settings, registry, redis, auth_cfg

# ---------- Factory di dipendenze FastAPI ----------
class FastAPIDeps:
    def __init__(self, *, settings: TenantSettings, registry: TenantsRegistry, redis: Redis, auth_cfg: AuthConfig, enforce_membership: bool = False):
        self.settings = settings
        self.registry = registry
        self.redis = redis
        self.auth_cfg = auth_cfg
        self.enforce_membership = enforce_membership

    # dipendenza: tenant
    async def dep_tenant(self, request: Request) -> str:
        tenant = get_tenant_from_request(request, self.settings)
        if not tenant:
            raise TenantNotFound(tenant)
        return tenant

    # dipendenza: sessione DB per-tenant
    async def dep_db_session(self, tenant: str = Depends(dep_tenant)):
        async with tenant_session(self.settings, tenant, self.registry) as s:
            yield s

    # helper: ottieni security per-tenant
    def get_security(self, tenant: str) -> TenantSecurity:
        return TenantSecurity(redis=self.redis, tenant=tenant, cfg=self.auth_cfg)

    async def dep_current_user(
        self,
        request: Request,
        required_roles: Optional[Iterable[str]] = None,
        require_active: bool = True,
    ) -> dict:
        """
        Legge Authorization: Bearer, verifica ACCESS con TenantSecurity,
        poi carica i dati utente dalla sessione Redis (userinfo).
        Opzionalmente verifica 'is_active' e i 'required_roles'.
        Ritorna il dict utente (es. UtenteRead.model_dump()).

        Chiavi Redis come da tua convenzione:
            tenant:{tenant}:user:{user_id}:userinfo
        """
        # 1) token
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Bearer token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = auth.removeprefix("Bearer ").strip()

        # 2) tenant + security
        tenant = await self.dep_tenant(request)
        sec: TenantSecurity = self.get_security(tenant)

        # 3) verify ACCESS (membership jti opzionale, di solito no qui)
        payload = await sec.verify_token(token, TokenType.ACCESS, enforce_membership=False)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing user id",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 4) carica sessione utente da Redis
        raw = await sec.redis.get(sec.userinfo_key(user_id))
        if not raw:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sessione scaduta",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")

        try:
            user_data = json.loads(raw)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Dati sessione non validi",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 5) active + roles
        if require_active and not user_data.get("is_active", True):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Utente non attivo")

        if required_roles:
            if not user_data.get("is_superuser", False):
                roles = set(user_data.get("roles") or [])
                if not roles.intersection(set(required_roles)):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Richiesto uno dei ruoli: {list(required_roles)}",
                    )

        return user_data



    # dipendenza: current user da Bearer
    # async def dep_current_userxxxxxxxxx(self, request: Request, tenant: str = Depends(dep_tenant)) -> dict:
    #     auth = request.headers.get("Authorization", "")
    #     if not auth.startswith("Bearer "):
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    #     token = auth.removeprefix("Bearer ").strip()
    #     sec = self.get_security(tenant)
    #     # decode e, se vuoi, membership sugli access
    #     payload = sec.decode_token(token, expected_type=TokenType.ACCESS)
    #     if self.enforce_membership:
    #         await sec.verify_token(token, TokenType.ACCESS, enforce_membership=True)
    #     return {"userid": payload["sub"], "claims": payload, "tenant": tenant}
    
