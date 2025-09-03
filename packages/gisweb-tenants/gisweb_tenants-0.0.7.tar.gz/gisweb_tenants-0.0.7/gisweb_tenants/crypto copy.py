# gisweb_tenants/crypto.py
from __future__ import annotations
import base64, secrets
from typing import Any, Dict
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def _b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "===")

def _is_b64url(s: str) -> bool:
    return all(c.isalnum() or c in "-_" for c in s)

def coerce_key_to_bytes(key: str | bytes) -> bytes:
    import pdb;pdb.set_trace()
    if isinstance(key, bytes):
        return key
    k = key.strip()
    if _is_b64url(k):
        try:
            return _b64url_decode(k)
        except Exception:
            pass
    return bytes.fromhex(k)

def encrypt_secret(plain: str, aad: str, encrypt_key: bytes, v: int = 1) -> Dict[str, Any]:
    _aes = AESGCM(encrypt_key)
    nonce = secrets.token_bytes(12)
    ct = _aes.encrypt(nonce, plain.encode(), aad.encode())
    return {
        "$enc": "aesgcm",
        "v": v,
        "n": base64.urlsafe_b64encode(nonce).decode().rstrip("="),
        "ct": base64.urlsafe_b64encode(ct).decode().rstrip("="),
    }

def is_encrypted(x: Any) -> bool:
    return isinstance(x, dict) and x.get("$enc") == "aesgcm" and "n" in x and "ct" in x

def decrypt_secret(enc: Dict[str, Any], aad: str, encrypt_key: bytes) -> str:
    nonce = base64.urlsafe_b64decode(enc["n"] + "===")
    ct = base64.urlsafe_b64decode(enc["ct"] + "===")
    _aes = AESGCM(encrypt_key)
    pt = _aes.decrypt(nonce, ct, aad.encode())
    return pt.decode()


def decode_key(s: str) -> bytes:
    s = (s or "").strip()
    # 1) base64url
    try:
        raw = base64.urlsafe_b64decode(s + "===")
        if len(raw) == 32:
            return raw
    except Exception:
        pass
    # 2) hex
    try:
        raw = bytes.fromhex(s)
        if len(raw) == 32:
            return raw
    except Exception:
        pass
    raise ValueError("ENCRYPT_KEY deve essere 32 bytes (base64url o hex)")