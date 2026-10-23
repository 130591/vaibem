"""create_guardian_student_and_remove_student_account_id

Revision ID: 090d4cb4525d
Revises: 6cf75b4e3513
Create Date: 2026-10-22 22:24:57.744250

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "090d4cb4525d"
down_revision: str | Sequence[str] | None = "6cf75b4e3513"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  # 1. Criar tabela vaibem.guardian_student
  op.create_table(
    "guardian_student",
    sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
    sa.Column("guardian_id", sa.UUID(), nullable=False),
    sa.Column("student_id", sa.UUID(), nullable=False),
    sa.Column(
      "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
    ),
    sa.ForeignKeyConstraint(["guardian_id"], ["vaibem.guardian.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["student_id"], ["vaibem.student.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("guardian_id", "student_id", name="uq_guardian_student"),
    schema="vaibem",
  )
  op.create_index(
    "idx_guardian_student_guardian", "guardian_student", ["guardian_id"], schema="vaibem"
  )
  op.create_index(
    "idx_guardian_student_student", "guardian_student", ["student_id"], schema="vaibem"
  )

  # 2. Remover fk_student_account e coluna account_id da tabela vaibem.student
  op.drop_constraint("fk_student_account", "student", schema="vaibem", type_="foreignkey")
  op.drop_column("student", "account_id", schema="vaibem")


def downgrade() -> None:
  # 1. Recriar coluna account_id em vaibem.student
  op.add_column(
    "student",
    sa.Column("account_id", sa.UUID(), nullable=True),
    schema="vaibem",
  )
  op.create_foreign_key(
    "fk_student_account",
    "student",
    "account",
    ["account_id"],
    ["id"],
    source_schema="vaibem",
    referent_schema="vaibem",
    ondelete="CASCADE",
  )

  # 2. Dropar tabela vaibem.guardian_student
  op.drop_table("guardian_student", schema="vaibem")
