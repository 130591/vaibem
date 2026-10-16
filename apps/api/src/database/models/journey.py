from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from apps.api.src.database.base import Base
from apps.api.src.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import DateTime, ForeignKey, Interval, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
  from apps.api.src.database.models.journey_event import JourneyEvent
  from apps.api.src.database.models.journey_location import JourneyLocation
  from apps.api.src.database.models.journey_status import JourneyStatus
  from apps.api.src.database.models.route import Route
  from apps.api.src.database.models.student import Student


class JourneyModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "journey"

  name: Mapped[str] = mapped_column(String(255), default="School Journey", nullable=False)
  student_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("student.id", ondelete="CASCADE"),
    nullable=False,
  )
  left_home: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  time_duration: Mapped[timedelta | None] = mapped_column(
    Interval, nullable=True
  )
  arrived_time: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  last_time_updated: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True), nullable=True
  )

  route_type: Mapped[str] = mapped_column(String(50), default="standard", nullable=False)
  status_id: Mapped[int | None] = mapped_column(
    ForeignKey("journey_status.id"),
    nullable=True,
  )
  route_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("route.id"),
    nullable=True,
  )


  student: Mapped[Student] = relationship(back_populates="journeys")
  status: Mapped[JourneyStatus] = relationship(back_populates="journeys")
  route: Mapped[Route] = relationship(back_populates="journeys")
  events: Mapped[list[JourneyEvent]] = relationship(
    back_populates="journey",
    cascade="all, delete-orphan",
  )
  locations: Mapped[list[JourneyLocation]] = relationship(
    back_populates="journey",
    cascade="all, delete-orphan",
  )


# Alias para compatibilidade com SQLAlchemy relationships e repositories
Journey = JourneyModel