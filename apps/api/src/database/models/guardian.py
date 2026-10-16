from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from apps.api.src.database.base import Base
from apps.api.src.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
  from apps.api.src.database.models.account import Account


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

  account: Mapped[Account] = relationship(back_populates="guardians")