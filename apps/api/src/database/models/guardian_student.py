from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from apps.api.src.database.base import Base
from apps.api.src.database.mixins import UUIDPrimaryKeyMixin
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
  from apps.api.src.database.models.guardian import Guardian
  from apps.api.src.database.models.student import Student


class GuardianStudent(UUIDPrimaryKeyMixin, Base):
  __tablename__ = "guardian_student"

  guardian_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("guardian.id", ondelete="CASCADE"),
    nullable=False,
  )
  student_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("student.id", ondelete="CASCADE"),
    nullable=False,
  )
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False,
  )

  guardian: Mapped[Guardian] = relationship(back_populates="guardian_students", overlaps="students")
  student: Mapped[Student] = relationship(back_populates="guardian_students", overlaps="students")

  __table_args__ = (UniqueConstraint("guardian_id", "student_id", name="uq_guardian_student"),)
