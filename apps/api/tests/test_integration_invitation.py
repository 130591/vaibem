
import httpx
import pytest
from apps.api.src.main import app


@pytest.mark.asyncio
async def test_validate_invite_token(invitation_fixture):
  raw_token = invitation_fixture["raw_token"]
  expected_school = invitation_fixture["school_name"]
  expected_student = invitation_fixture["student_name"]
  
  transport = httpx.ASGITransport(app=app)
  async with httpx.AsyncClient(
    transport=transport, base_url="http://test"
  ) as client:
    response = await client.post(
      "/graphql",
      json={
        "query": """
          query Validate($token: String!) {
            validateSchoolInvitation(token: $token) {
              status
              schoolName
              studentName
            }
          }
        """,
        "variables": {"token": raw_token },
      },
    )
        
    assert response.status_code == 200
    payload = response.json()
   
    assert "errors" not in payload, f"Erros no GraphQL: {payload.get('errors')}"
    
    data = payload["data"]["validateSchoolInvitation"]
    assert data["schoolName"] == expected_school
    assert data["studentName"] == expected_student
    assert data["status"] == "pending" 