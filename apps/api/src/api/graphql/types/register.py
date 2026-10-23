from __future__ import annotations

from typing import Annotated

import strawberry
from apps.api.src.api.graphql.types.invitation import (
  InvitationAlreadyUsedError,
  InvitationExpiredError,
  InvitationInvalidError,
  InvitationNotFoundError,
)


@strawberry.type(name="AuthPayload")
class AuthPayload:
  access_token: str
  refresh_token: str

  @classmethod
  def from_domain(cls, access_token: str = "", refresh_token: str = "") -> AuthPayload:
    return cls(
      access_token=access_token,
      refresh_token=refresh_token,
    )

  @classmethod
  def from_tokens(cls, access_token: str, refresh_token: str) -> AuthPayload:
    return cls(
      access_token=access_token,
      refresh_token=refresh_token,
    )


RegisterGuardianDTO = AuthPayload


@strawberry.type
class AccountAlreadyExistsError:
  message: str = "Responsável já possui conta cadastrada."


RegisterGuardianResult = Annotated[
  AuthPayload
  | InvitationNotFoundError
  | InvitationExpiredError
  | InvitationAlreadyUsedError
  | InvitationInvalidError
  | AccountAlreadyExistsError,
  strawberry.union("RegisterGuardianResult"),
]
