from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from apps.api.src.constant import InviteStatus
from apps.api.src.domains.account import Account
from apps.api.src.domains.exceptions import (
  AlreadyUsedInviteError,
  InvalidExpiredError,
  InvalidInviteError,
  InviteNotFoundException,
)
from apps.api.src.domains.guardian import Guardian

if TYPE_CHECKING:
  from apps.api.src.database.models.invitation import SchoolInvitation
  from apps.api.src.database.repositories.invite_school_repository import (
    InviteSchoolRepository,
  )


class InviteService:
  def __init__(
    self,
    invite_repository: InviteSchoolRepository,
    guardian_repository: Any = None,
  ) -> None:
    self.invite_repository = invite_repository
    self.guardian_repository = guardian_repository

  @staticmethod
  def calculate_hash(raw_token: str) -> str:
    return hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()

  async def validate(self, token: str) -> SchoolInvitation:
    token_hash = self.calculate_hash(token)
    entity = await self.invite_repository.get_by_token_hash(token_hash)

    if not entity:
      raise InviteNotFoundException()

    if entity.status == InviteStatus.ACCEPTED:
      raise AlreadyUsedInviteError()

    if entity.is_expired():
      raise InvalidExpiredError()

    if entity.status != InviteStatus.PENDING:
      raise InvalidInviteError(f"Convite inválido (status: {entity.status}).")

    return entity

  async def register(self, input: Any) -> None:
    invite = await self.invite_repository.get_by_token_hash(input.token)

    if invite is None:
      raise InviteNotFoundException()

    now = datetime.now(UTC)
    invite.accept(now=now)

    account = Account.create(
      email=invite.guardian_email,
      password_hash=self.password_hasher.hash(input.password),
      now=now,
    )

    guardian = Guardian.create(
      account_id=account.id,
      full_name=input.name,
      phone=input.phone,
    )

    invite.accept(datetime.now(UTC))

    async with self.unit_of_work:
      await self.account_repository.save(account)
      await self.guardian_repository.save(guardian)
      await self.invite_repository.save(invite)
