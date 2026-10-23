from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from apps.api.src.database.base import Base
from apps.api.src.database.mixins import UUIDPrimaryKeyMixin
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
  from apps.api.src.database.models.journey import Journey


class JourneyEvent(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "journey_events"

  journey_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("journey.id", ondelete="CASCADE"),
    nullable=False,
  )

  event_type: Mapped[str] = mapped_column(String(50), nullable=False)
  message: Mapped[str | None] = mapped_column(String(255), nullable=True)
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False,
  )

  journey: Mapped[Journey] = relationship(back_populates="events")
