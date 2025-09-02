from __future__ import annotations
import base64, secrets
from dataclasses import dataclass
from typing import Optional, Iterable
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

def _b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "===")

def _is_b64url(s: str) -> bool:
    return all(c.isalnum() or c in "-_" for c in s)

def coerce_key_to_bytes(key: str | bytes) -> bytes:
    if isinstance(key, bytes):
        return key
    k = key.strip()
    if _is_b64url(k):
        try:
            return _b64url_decode(k)
        except Exception:
            pass
    return bytes.fromhex(k)

@dataclass(frozen=True)
class AeadBox:
    key: bytes  # 16|24|32

    @staticmethod
    def from_text(key: str | bytes) -> "AeadBox":
        raw = coerce_key_to_bytes(key)
        if len(raw) not in (16, 24, 32):
            raise ValueError("AES key must be 16/24/32 bytes")
        return AeadBox(raw)

    def encrypt(self, plaintext: bytes, aad: Optional[bytes] = None) -> bytes:
        nonce = secrets.token_bytes(12)
        ct = AESGCM(self.key).encrypt(nonce, plaintext, aad)
        return nonce + ct

    def decrypt(self, payload: bytes, aad: Optional[bytes] = None) -> bytes:
        if len(payload) < 13:
            raise ValueError("ciphertext too short")
        nonce, ct = payload[:12], payload[12:]
        return AESGCM(self.key).decrypt(nonce, ct, aad)

# ---- supporto registro {$enc:aesgcm, v:1, n:..., ct:..., [aad: "..."]}

def decrypt_field(
    value: str | dict,
    box: AeadBox,
    *,
    aad: Optional[bytes] = None,
    field: Optional[str] = None,
    tenant: Optional[str] = None,
    try_common: bool = True,
) -> str:
    """
    Decifra un campo del registry.
    - Se 'value' è stringa, la restituisce.
    - Se è dict {$enc:'aesgcm', v, n, ct, [aad]}, usa AAD esplicita oppure tenta
      una lista di AAD candidate (field, v, tenant) per compat con versioni precedenti.
    """
    if isinstance(value, str):
        return value

    if not (isinstance(value, dict) and value.get("$enc") == "aesgcm"):
        raise ValueError("Formato campo non supportato per decrypt_field")

    v = value.get("v")
    nonce = _b64url_decode(value["n"])
    ct = _b64url_decode(value["ct"])
    payload = nonce + ct

    # 1) se l'aad è nel dict, usala subito
    if "aad" in value and value["aad"] is not None:
        cand = value["aad"]
        aad_bytes = cand.encode("utf-8") if isinstance(cand, str) else cand
        return box.decrypt(payload, aad=aad_bytes).decode("utf-8")

    # 2) costruisci lista di candidate
    candidates: list[Optional[bytes]] = []
    if aad is not None:
        candidates.append(aad)
    if try_common:
        if field:
            candidates += [field.encode("utf-8")]
        if isinstance(v, int):
            candidates += [f"v={v}".encode("utf-8"), f"aesgcm|v={v}".encode("utf-8")]
        if tenant and field and isinstance(v, int):
            candidates += [f"{tenant}|{field}|v={v}".encode("utf-8")]
        # ultima spiaggia: nessuna AAD
        candidates.append(None)

    last_err: Optional[Exception] = None
    for cand in candidates:
        try:
            return box.decrypt(payload, aad=cand).decode("utf-8")
        except InvalidTag as e:
            last_err = e
            continue

    raise InvalidTag(f"Impossibile decifrare: chiave o AAD non corretti. Tentativi: {len(candidates)}") from last_err
