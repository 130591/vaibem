from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from apps.api.src.database.base import Base
from apps.api.src.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
  from apps.api.src.database.models.account import Account
  from apps.api.src.database.models.guardian_device import GuardianDevice
  from apps.api.src.database.models.guardian_student import GuardianStudent
  from apps.api.src.database.models.student import Student


class Guardian(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "guardian"

  email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
  name: Mapped[str] = mapped_column(String(255), nullable=False)
  phone: Mapped[str] = mapped_column(String(30), nullable=False)
  account_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("account.id", ondelete="CASCADE"),
    nullable=False,
  )
  notifications_enabled: Mapped[bool] = mapped_column(
    Boolean,
    default=False,
    nullable=False,
  )

  account: Mapped[Account] = relationship(back_populates="guardians")
  students: Mapped[list[Student]] = relationship(
    secondary="guardian_student",
    back_populates="guardians",
    overlaps="guardian_students,guardians,student,students",
  )
  guardian_students: Mapped[list[GuardianStudent]] = relationship(
    back_populates="guardian",
    cascade="all, delete-orphan",
    overlaps="students",
  )
  devices: Mapped[list[GuardianDevice]] = relationship(
    back_populates="guardian",
    cascade="all, delete-orphan",
  )
