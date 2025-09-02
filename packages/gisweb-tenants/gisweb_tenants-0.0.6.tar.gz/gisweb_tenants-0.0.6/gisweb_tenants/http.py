from __future__ import annotations
from fastapi import Request
from .config import TenantSettings

def get_tenant_from_request(request: Request, settings: TenantSettings) -> str:
    tenant = request.headers.get(settings.TENANT_HEADER)
    if tenant:
        return tenant.strip().lower()
    t = request.path_params.get("tenant") if hasattr(request, "path_params") else None
    return (t or settings.DEFAULT_TENANT).strip().lower()
