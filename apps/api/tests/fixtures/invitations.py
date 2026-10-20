from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from apps.api.src.database.models import Account, School, SchoolInvitation, Student
from apps.api.src.database.session import SessionLocal
from apps.api.tests.fixtures.tokens import generate_invitation_token


@pytest.fixture
async def invitation_fixture_expired():
    """Cria a árvore completa: Account -> School + Student -> SchoolInvitation (expirado).
    
    Ao terminar o teste, deleta a Account (o banco limpa o resto em cascata).
    """

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
            status="pending",
            expires_at=datetime.now(UTC) - timedelta(days=1),  # expirado!
        )
        session.add(invitation)
        await session.commit()
   
    yield {
        "raw_token": raw_token,
        "school_name": school.name,
        "student_name": student.name,
        "guardian_email": invitation.guardian_email,
        "account_id": account.id,
    }
    # 3. TEARDOWN: Limpeza após o teste rodar via CASCADE nativo do PostgreSQL
    async with SessionLocal() as session:
        from sqlalchemy import text
        await session.execute(
            text("DELETE FROM vaibem.account WHERE id = :id"),
            {"id": account.id},
        )
        await session.commit()


@pytest.fixture
async def invitation_fixture():
    """Cria a árvore completa: Account -> School + Student -> SchoolInvitation.
    
    Ao terminar o teste, deleta a Account (o banco limpa o resto em cascata).
    """

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
            status="pending",
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        session.add(invitation)
        await session.commit()
   
    yield {
        "raw_token": raw_token,
        "school_name": school.name,
        "student_name": student.name,
        "guardian_email": invitation.guardian_email,
        "account_id": account.id,
    }
    # 3. TEARDOWN: Limpeza após o teste rodar via CASCADE nativo do PostgreSQL
    async with SessionLocal() as session:
        from sqlalchemy import text
        await session.execute(
            text("DELETE FROM vaibem.account WHERE id = :id"),
            {"id": account.id},
        )
        await session.commit()
