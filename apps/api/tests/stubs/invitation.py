import httpx

VALIDATE_INVITATION_QUERY = """
  query Validate($token: String!) {
    validateSchoolInvitation(token: $token) {
      status
      schoolName
      studentName
      guardianEmail
    }
  }
"""


async def execute_validate_invitation(client: httpx.AsyncClient, token: str) -> httpx.Response:
  return await client.post(
    "/graphql",
    json={
      "query": VALIDATE_INVITATION_QUERY,
      "variables": {"token": token},
    },
  )
