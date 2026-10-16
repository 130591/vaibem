from __future__ import annotations

import uuid
from datetime import time
from typing import TYPE_CHECKING

from apps.api.src.database.base import Base
from apps.api.src.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from geoalchemy2 import Geometry
from sqlalchemy import Boolean, ForeignKey, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from apps.api.src.database.models.student import Student


class Routine(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "routine"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student.id", ondelete="CASCADE"),
        unique=True,  # 1:1 no MVP (garante integridade rápida)
        nullable=False,
    )
    home_address: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Ponto espacial no PostGIS para geofencing residencial:
    home_point: Mapped[str | None] = mapped_column(
        Geometry("POINT", srid=4326), nullable=True
    )
    
    habitual_departure: Mapped[time] = mapped_column(Time, nullable=False)
    habitual_return: Mapped[time] = mapped_column(Time, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    student: Mapped[Student] = relationship(back_populates="routine")