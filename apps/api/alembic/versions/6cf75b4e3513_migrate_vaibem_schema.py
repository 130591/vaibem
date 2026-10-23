"""create routine, invitations and migrate journey status to StrEnum

Revision ID: 6cf75b4e3513
Revises:
Create Date: 2026-10-19 12:40:44.053178

"""

from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6cf75b4e3513"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  # 1. Criar tabela routine no schema vaibem
  op.create_table(
    "routine",
    sa.Column("student_id", sa.UUID(), nullable=False),
    sa.Column("home_address", sa.String(length=255), nullable=False),
    sa.Column(
      "home_point",
      geoalchemy2.types.Geometry(
        geometry_type="POINT", srid=4326, dimension=2, from_text="ST_GeomFromEWKT", name="geometry"
      ),
      nullable=True,
    ),
    sa.Column("habitual_departure", sa.Time(), nullable=False),
    sa.Column("habitual_return", sa.Time(), nullable=False),
    sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    sa.Column("id", sa.UUID(), nullable=False),
    sa.Column(
      "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
    ),
    sa.Column(
      "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
    ),
    sa.ForeignKeyConstraint(["student_id"], ["vaibem.student.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("student_id"),
    schema="vaibem",
  )

  # 2. Criar tabela school_invitations no schema vaibem
  op.create_table(
    "school_invitations",
    sa.Column("school_id", sa.UUID(), nullable=False),
    sa.Column("student_id", sa.UUID(), nullable=False),
    sa.Column("guardian_email", sa.String(length=255), nullable=False),
    sa.Column("token_hash", sa.String(length=64), nullable=False),
    sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("id", sa.UUID(), nullable=False),
    sa.Column(
      "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
    ),
    sa.Column(
      "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
    ),
    sa.ForeignKeyConstraint(["school_id"], ["vaibem.school.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["student_id"], ["vaibem.student.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("token_hash"),
    schema="vaibem",
  )
  op.create_index(
    "idx_invitations_school_student",
    "school_invitations",
    ["school_id", "student_id"],
    unique=False,
    schema="vaibem",
  )
  op.create_index(
    "idx_invitations_token_hash",
    "school_invitations",
    ["token_hash"],
    unique=False,
    schema="vaibem",
  )

  # 3. Adicionar coluna status em vaibem.journey
  op.add_column(
    "journey",
    sa.Column("status", sa.String(length=30), nullable=True),
    schema="vaibem",
  )

  # 4. Migrar os dados existentes (5.000 jornadas) convertendo status_lost_name para minúsculo
  op.execute("""
        UPDATE vaibem.journey j
        SET status = LOWER(js.status_lost_name)
        FROM vaibem.journey_status js
        WHERE j.status_id = js.id;
    """)
  op.execute("UPDATE vaibem.journey SET status = 'planned' WHERE status IS NULL;")

  # 5. Tornar a coluna status NOT NULL e com default
  op.alter_column(
    "journey",
    "status",
    nullable=False,
    server_default="planned",
    schema="vaibem",
  )

  # 6. Remover a chave estrangeira e coluna antiga status_id
  op.drop_constraint("fk_journey_status", "journey", schema="vaibem", type_="foreignkey")
  op.execute("DROP INDEX IF EXISTS vaibem.idx_journey_status_id;")
  op.drop_column("journey", "status_id", schema="vaibem")

  # 7. Dropar a tabela obsoleta journey_status
  op.drop_table("journey_status", schema="vaibem")


def downgrade() -> None:
  # 1. Recriar tabela journey_status
  op.create_table(
    "journey_status",
    sa.Column("id", sa.SmallInteger(), primary_key=True),
    sa.Column("status_lost_name", sa.String(100), nullable=False),
    sa.Column("status_lost_message", sa.String(255), nullable=False),
    schema="vaibem",
  )
  op.execute("""
        INSERT INTO vaibem.journey_status (id, status_lost_name, status_lost_message) VALUES
        (1, 'PLANNED', 'Journey has not started yet'),
        (2, 'IN_PROGRESS', 'Journey is currently in progress'),
        (3, 'ARRIVED_AT_SCHOOL', 'Student arrived at school'),
        (4, 'COMPLETED', 'Journey completed');
    """)

  # 2. Adicionar status_id de volta em journey
  op.add_column(
    "journey",
    sa.Column("status_id", sa.SmallInteger(), nullable=True),
    schema="vaibem",
  )
  op.execute("""
        UPDATE vaibem.journey j
        SET status_id = js.id
        FROM vaibem.journey_status js
        WHERE UPPER(j.status) = js.status_lost_name;
    """)
  op.create_foreign_key(
    "fk_journey_status",
    "journey",
    "journey_status",
    ["status_id"],
    ["id"],
    source_schema="vaibem",
    referent_schema="vaibem",
  )
  op.drop_column("journey", "status", schema="vaibem")

  # 3. Dropar tabelas novas
  op.drop_table("school_invitations", schema="vaibem")
  op.drop_table("routine", schema="vaibem")
