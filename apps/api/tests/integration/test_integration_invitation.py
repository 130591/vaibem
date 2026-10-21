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
  assert data["__typename"] == "SchoolInvitationDTO"
  assert data["schoolName"] == invitation_fixture["school_name"]
  assert data["studentName"] == invitation_fixture["student_name"]
  assert data["guardianEmail"] == invitation_fixture["guardian_email"]
  assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_invite_token_expired(client, invitation_fixture_expired):
  response = await execute_validate_invitation(client, invitation_fixture_expired["raw_token"])
  assert response.status_code == 200
  payload = response.json()

  assert "errors" not in payload, f"Erros no GraphQL: {payload.get('errors')}"
  data = payload["data"]["validateSchoolInvitation"]
  assert data["__typename"] == "InvitationExpiredError"
  assert data["message"] == "Este convite expirou."


@pytest.mark.asyncio
async def test_invite_token_already_used(client, invitation_fixture_accepted):
  response = await execute_validate_invitation(client, invitation_fixture_accepted["raw_token"])
  assert response.status_code == 200
  payload = response.json()

  assert "errors" not in payload, f"Erros no GraphQL: {payload.get('errors')}"
  data = payload["data"]["validateSchoolInvitation"]
  assert data["__typename"] == "InvitationAlreadyUsedError"
  assert data["message"] == "Este convite já foi utilizado."


@pytest.mark.asyncio
async def test_invite_token_notfound(client):
  wrong_token, _ = generate_invitation_token()
  response = await execute_validate_invitation(client, wrong_token)
  assert response.status_code == 200
  payload = response.json()

  assert "errors" not in payload, f"Erros no GraphQL: {payload.get('errors')}"
  data = payload["data"]["validateSchoolInvitation"]
  assert data["__typename"] == "InvitationNotFoundError"
  assert data["message"] == "Convite não encontrado."


@pytest.mark.asyncio
async def test_invite_token_bad_user_input(client):
  response = await execute_validate_invitation(client, "")
  assert response.status_code == 200
  payload = response.json()

  assert "errors" in payload
  assert payload["errors"][0]["extensions"]["code"] == "BAD_USER_INPUT"
  assert payload["errors"][0]["extensions"]["argument"] == "token"
