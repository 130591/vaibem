from __future__ import annotations

import httpx

VALIDATE_INVITATION_QUERY = """
  query Validate($token: String!) {
    validateSchoolInvitation(token: $token) {
      __typename
      ... on SchoolInvitationDTO {
        status
        schoolName
        studentName
        guardianEmail
      }
      ... on InvitationNotFoundError {
        message
      }
      ... on InvitationExpiredError {
        message
      }
      ... on InvitationAlreadyUsedError {
        message
      }
      ... on InvitationInvalidError {
        message
      }
    }
  }
"""

REGISTER_GUARDIAN_MUTATION = """
  mutation Register($input: RegisterGuardianInfo!) {
    registerGuardianFromInvitation(input: $input) {
      __typename
      ... on AuthPayload {
        accessToken
        refreshToken
      }
      ... on InvitationNotFoundError {
        message
      }
      ... on InvitationExpiredError {
        message
      }
      ... on InvitationAlreadyUsedError {
        message
      }
      ... on InvitationInvalidError {
        message
      }
      ... on AccountAlreadyExistsError {
        message
      }
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


async def execute_activation_account(client: httpx.AsyncClient, input_data: dict) -> httpx.Response:
  return await client.post(
    "/graphql",
    json={
      "query": REGISTER_GUARDIAN_MUTATION,
      "variables": {"input": input_data},
    },
  )
