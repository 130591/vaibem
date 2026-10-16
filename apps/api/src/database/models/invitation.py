from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from apps.api.src.database.base import Base
from apps.api.src.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from apps.api.src.database.models.school import School
    from apps.api.src.database.models.student import Student


class SchoolInvitation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "school_invitations"

    school_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("school.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student.id", ondelete="CASCADE"),
        nullable=False,
    )
    guardian_email: Mapped[str] = mapped_column(String(255), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    school: Mapped[School] = relationship()
    student: Mapped[Student] = relationship()

    __table_args__ = (
        Index("idx_invitations_token_hash", "token_hash"),
        Index("idx_invitations_school_student", "school_id", "student_id"),
    )

    def is_valid(self, now: datetime | None = None) -> bool:
        current_time = now or datetime.now(UTC)
        return self.status == "pending" and self.expires_at > current_time

    def mark_as_accepted(self, now: datetime | None = None) -> None:
        if not self.is_valid(now):
            raise ValueError("O convite expirou ou já foi utilizado.")
        self.status = "accepted"