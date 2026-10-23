from __future__ import annotations

from uuid import UUID

from apps.api.src.database.models.guardian import Guardian as GuardianModel
from apps.api.src.database.repositories.base_repository import BaseRepository
from apps.api.src.domains.guardian import Guardian as GuardianDomain
from sqlalchemy import select


class GuardianRepository(BaseRepository[GuardianModel, GuardianDomain]):
  model_cls = GuardianModel
  entity_name = "Guardian"

  def _to_domain(self, model: GuardianModel) -> GuardianDomain:
    return GuardianDomain(
      id=model.id,
      account_id=model.account_id,
      email=model.email,
      name=model.name,
      phone=model.phone,
      notifications_enabled=model.notifications_enabled,
    )

  async def find_by_id(self, guardian_id: UUID) -> GuardianDomain | None:
    async with self._translate_db_errors(guardian_id=str(guardian_id)):
      stmt = select(GuardianModel).where(GuardianModel.id == guardian_id)
      result = await self.session.execute(stmt)
      model = result.scalar_one_or_none()
      return self._to_domain(model) if model is not None else None

  async def find_by_email(self, email: str) -> GuardianDomain | None:
    async with self._translate_db_errors(email=email):
      stmt = select(GuardianModel).where(GuardianModel.email == email)
      result = await self.session.execute(stmt)
      model = result.scalar_one_or_none()
      return self._to_domain(model) if model is not None else None

  async def find_by_phone(self, phone: str) -> GuardianDomain | None:
    async with self._translate_db_errors(phone=phone):
      stmt = select(GuardianModel).where(GuardianModel.phone == phone)
      result = await self.session.execute(stmt)
      model = result.scalar_one_or_none()
      return self._to_domain(model) if model is not None else None

  async def save(self, guardian: GuardianDomain) -> None:
    async with self._translate_db_errors(guardian_id=str(guardian.id)):
      model = await self.session.get(GuardianModel, guardian.id)
      if model is None:
        model = GuardianModel(
          id=guardian.id,
          account_id=guardian.account_id,
          email=guardian.email,
          name=guardian.name,
          phone=guardian.phone,
          notifications_enabled=guardian.notifications_enabled,
        )
        self.session.add(model)
      else:
        model.email = guardian.email
        model.name = guardian.name
        model.phone = guardian.phone
        model.notifications_enabled = guardian.notifications_enabled

      await self.session.commit()
