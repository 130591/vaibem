from __future__ import annotations

from typing import TYPE_CHECKING

from apps.api.src.database.base import Base
from apps.api.src.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from geoalchemy2 import Geometry
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
  from apps.api.src.database.models.journey import Journey


class Route(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "route"

  origin_point: Mapped[str] = mapped_column(
    Geometry("POINT", srid=4326), nullable=False
  )
  destination_point: Mapped[str] = mapped_column(
    Geometry("POINT", srid=4326), nullable=False
  )
  # Traçado completo da rota.
  geometry: Mapped[str | None] = mapped_column(
    Geometry("LINESTRING", srid=4326), nullable=True
  )

  journeys: Mapped[list[Journey]] = relationship(back_populates="route")