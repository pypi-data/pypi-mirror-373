from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import hashlib
import yaml
from sqlalchemy.engine import make_url, URL

from .crypto import AeadBox, decrypt_field  # usa la libreria che abbiamo già scritto

# version -> (entries, aead_key_bytes)
_REG_SNAPSHOTS: Dict[int, tuple[dict[str, "TenantRecord"], Optional[bytes]]] = {}

@lru_cache(maxsize=512)
def _resolve_triplet_cached(version: int, tenant: str) -> Tuple[str, str, str]:
    entries, aead_key = _REG_SNAPSHOTS[version]
    rec = entries.get(tenant)
    if rec is None:
        raise KeyError(f"Tenant '{tenant}' non trovato")
    cfg = rec.config or {}

    db_name = cfg.get("db_name") or tenant
    db_user = cfg.get("db_user")
    db_password = cfg.get("db_password")

    # decrypt se necessario: AAD fissa come da tuo encrypt.py
    if isinstance(db_user, dict) and db_user.get("$enc") == "aesgcm":
        if not aead_key:
            raise RuntimeError("Credenziali cifrate ma manca chiave AEAD")
        box = AeadBox.from_text(aead_key)
        db_user = decrypt_field(db_user, box, aad=f"{tenant}|db|user".encode())

    if isinstance(db_password, dict) and db_password.get("$enc") == "aesgcm":
        if not aead_key:
            raise RuntimeError("Credenziali cifrate ma manca chiave AEAD")
        box = AeadBox.from_text(aead_key)
        db_password = decrypt_field(db_password, box, aad=f"{tenant}|db|password".encode())

    if not db_user or not db_password:
        raise RuntimeError(f"Credenziali DB mancanti per tenant '{tenant}'")

    return db_name, db_user, db_password


@dataclass(frozen=True)
class TenantRecord:
    name: str
    config: Dict[str, Any]


class TenantsRegistry:
    """
    Registry con cache LRU per triplet decrittati.
    - Se istanzi da file, invalida automaticamente quando cambia l'mtime.
    - Se istanzi da testo, la "versione" deriva da hash(text + aead_key).
    """

    def __init__(self, *, text: Optional[str] = None, path: Optional[Path] = None, aead_key: Optional[str | bytes] = None):
        if not text and not path:
            raise ValueError("Serve 'text' YAML oppure 'path' al file del registry")
        self._text = text
        self._path = Path(path) if path else None
        self._aead_key: Optional[bytes] = (aead_key.encode() if isinstance(aead_key, str) else aead_key) if aead_key else None
        self._version: Optional[int] = None  # int(mtime) oppure hash del testo
        self._ensure_loaded()

    # --------- API pubblico

    def exists(self, tenant: str) -> bool:
        self._ensure_loaded()
        entries, _ = _REG_SNAPSHOTS[self._version]  # type: ignore[arg-type]
        return tenant.strip().lower() in entries

    def get(self, tenant: str) -> TenantRecord:
        self._ensure_loaded()
        entries, _ = _REG_SNAPSHOTS[self._version]  # type: ignore[arg-type]
        rec = entries.get(tenant.strip().lower())
        if not rec:
            raise KeyError(f"Tenant '{tenant}' non trovato")
        return rec

    def resolve_triplet(self, tenant: str) -> Tuple[str, str, str]:
        self._ensure_loaded()
        return _resolve_triplet_cached(self._version, tenant.strip().lower())  # type: ignore[arg-type]

    def build_dsn(self, base_dsn: str, tenant: str) -> str:
        """
        Costruisce un DSN per il tenant a partire da un DSN base (driver/host/port).
        Esempio base_dsn: "postgresql+asyncpg://@localhost:6432/postgres"
        """
        db_name, db_user, db_password = self.resolve_triplet(tenant)
        base: URL = make_url(base_dsn)
        url = base.set(database=db_name, username=db_user, password=db_password)
        return url

    @property
    def names(self) -> list[str]:
        self._ensure_loaded()
        entries, _ = _REG_SNAPSHOTS[self._version]  # type: ignore[arg-type]
        return list(entries.keys())

    def invalidate(self) -> None:
        """Forza ricarica alla prossima chiamata."""
        self._version = None

    # --------- privato

    def _ensure_loaded(self) -> None:
        # Se da file: versione = int(mtime). Se da testo: hash(text + aead_key)
        if self._path:
            try:
                mtime = int(self._path.stat().st_mtime)
            except FileNotFoundError:
                raise RuntimeError(f"Registry file non trovato: {self._path}")
            if self._version != mtime:
                text = self._path.read_text(encoding="utf-8")
                self._load_into_snapshots(text, version=mtime)
                self._version = mtime
        else:
            # versione derivata da hash
            text = self._text or ""
            h = hashlib.sha1()
            h.update(text.encode("utf-8"))
            if self._aead_key:
                h.update(self._aead_key)
            ver = int.from_bytes(h.digest()[:4], "big")  # un int stabile a 32 bit
            if self._version != ver:
                self._load_into_snapshots(text, version=ver)
                self._version = ver

    def _load_into_snapshots(self, yaml_text: str, *, version: int) -> None:
        data = yaml.safe_load(yaml_text) or {}
        tenants = data.get("tenants") or {}
        entries: dict[str, TenantRecord] = {}
        for name, cfg in tenants.items():
            k = str(name).strip().lower()
            entries[k] = TenantRecord(name=k, config=cfg or {})
        _REG_SNAPSHOTS[version] = (entries, self._aead_key)
