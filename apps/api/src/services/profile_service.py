from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from apps.api.src.constant import InviteStatus
from apps.api.src.database.models import Account, Guardian, GuardianStudent
from apps.api.src.domains.exceptions import (
  AccountAlreadyExistsError,
  AlreadyUsedInviteError,
  InvalidExpiredError,
  InvalidInviteError,
  InviteNotFoundException,
)
from apps.api.src.security import create_access_token, create_refresh_token

if TYPE_CHECKING:
  from apps.api.src.api.graphql.mutations.account import RegisterGuardianInfo
  from apps.api.src.database.repositories.invite_school_repository import (
    InviteSchoolRepository,
  )
  from apps.api.src.database.repositories.profile_repository import ProfileRepository
  from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(slots=True)
class Profile:
  id: UUID
  name: str
  email: str


@dataclass(slots=True)
class AuthTokens:
  access_token: str
  refresh_token: str


class ProfileService:
  def __init__(
    self,
    profile_repository: ProfileRepository | None = None,
    invite_repository: InviteSchoolRepository | None = None,
    session: AsyncSession | None = None,
  ) -> None:
    self.profile_repository = profile_repository
    self.invite_repository = invite_repository
    self.session = session

  @staticmethod
  def calculate_hash(raw_token: str) -> str:
    return hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()

  async def get_profile_by_id(self, guardian_id: UUID) -> Profile | None:
    if self.profile_repository is None:
      return None
    guardian = await self.profile_repository.get_by_id(guardian_id)
    if guardian is None:
      return None
    return Profile(id=guardian.id, name=guardian.name, email=guardian.email)

  async def register(self, register_guardian: RegisterGuardianInfo) -> AuthTokens:
    if self.invite_repository is None or self.profile_repository is None:
      raise RuntimeError("Repositórios não configurados no ProfileService.")

    token_hash = self.calculate_hash(register_guardian.token)
    invite = await self.invite_repository.get_by_token_hash(token_hash)

    if invite is None:
      raise InviteNotFoundException()

    if invite.status == InviteStatus.ACCEPTED or invite.status == "accepted":
      raise AlreadyUsedInviteError()

    if invite.is_expired():
      raise InvalidExpiredError()

    if invite.status != InviteStatus.PENDING and invite.status != "pending":
      raise InvalidInviteError(f"Convite inválido (status: {invite.status}).")

    existing_by_email = await self.profile_repository.find_guardian_by_email(invite.guardian_email)
    if existing_by_email is not None:
      raise AccountAlreadyExistsError("Responsável já possui conta cadastrada.")

    existing_by_phone = await self.profile_repository.find_guardian_by_phone(
      register_guardian.phone.strip()
    )
    if existing_by_phone is not None:
      raise AccountAlreadyExistsError("Telefone já cadastrado.")

    account = Account(
      id=uuid4(),
      address="",
      alarm_enabled=True,
    )

    guardian = Guardian(
      id=uuid4(),
      account_id=account.id,
      email=invite.guardian_email,
      name=register_guardian.name,
      phone=register_guardian.phone.strip(),
    )

    link = GuardianStudent(
      id=uuid4(),
      guardian_id=guardian.id,
      student_id=invite.student_id,
    )

    invite.status = "accepted"
    invite.updated_at = datetime.now(UTC)

    if self.session is not None:
      self.session.add_all([account, guardian, link, invite])
      await self.session.commit()

    access_token = create_access_token(
      account_id=str(account.id),
      guardian_id=str(guardian.id),
    )
    refresh_token = create_refresh_token(
      account_id=str(account.id),
    )

    return AuthTokens(access_token=access_token, refresh_token=refresh_token)
