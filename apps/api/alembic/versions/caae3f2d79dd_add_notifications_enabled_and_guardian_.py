"""add_notifications_enabled_and_guardian_devices

Revision ID: caae3f2d79dd
Revises: 090d4cb4525d
Create Date: 2026-10-23

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "caae3f2d79dd"
down_revision: str | Sequence[str] | None = "090d4cb4525d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  # 1. Adicionar notifications_enabled na tabela guardian
  op.add_column(
    "guardian",
    sa.Column(
      "notifications_enabled", sa.Boolean(), server_default=sa.text("false"), nullable=False
    ),
    schema="vaibem",
  )

  # 2. Criar tabela guardian_devices
  op.create_table(
    "guardian_devices",
    sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
    sa.Column("guardian_id", sa.UUID(), nullable=False),
    sa.Column("device_token", sa.String(length=255), nullable=False),
    sa.Column("platform", sa.String(length=20), nullable=False),
    sa.Column(
      "last_active_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
    ),
    sa.Column(
      "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
    ),
    sa.Column(
      "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
    ),
    sa.ForeignKeyConstraint(["guardian_id"], ["vaibem.guardian.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("device_token", name="uq_guardian_device_token"),
    schema="vaibem",
  )
  op.create_index(
    "idx_guardian_devices_guardian_id", "guardian_devices", ["guardian_id"], schema="vaibem"
  )


def downgrade() -> None:
  op.drop_table("guardian_devices", schema="vaibem")
  op.drop_column("guardian", "notifications_enabled", schema="vaibem")
