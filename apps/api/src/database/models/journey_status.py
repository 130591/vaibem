from __future__ import annotations

from typing import TYPE_CHECKING

from apps.api.src.database.base import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
  from apps.api.src.database.models.journey import Journey


class JourneyStatus(Base):
  __tablename__ = "journey_status"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  status_lost_name: Mapped[str] = mapped_column(String(100), nullable=False)
  status_lost_message: Mapped[str] = mapped_column(String(255), nullable=False)

  journeys: Mapped[list[Journey]] = relationship(back_populates="status")