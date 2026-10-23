from __future__ import annotations

from uuid import UUID

from apps.api.src.database.models.guardian import Guardian
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ProfileRepository:
  def __init__(self, session: AsyncSession) -> None:
    self.session = session

  async def find_guardian_by_email(self, email: str) -> Guardian | None:
    stmt = select(Guardian).where(Guardian.email == email)
    result = await self.session.execute(stmt)
    return result.scalar_one_or_none()

  async def find_guardian_by_phone(self, phone: str) -> Guardian | None:
    stmt = select(Guardian).where(Guardian.phone == phone)
    result = await self.session.execute(stmt)
    return result.scalar_one_or_none()

  async def get_by_id(self, guardian_id: UUID) -> Guardian | None:
    stmt = select(Guardian).where(Guardian.id == guardian_id)
    result = await self.session.execute(stmt)
    return result.scalar_one_or_none()

  async def save_guardian(self, guardian: Guardian) -> Guardian:
    self.session.add(guardian)
    await self.session.flush()
    return guardian
