import pytest
from apps.api.tests.fixtures.tokens import generate_invitation_token
from apps.api.tests.stubs.invitation import execute_validate_invitation


@pytest.mark.asyncio
async def test_validate_invite_token(client, invitation_fixture):
  response = await execute_validate_invitation(client, invitation_fixture["raw_token"])
  assert response.status_code == 200
  payload = response.json()

  assert "errors" not in payload, f"Erros no GraphQL: {payload.get('errors')}"
  data = payload["data"]["validateSchoolInvitation"]
  assert data["schoolName"] == invitation_fixture["school_name"]
  assert data["studentName"] == invitation_fixture["student_name"]
  assert data["guardianEmail"] == invitation_fixture["guardian_email"]
  assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_invite_token_expired(client, invitation_fixture_expired):
  response = await execute_validate_invitation(client, invitation_fixture_expired["raw_token"])
  assert response.status_code == 200
  payload = response.json()

  assert "errors" in payload
  assert "Este convite expirou." in payload["errors"][0]["message"]
  assert payload["errors"][0]["extensions"]["code"] == "INVITATION_EXPIRED"
  assert (
    payload.get("data") is None
    or payload["data"]["validateSchoolInvitation"] is None
  )


@pytest.mark.asyncio
async def test_invite_token_already_used(client, invitation_fixture_accepted):
  response = await execute_validate_invitation(client, invitation_fixture_accepted["raw_token"])
  assert response.status_code == 200
  payload = response.json()

  assert "errors" in payload
  assert "Este convite já foi utilizado." in payload["errors"][0]["message"]
  assert payload["errors"][0]["extensions"]["code"] == "INVITATION_ALREADY_USED"
  assert (
    payload.get("data") is None
    or payload["data"]["validateSchoolInvitation"] is None
  )


@pytest.mark.asyncio
async def test_invite_token_notfound(client):
  wrong_token, _ = generate_invitation_token()
  response = await execute_validate_invitation(client, wrong_token)
  assert response.status_code == 200
  payload = response.json()

  assert "errors" in payload
  assert "Convite não encontrado." in payload["errors"][0]["message"]
  assert payload["errors"][0]["extensions"]["code"] == "INVITATION_NOT_FOUND"
  assert (
    payload.get("data") is None
    or payload["data"]["validateSchoolInvitation"] is None
  )
