from __future__ import annotations

import httpx
import pytest

UPDATE_SCHEDULE_MUTATION = """
  mutation UpdateSchedule($studentId: ID!, $input: StudentScheduleInput!) {
    updateStudentSchedule(studentId: $studentId, input: $input) {
      __typename
      ... on StudentDTO {
        id
        name
        grade
        routine {
          homeAddress
          habitualDeparture
          habitualReturn
          active
        }
      }
      ... on StudentNotFoundError {
        message
      }
      ... on InvalidScheduleError {
        message
      }
    }
  }
"""


async def execute_update_schedule(
  client: httpx.AsyncClient, student_id: str, input_data: dict
) -> httpx.Response:
  return await client.post(
    "/graphql",
    json={
      "query": UPDATE_SCHEDULE_MUTATION,
      "variables": {
        "studentId": student_id,
        "input": input_data,
      },
    },
  )


@pytest.mark.asyncio
async def test_update_student_schedule_success(client, invitation_fixture):
  student_id = str(invitation_fixture["student_id"])
  schedule_input = {
    "home_address": "Rua das Flores, 123 - Apto 45",
    "habitual_departure": "07:10",
    "habitual_return": "17:10",
  }

  response = await execute_update_schedule(client, student_id, schedule_input)
  assert response.status_code == 200
  payload = response.json()

  assert "errors" not in payload, f"Erros no GraphQL: {payload.get('errors')}"
  data = payload["data"]["updateStudentSchedule"]

  assert data["__typename"] == "StudentDTO"
  assert data["name"] == invitation_fixture["student_name"]
  assert data["routine"] is not None
  assert data["routine"]["homeAddress"] == "Rua das Flores, 123 - Apto 45"
  assert data["routine"]["habitualDeparture"] == "07:10"
  assert data["routine"]["habitualReturn"] == "17:10"
  assert data["routine"]["active"] is True


@pytest.mark.asyncio
async def test_update_student_schedule_adjust_time_and_address(client, invitation_fixture):
  student_id = str(invitation_fixture["student_id"])
  # 1. Primeira confirmação
  await execute_update_schedule(
    client,
    student_id,
    {
      "home_address": "Rua das Flores, 123",
      "habitual_departure": "07:10",
      "habitual_return": "17:10",
    },
  )

  # 2. Ajuste de horário e endereço (Cenário 2 da US01.3)
  response = await execute_update_schedule(
    client,
    student_id,
    {
      "home_address": "Av. Brasil, 500",
      "habitual_departure": "07:15",
      "habitual_return": "17:30",
    },
  )
  assert response.status_code == 200
  data = response.json()["data"]["updateStudentSchedule"]

  assert data["__typename"] == "StudentDTO"
  assert data["routine"]["homeAddress"] == "Av. Brasil, 500"
  assert data["routine"]["habitualDeparture"] == "07:15"
  assert data["routine"]["habitualReturn"] == "17:30"


@pytest.mark.asyncio
async def test_update_student_schedule_student_not_found(client):
  fake_id = "00000000-0000-0000-0000-000000000000"
  response = await execute_update_schedule(
    client,
    fake_id,
    {
      "home_address": "Rua Teste, 1",
      "habitual_departure": "07:00",
      "habitual_return": "17:00",
    },
  )
  assert response.status_code == 200
  data = response.json()["data"]["updateStudentSchedule"]

  assert data["__typename"] == "StudentNotFoundError"
  assert "não encontrado" in data["message"].lower()


@pytest.mark.asyncio
async def test_update_student_schedule_invalid_time_range(client, invitation_fixture):
  student_id = str(invitation_fixture["student_id"])
  # Retorno antes da saída (ex: saída 17:00, volta 07:00)
  response = await execute_update_schedule(
    client,
    student_id,
    {
      "home_address": "Rua Teste, 1",
      "habitual_departure": "17:00",
      "habitual_return": "07:00",
    },
  )
  assert response.status_code == 200
  data = response.json()["data"]["updateStudentSchedule"]

  assert data["__typename"] == "InvalidScheduleError"
  assert "posterior" in data["message"].lower()


@pytest.mark.asyncio
async def test_update_student_schedule_bad_user_input_invalid_uuid(client):
  response = await execute_update_schedule(
    client,
    "uuid-invalido-123",
    {
      "home_address": "Rua Teste, 1",
      "habitual_departure": "07:00",
      "habitual_return": "17:00",
    },
  )
  assert response.status_code == 200
  payload = response.json()

  assert "errors" in payload
  assert payload["errors"][0]["extensions"]["code"] == "BAD_USER_INPUT"
