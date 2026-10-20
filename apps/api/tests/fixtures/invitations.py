from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import pytest
from apps.api.src.database.models import Account, School, SchoolInvitation, Student
from apps.api.src.database.session import SessionLocal
from apps.api.tests.fixtures.tokens import generate_invitation_token
from sqlalchemy import text


async def _create_invitation_tree(
    status: str = "pending",
    delta_days: int = 7,
) -> AsyncGenerator[dict[str, Any], None]:
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
            account_id=account.id,
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

    try:
        yield {
            "raw_token": raw_token,
            "school_name": school.name,
            "student_name": student.name,
            "guardian_email": invitation.guardian_email,
            "account_id": account.id,
        }
    finally:
        async with SessionLocal() as session:
            await session.execute(
                text("DELETE FROM vaibem.account WHERE id = :id"),
                {"id": account.id},
            )
            await session.commit()


@pytest.fixture
async def invitation_fixture():
    """Cria árvore completa de convite válido (pending, expira em 7 dias)."""
    async for data in _create_invitation_tree(status="pending", delta_days=7):
        yield data


@pytest.fixture
async def invitation_fixture_expired():
    """Cria árvore completa de convite expirado (pending, expirou há 1 dia)."""
    async for data in _create_invitation_tree(status="pending", delta_days=-1):
        yield data


@pytest.fixture
async def invitation_fixture_accepted():
    """Cria árvore completa de convite já consumido (accepted)."""
    async for data in _create_invitation_tree(status="accepted", delta_days=7):
        yield data
