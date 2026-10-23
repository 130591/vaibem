import pytest
from apps.api.tests.stubs.invitation import execute_activation_account


@pytest.mark.asyncio
async def test_account_activation(client, invitation_fixture):
  raw_token = invitation_fixture["raw_token"]
  register = {
    "guardian_name": "joao",
    "phone": "12333212",
    "token": raw_token,
    "password": "mdewomwkdmcowmkmck",
  }
  response = await execute_activation_account(client, register)
  assert response.status_code == 200
  payload = response.json()

  assert "errors" not in payload, f"Erros no GraphQL: {payload.get('errors')}"
  data = payload["data"]["registerGuardianFromInvitation"]

  assert data["__typename"] == "AuthPayload"
  assert data["accessToken"] is not None
