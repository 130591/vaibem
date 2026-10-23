import pytest
from apps.api.src.database.session import SessionLocal
from apps.api.tests.stubs.invitation import execute_activation_account
from sqlalchemy import text


async def _teardown_guardian(email: str, phone: str = ""):
  async with SessionLocal() as session:
    await session.execute(
      text("DELETE FROM vaibem.guardian WHERE email = :email OR phone = :phone"),
      {"email": email, "phone": phone},
    )
    await session.commit()


@pytest.mark.asyncio
async def test_account_activation_success(client, invitation_fixture):
  email = invitation_fixture["guardian_email"]
  raw_token = invitation_fixture["raw_token"]
  register = {
    "guardian_name": "João Responsável",
    "phone": "11987654321",
    "token": raw_token,
    "password": "strongpassword123",
  }
  try:
    response = await execute_activation_account(client, register)
    assert response.status_code == 200
    payload = response.json()

    assert "errors" not in payload, f"Erros no GraphQL: {payload.get('errors')}"
    data = payload["data"]["registerGuardianFromInvitation"]

    assert data["__typename"] == "AuthPayload"
    assert data["accessToken"] is not None
    assert data["refreshToken"] is not None
  finally:
    await _teardown_guardian(email, register["phone"])


@pytest.mark.asyncio
async def test_account_activation_already_exists_returns_error(client, invitation_fixture):
  email = invitation_fixture["guardian_email"]
  raw_token = invitation_fixture["raw_token"]
  register = {
    "guardian_name": "João Responsável",
    "phone": "11987654321",
    "token": raw_token,
    "password": "strongpassword123",
  }
  try:
    # 1. Primeiro cadastro com sucesso
    res1 = await execute_activation_account(client, register)
    assert res1.status_code == 200
    data1 = res1.json()["data"]["registerGuardianFromInvitation"]
    assert data1["__typename"] == "AuthPayload"

    # 2. Tentar registrar novamente com os mesmos dados
    res2 = await execute_activation_account(client, register)
    assert res2.status_code == 200
    data2 = res2.json()["data"]["registerGuardianFromInvitation"]
    # Pode falhar por já usado ou por conta já existir
    assert data2["__typename"] in ("AccountAlreadyExistsError", "InvitationAlreadyUsedError")
  finally:
    await _teardown_guardian(email, register["phone"])


@pytest.mark.asyncio
async def test_account_activation_expired_invitation(client, invitation_fixture_expired):
  raw_token = invitation_fixture_expired["raw_token"]
  register = {
    "guardian_name": "Responsável Teste",
    "phone": "11999998888",
    "token": raw_token,
    "password": "strongpassword123",
  }
  response = await execute_activation_account(client, register)
  assert response.status_code == 200
  data = response.json()["data"]["registerGuardianFromInvitation"]

  assert data["__typename"] == "InvitationExpiredError"
  assert "expirou" in data["message"].lower()


@pytest.mark.asyncio
async def test_account_activation_already_used_invitation(client, invitation_fixture_accepted):
  raw_token = invitation_fixture_accepted["raw_token"]
  register = {
    "guardian_name": "Responsável Teste",
    "phone": "11999998888",
    "token": raw_token,
    "password": "strongpassword123",
  }
  response = await execute_activation_account(client, register)
  assert response.status_code == 200
  data = response.json()["data"]["registerGuardianFromInvitation"]

  assert data["__typename"] == "InvitationAlreadyUsedError"
  assert "já foi utilizado" in data["message"].lower()


@pytest.mark.asyncio
async def test_account_activation_invalid_token_not_found(client):
  register = {
    "guardian_name": "Responsável Teste",
    "phone": "11999998888",
    "token": "token_que_nao_existe_no_banco_123456789",
    "password": "strongpassword123",
  }
  response = await execute_activation_account(client, register)
  assert response.status_code == 200
  data = response.json()["data"]["registerGuardianFromInvitation"]

  assert data["__typename"] == "InvitationNotFoundError"


@pytest.mark.asyncio
async def test_account_activation_password_too_short_raises_bad_user_input(
  client, invitation_fixture
):
  raw_token = invitation_fixture["raw_token"]
  register = {
    "guardian_name": "João",
    "phone": "11999998888",
    "token": raw_token,
    "password": "short",  # < 8 chars
  }
  response = await execute_activation_account(client, register)
  assert response.status_code == 200
  payload = response.json()

  assert "errors" in payload
  error = payload["errors"][0]
  assert error["extensions"]["code"] == "BAD_USER_INPUT"
  assert error["extensions"]["argument"] == "password"
