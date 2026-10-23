from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from apps.api.src.database.base import Base
from apps.api.src.database.mixins import UUIDPrimaryKeyMixin
from geoalchemy2 import Geometry
from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
  from apps.api.src.database.models.journey import Journey


class JourneyLocation(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "journey_location"

  journey_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("journey.id", ondelete="CASCADE"),
    nullable=False,
  )
  timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
  point: Mapped[str] = mapped_column(Geometry("POINT", srid=4326), nullable=False)
  accuracy: Mapped[float | None] = mapped_column(Numeric, nullable=True)

  journey: Mapped[Journey] = relationship(back_populates="locations")
