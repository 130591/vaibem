from __future__ import annotations

from uuid import UUID

from apps.api.src.database.repositories.device_repository import DeviceRepository
from apps.api.src.database.repositories.guardian_repository import GuardianRepository
from apps.api.src.domains.device import GuardianDevice
from apps.api.src.domains.exceptions import (
  GuardianNotFoundException,
  InvalidDeviceTokenException,
)


class DeviceService:
  def __init__(
    self,
    guardian_repository: GuardianRepository,
    device_repository: DeviceRepository,
  ) -> None:
    self.guardian_repository = guardian_repository
    self.device_repository = device_repository

  async def register_device(
    self,
    guardian_id: UUID,
    device_token: str,
    platform: str,
  ) -> bool:
    guardian = await self.guardian_repository.find_by_id(guardian_id)
    if guardian is None:
      raise GuardianNotFoundException()

    guardian.enable_notifications()
    await self.guardian_repository.save(guardian)

    clean_token = device_token.strip()
    clean_platform = platform.strip().lower()

    device = await self.device_repository.find_by_token(clean_token)
    if device is not None:
      device.update_activity(platform=clean_platform)
    else:
      try:
        device = GuardianDevice.create(
          guardian_id=guardian.id,
          device_token=clean_token,
          platform=clean_platform,
        )
      except ValueError as exc:
        raise InvalidDeviceTokenException(str(exc)) from exc

    await self.device_repository.save(device)
    return True
