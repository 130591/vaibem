from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

ALLOWED_PLATFORMS = {"ios", "android", "web"}


@dataclass(slots=True, kw_only=True)
class GuardianDevice:
  id: UUID
  guardian_id: UUID
  device_token: str
  platform: str
  last_active_at: datetime

  @classmethod
  def create(
    cls,
    *,
    guardian_id: UUID,
    device_token: str,
    platform: str,
    now: datetime | None = None,
  ) -> GuardianDevice:
    clean_token = device_token.strip()
    clean_platform = platform.strip().lower()

    if not clean_token:
      raise ValueError("O token do dispositivo não pode ser vazio.")

    if clean_platform not in ALLOWED_PLATFORMS:
      raise ValueError(
        f"Plataforma inválida: '{platform}'. Permitidas: {', '.join(sorted(ALLOWED_PLATFORMS))}."
      )

    return cls(
      id=uuid4(),
      guardian_id=guardian_id,
      device_token=clean_token,
      platform=clean_platform,
      last_active_at=now or datetime.now(UTC),
    )

  def update_activity(
    self,
    platform: str | None = None,
    now: datetime | None = None,
  ) -> None:
    if platform:
      clean_platform = platform.strip().lower()
      if clean_platform in ALLOWED_PLATFORMS:
        self.platform = clean_platform
    self.last_active_at = now or datetime.now(UTC)
