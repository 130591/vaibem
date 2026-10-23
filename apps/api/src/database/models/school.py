from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from apps.api.src.database.base import Base
from apps.api.src.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from geoalchemy2 import Geography
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
  from apps.api.src.database.models.account import Account


class School(UUIDPrimaryKeyMixin, TimestampMixin, Base):
  __tablename__ = "school"

  name: Mapped[str] = mapped_column(String(255), nullable=False)
  geofence: Mapped[str | None] = mapped_column(Geography("POLYGON", srid=4326), nullable=True)
  account_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("account.id", ondelete="CASCADE"),
    nullable=False,
  )

  account: Mapped[Account] = relationship(back_populates="schools")
