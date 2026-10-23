from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(slots=True, kw_only=True)
class Guardian:
  id: UUID
  account_id: UUID
  email: str
  name: str
  phone: str

  @classmethod
  def create(
    cls,
    *,
    account_id: UUID,
    email: str = "",
    full_name: str,
    phone: str,
  ) -> Guardian:
    name = full_name.strip()
    normalized_phone = phone.strip()

    if not name:
      raise ValueError("Nome obrigatório.")

    if not normalized_phone:
      raise ValueError("Telefone obrigatório.")

    return cls(
      id=uuid4(),
      account_id=account_id,
      email=email,
      name=name,
      phone=normalized_phone,
    )
