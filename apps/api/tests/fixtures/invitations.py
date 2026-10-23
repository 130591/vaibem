from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from apps.api.src.database.models import Account, School, SchoolInvitation, Student
from apps.api.src.database.session import SessionLocal
from apps.api.tests.fixtures.tokens import generate_invitation_token
from sqlalchemy import text


async def _create_test_invitation(
  status: str = "pending",
  delta_days: int = 7,
) -> tuple[UUID, UUID, str, str, str, str]:
  async with SessionLocal() as session:
    account = Account(
      id=uuid4(),
      address="Av. Paulista, 1000",
      alarm_enabled=True,
    )
    session.add(account)
    await session.flush()
    school = School(
      id=uuid4(),
      name="Escola Horizonte",
      account_id=account.id,
      geofence="SRID=4326;POLYGON((-43.42 -22.83, -43.42 -22.84, -43.43 -22.84, -43.43 -22.83, -43.42 -22.83))",
    )
    student = Student(
      id=uuid4(),
      name="João Ribeiro",
      grade="6º Ano B",
      device_status="active",
    )
    session.add_all([school, student])
    await session.flush()
    raw_token, token_hash = generate_invitation_token()

    invitation = SchoolInvitation(
      id=uuid4(),
      school_id=school.id,
      student_id=student.id,
      guardian_email="everton@exemplo.com",
      token_hash=token_hash,
      status=status,
      expires_at=datetime.now(UTC) + timedelta(days=delta_days),
    )
    session.add(invitation)
    await session.commit()

    return account.id, student.id, raw_token, school.name, student.name, invitation.guardian_email


async def _teardown_account(account_id: UUID, student_id: UUID | None = None) -> None:
  async with SessionLocal() as session:
    if student_id is not None:
      await session.execute(
        text("DELETE FROM vaibem.student WHERE id = :id"),
        {"id": student_id},
      )
    await session.execute(
      text("DELETE FROM vaibem.account WHERE id = :id"),
      {"id": account_id},
    )
    await session.commit()


@pytest.fixture
async def invitation_fixture():
  (
    account_id,
    student_id,
    raw_token,
    school_name,
    student_name,
    guardian_email,
  ) = await _create_test_invitation(status="pending", delta_days=7)
  yield {
    "raw_token": raw_token,
    "school_name": school_name,
    "student_name": student_name,
    "guardian_email": guardian_email,
    "account_id": account_id,
    "student_id": student_id,
  }
  await _teardown_account(account_id, student_id)


@pytest.fixture
async def invitation_fixture_expired():
  (
    account_id,
    student_id,
    raw_token,
    school_name,
    student_name,
    guardian_email,
  ) = await _create_test_invitation(status="pending", delta_days=-1)
  yield {
    "raw_token": raw_token,
    "school_name": school_name,
    "student_name": student_name,
    "guardian_email": guardian_email,
    "account_id": account_id,
    "student_id": student_id,
  }
  await _teardown_account(account_id, student_id)


@pytest.fixture
async def invitation_fixture_accepted():
  (
    account_id,
    student_id,
    raw_token,
    school_name,
    student_name,
    guardian_email,
  ) = await _create_test_invitation(status="accepted", delta_days=7)
  yield {
    "raw_token": raw_token,
    "school_name": school_name,
    "student_name": student_name,
    "guardian_email": guardian_email,
    "account_id": account_id,
    "student_id": student_id,
  }
  await _teardown_account(account_id, student_id)
