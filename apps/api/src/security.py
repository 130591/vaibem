from __future__ import annotations

import hashlib
import os
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from apps.api.src.config import settings


def hash_password(password: str) -> str:
  salt = os.urandom(16)
  derived = hashlib.scrypt(
    password.encode("utf-8"),
    salt=salt,
    n=16384,
    r=8,
    p=1,
  )
  return f"{salt.hex()}:{derived.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
  try:
    salt_hex, hash_hex = stored_hash.split(":")
    salt = bytes.fromhex(salt_hex)
    derived = hashlib.scrypt(
      plain_password.encode("utf-8"),
      salt=salt,
      n=16384,
      r=8,
      p=1,
    )
    return secrets.compare_digest(derived.hex(), hash_hex)
  except Exception:  # noqa: BLE001
    return False


def create_access_token(account_id: str, guardian_id: str | None = None) -> str:
  now = datetime.now(UTC)
  payload = {
    "sub": str(account_id),
    "type": "access",
    "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
    "iat": now,
  }
  if guardian_id:
    payload["guardian_id"] = str(guardian_id)
  return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(account_id: str) -> str:
  now = datetime.now(UTC)
  payload = {
    "sub": str(account_id),
    "type": "refresh",
    "exp": now + timedelta(days=settings.jwt_refresh_token_expire_days),
    "iat": now,
  }
  return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
  return jwt.decode(
    token,
    settings.jwt_secret_key,
    algorithms=[settings.jwt_algorithm],
  )
