from __future__ import annotations

from uuid import uuid4

import httpx
import pytest
from apps.api.src.database.models import Account, Guardian
from apps.api.src.database.session import SessionLocal
from apps.api.src.security import create_access_token
from sqlalchemy import text

REGISTER_DEVICE_TOKEN_MUTATION = """
  mutation RegisterDevice($input: DeviceTokenInput!) {
    registerDeviceToken(input: $input) {
      __typename
      ... on DeviceTokenPayload {
        success
        notificationsEnabled
      }
      ... on GuardianNotFoundError {
        message
      }
      ... on InvalidDeviceTokenError {
        message
      }
    }
  }
"""


async def execute_register_device(
  client: httpx.AsyncClient, input_data: dict, token: str | None = None
) -> httpx.Response:
  headers = {}
  if token:
    headers["Authorization"] = f"Bearer {token}"

  return await client.post(
    "/graphql",
    headers=headers,
    json={
      "query": REGISTER_DEVICE_TOKEN_MUTATION,
      "variables": {"input": input_data},
    },
  )


@pytest.fixture
async def guardian_fixture():
  async with SessionLocal() as session:
    account = Account(
      id=uuid4(),
      address="Av. Paulista, 1000",
      alarm_enabled=False,
    )
    session.add(account)
    await session.flush()

    guardian = Guardian(
      id=uuid4(),
      email="responsavel.device@teste.com",
      name="Maria dos Santos",
      phone="11988887777",
      account_id=account.id,
      notifications_enabled=False,
    )
    session.add(guardian)
    await session.commit()

    yield {
      "account_id": account.id,
      "guardian_id": guardian.id,
      "email": guardian.email,
    }

  async with SessionLocal() as session:
    await session.execute(
      text("DELETE FROM vaibem.account WHERE id = :id"),
      {"id": account.id},
    )
    await session.commit()


@pytest.mark.asyncio
async def test_register_device_token_success(client, guardian_fixture):
  guardian_id = str(guardian_fixture["guardian_id"])
  device_input = {
    "device_token": "fcm_token_super_seguro_12345",
    "platform": "ios",
    "guardian_id": guardian_id,
  }

  response = await execute_register_device(client, device_input)
  assert response.status_code == 200
  payload = response.json()

  assert "errors" not in payload, f"Erros no GraphQL: {payload.get('errors')}"
  data = payload["data"]["registerDeviceToken"]

  assert data["__typename"] == "DeviceTokenPayload"
  assert data["success"] is True
  assert data["notificationsEnabled"] is True


@pytest.mark.asyncio
async def test_register_device_token_authenticated_via_jwt_header(client, guardian_fixture):
  guardian_id = str(guardian_fixture["guardian_id"])
  account_id = str(guardian_fixture["account_id"])
  jwt_token = create_access_token(account_id=account_id, guardian_id=guardian_id)

  # Não envia guardian_id no input, o resolver obtém do JWT no header Authorization
  device_input = {
    "device_token": "fcm_token_via_jwt_auth_999",
    "platform": "android",
  }

  response = await execute_register_device(client, device_input, token=jwt_token)
  assert response.status_code == 200
  payload = response.json()

  assert "errors" not in payload, f"Erros no GraphQL: {payload.get('errors')}"
  data = payload["data"]["registerDeviceToken"]

  assert data["__typename"] == "DeviceTokenPayload"
  assert data["success"] is True
  assert data["notificationsEnabled"] is True


@pytest.mark.asyncio
async def test_register_device_token_update_existing_device(client, guardian_fixture):
  guardian_id = str(guardian_fixture["guardian_id"])
  token_str = "fcm_token_reutilizado_001"

  # 1. Primeiro registro
  res1 = await execute_register_device(
    client,
    {"device_token": token_str, "platform": "android", "guardian_id": guardian_id},
  )
  assert res1.json()["data"]["registerDeviceToken"]["success"] is True

  # 2. Segundo registro com mesmo token (ex: migrou ou renovou)
  res2 = await execute_register_device(
    client,
    {"device_token": token_str, "platform": "ios", "guardian_id": guardian_id},
  )
  assert res2.json()["data"]["registerDeviceToken"]["success"] is True


@pytest.mark.asyncio
async def test_register_device_token_guardian_not_found(client):
  fake_id = "00000000-0000-0000-0000-000000000000"
  response = await execute_register_device(
    client,
    {"device_token": "fcm_token_qualquer_123", "platform": "android", "guardian_id": fake_id},
  )
  assert response.status_code == 200
  data = response.json()["data"]["registerDeviceToken"]

  assert data["__typename"] == "GuardianNotFoundError"


@pytest.mark.asyncio
async def test_register_device_token_invalid_platform(client, guardian_fixture):
  guardian_id = str(guardian_fixture["guardian_id"])
  response = await execute_register_device(
    client,
    {
      "device_token": "fcm_token_qualquer_123",
      "platform": "windows_phone",
      "guardian_id": guardian_id,
    },
  )
  assert response.status_code == 200
  data = response.json()["data"]["registerDeviceToken"]

  assert data["__typename"] == "InvalidDeviceTokenError"
  assert "inválida" in data["message"].lower()


@pytest.mark.asyncio
async def test_register_device_token_bad_user_input_missing_guardian(client):
  response = await execute_register_device(
    client,
    {"device_token": "fcm_token_qualquer_123", "platform": "android"},
  )
  assert response.status_code == 200
  payload = response.json()

  assert "errors" in payload
  assert payload["errors"][0]["extensions"]["code"] == "BAD_USER_INPUT"
  assert payload["errors"][0]["extensions"]["argument"] == "guardian_id"
