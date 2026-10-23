from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from apps.api.src.database.base import Base
from apps.api.src.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
  from apps.api.src.database.models.guardian import Guardian


class GuardianDevice(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "guardian_devices"

  guardian_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("guardian.id", ondelete="CASCADE"),
    nullable=False,
  )
  device_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
  platform: Mapped[str] = mapped_column(String(20), nullable=False)
  last_active_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False,
  )

  guardian: Mapped[Guardian] = relationship(back_populates="devices")
