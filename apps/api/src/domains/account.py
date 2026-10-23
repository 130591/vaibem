from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(slots=True, kw_only=True)
class Account:
  id: UUID
  email: str
  password_hash: str

  @classmethod
  def create(
    cls,
    *,
    email: str,
    password_hash: str,
    now=None,
  ) -> Account:
    return cls(
      id=uuid4(),
      email=email,
      password_hash=password_hash,
    )
