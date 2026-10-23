from __future__ import annotations

from typing import TYPE_CHECKING

from apps.api.src.database.base import Base
from apps.api.src.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
  from apps.api.src.database.models.guardian import Guardian
  from apps.api.src.database.models.guardian_student import GuardianStudent
  from apps.api.src.database.models.journey import Journey
  from apps.api.src.database.models.routine import Routine


class Student(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "student"

  name: Mapped[str] = mapped_column(String(255), nullable=False)
  grade: Mapped[str] = mapped_column(String(50), nullable=False)
  device_status: Mapped[str] = mapped_column(String(50), nullable=False)

  guardians: Mapped[list[Guardian]] = relationship(
    secondary="guardian_student",
    back_populates="students",
    overlaps="guardian,guardian_students,student,students",
  )
  guardian_students: Mapped[list[GuardianStudent]] = relationship(
    back_populates="student",
    cascade="all, delete-orphan",
    overlaps="guardians,students",
  )
  journeys: Mapped[list[Journey]] = relationship(
    back_populates="student",
    cascade="all, delete-orphan",
  )
  routine: Mapped[Routine | None] = relationship(
    back_populates="student", uselist=False, cascade="all, delete-orphan"
  )
