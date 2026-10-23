import httpx
from apps.api.src.api.graphql.mutations.account import RegisterGuardianInfo

ACTIVATION_ACCOUNT_FROM_INVITE_QUERY = """
  mutation Register($input: RegisterGuardianInput!) {
    registerGuardianFromInvitation(input: input!) {
      __typename
      ... on AuthPayload {
            accessToken
            refreshToken
            guardian {
             id
             name
             email
          }
       }
    }
  }
"""


async def execute_activation_account(
  client: httpx.AsyncClient, info: RegisterGuardianInfo
) -> httpx.Response:
  return await client.post(
    "/graphql",
    json={
      "query": ACTIVATION_ACCOUNT_FROM_INVITE_QUERY,
      "variables": {
        "guardian_name": info.guardian_name,
        "phone": info.phone,
        "token": info.token,
        "password": info.password,
      },
    },
  )
