from __future__ import annotations

from typing import TYPE_CHECKING

from apps.api.src.database.base import Base
from apps.api.src.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
  from apps.api.src.database.models.guardian import Guardian
  from apps.api.src.database.models.school import School
  from apps.api.src.database.models.student import Student


class Account(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "account"

  address: Mapped[str] = mapped_column(String(255), nullable=False)
  alarm_enabled: Mapped[bool] = mapped_column(
    Boolean, nullable=False, default=False
  )

  guardians: Mapped[list[Guardian]] = relationship(
    back_populates="account",
    cascade="all, delete-orphan",
  )
  schools: Mapped[list[School]] = relationship(
    back_populates="account",
    cascade="all, delete-orphan",
  )
  students: Mapped[list[Student]] = relationship(
    back_populates="account",
    cascade="all, delete-orphan",
  )