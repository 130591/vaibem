from __future__ import annotations

from uuid import UUID

from apps.api.src.database.models.guardian_device import GuardianDevice as GuardianDeviceModel
from apps.api.src.database.repositories.base_repository import BaseRepository
from apps.api.src.domains.device import GuardianDevice as GuardianDeviceDomain
from sqlalchemy import select


class DeviceRepository(BaseRepository[GuardianDeviceModel, GuardianDeviceDomain]):
  model_cls = GuardianDeviceModel
  entity_name = "GuardianDevice"

  def _to_domain(self, model: GuardianDeviceModel) -> GuardianDeviceDomain:
    return GuardianDeviceDomain(
      id=model.id,
      guardian_id=model.guardian_id,
      device_token=model.device_token,
      platform=model.platform,
      last_active_at=model.last_active_at,
    )

  async def find_by_token(self, device_token: str) -> GuardianDeviceDomain | None:
    async with self._translate_db_errors(device_token=device_token):
      stmt = select(GuardianDeviceModel).where(
        GuardianDeviceModel.device_token == device_token.strip()
      )
      result = await self.session.execute(stmt)
      model = result.scalar_one_or_none()
      return self._to_domain(model) if model is not None else None

  async def find_by_guardian_id(self, guardian_id: UUID) -> list[GuardianDeviceDomain]:
    async with self._translate_db_errors(guardian_id=str(guardian_id)):
      stmt = select(GuardianDeviceModel).where(GuardianDeviceModel.guardian_id == guardian_id)
      result = await self.session.execute(stmt)
      models = result.scalars().all()
      return [self._to_domain(m) for m in models]

  async def save(self, device: GuardianDeviceDomain) -> None:
    async with self._translate_db_errors(device_id=str(device.id)):
      model = await self.session.get(GuardianDeviceModel, device.id)
      if model is None:
        model = GuardianDeviceModel(
          id=device.id,
          guardian_id=device.guardian_id,
          device_token=device.device_token,
          platform=device.platform,
          last_active_at=device.last_active_at,
        )
        self.session.add(model)
      else:
        model.guardian_id = device.guardian_id
        model.device_token = device.device_token
        model.platform = device.platform
        model.last_active_at = device.last_active_at

      await self.session.commit()
