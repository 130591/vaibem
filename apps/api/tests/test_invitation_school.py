from datetime import UTC, datetime, timedelta

import pytest
from apps.api.src.database.models.invitation import SchoolInvitation


@pytest.mark.parametrize(
 ("status", "delta_seconds", "expected"),
 [
    ("pending", 3600, True),    # 1h no futuro -> Válido
    ("pending", -60, False),    # 1min no passado -> Expirado
    ("pending", 0, False),      # Limite exato -> Inválido
    ("accepted", 3600, False),  # Já aceito -> Inválido
    ("revoked", 3600, False),   # Revogado -> Inválido  
 ],
 ids=[
    "convite_pendente_no_prazo",
    "convite_pendente_porem_expirado",
    "convite_expirado_emcima_dahora",
    "convite_ja_aceito",
    "convite_revogado",
  ],
)
def test_school_invitation_validity(status, delta_seconds, expected):
  now = datetime(2026, 10, 18, 12, 0, tzinfo=UTC)
  expires_at = now + timedelta(seconds=delta_seconds)
        
  invitation = SchoolInvitation(
    status=status,
    expires_at=expires_at,
    guardian_email="pai@exemplo.com",
    token_hash="fake-hash",
  )

  assert invitation.is_valid(now=now) is expected
    

def test_mark_as_accepted_success():
  now = datetime(2026, 10, 18, 12, 0, tzinfo=UTC)
  invitation = SchoolInvitation(
    status="pending",
    expires_at=now + timedelta(hours=2),
    guardian_email="pai@exemplo.com",
    token_hash="fake-hash",
  )
    
  invitation.mark_as_accepted(now=now)
  assert invitation.status == "accepted"
    
def test_mark_as_accepted_fails_when_expired():
  now = datetime(2026, 10, 18, 12, 0, tzinfo=UTC)
  invitation = SchoolInvitation(
    status="pending",
    expires_at=now - timedelta(minutes=5),
    guardian_email="pai@exemplo.com",
    token_hash="fake-hash",
  )

  with pytest.raises(ValueError):
    invitation.mark_as_accepted(now=now)

  assert invitation.status == "pending" 
