from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from apps.api.src.domains.exceptions import (
  AlreadyUsedInviteError,
  InvalidExpiredError,
)


class DeviceStatus(StrEnum):
  ONLINE = "online"
  OFFLINE = "offline"


now = datetime.now(UTC)


@dataclass(slots=True, kw_only=True)
class Guardian:
  email: str
  name: str
  phone: str


@dataclass(slots=True, kw_only=True)
class Student:
  name: str
  grade: str
  device_status: DeviceStatus


@dataclass(frozen=True, slots=True, kw_only=True)
class Invite:
  id: UUID
  school_id: UUID
  expires_at: datetime
  status: str = "pending"
  accepted_at: datetime | None = None

  def is_expired(self, now: datetime | None = None) -> bool:
    current_time = now or datetime.now(UTC)
    return current_time >= self.expires_at

  def is_used(self) -> bool:
    return self.status == "accepted" or self.accepted_at is not None

  def accept(self, now: datetime) -> Invite:
    if self.status != "pending":
      raise AlreadyUsedInviteError()

    if self.is_expired(now=now):
      raise InvalidExpiredError()

    return Invite(
      id=self.id,
      school_id=self.school_id,
      expires_at=self.expires_at,
      status="accepted",
      accepted_at=now,
    )
