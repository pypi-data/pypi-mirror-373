"""加密/哈希辅助（防御用途）"""
from __future__ import annotations
import hashlib, secrets, hmac
from typing import Tuple, Optional

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    _HAS_CRYPTO = True
except Exception:
    _HAS_CRYPTO = False

def gen_salt(n: int = 16) -> bytes:
    return secrets.token_bytes(n)

def pbkdf2_derive(password: str, salt: Optional[bytes] = None, iterations: int = 200_000, dklen: int = 32, hash_name: str = 'sha256') -> Tuple[bytes, bytes]:
    if salt is None:
        salt = gen_salt(16)
    key = hashlib.pbkdf2_hmac(hash_name, password.encode('utf-8'), salt, iterations, dklen)
    return key, salt

def hmac_hex(key: bytes, message: bytes, hash_name: str = 'sha256') -> str:
    mac = hmac.new(key, message, getattr(hashlib, hash_name))
    return mac.hexdigest()

def hash_file(path: str, algo: str = 'sha256') -> str:
    h = getattr(hashlib, algo)()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def aes_gcm_encrypt(plaintext: bytes, key: bytes) -> dict:
    if not _HAS_CRYPTO:
        raise RuntimeError('cryptography 库不可用')
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)
    ct = aesgcm.encrypt(nonce, plaintext, None)
    return {"nonce": nonce.hex(), "ciphertext": ct.hex()}

def aes_gcm_decrypt(nonce_hex: str, ct_hex: str, key: bytes) -> bytes:
    if not _HAS_CRYPTO:
        raise RuntimeError('cryptography 库不可用')
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(bytes.fromhex(nonce_hex), bytes.fromhex(ct_hex), None)
