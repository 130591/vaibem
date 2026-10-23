import hashlib
import secrets


def generate_invitation_token() -> tuple[str, str]:
  """Retorna (raw_token, token_hash)."""
  raw = secrets.token_urlsafe(32)
  hashed = hash_token(raw)
  return raw, hashed


def hash_token(raw_token: str) -> str:
  """Calcula o SHA-256 de um token para busca indexada."""
  return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
