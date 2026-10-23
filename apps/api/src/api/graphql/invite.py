from __future__ import annotations

import strawberry
from apps.api.src.api.graphql.types.invitation import (
  InvitationAlreadyUsedError,
  InvitationExpiredError,
  InvitationInvalidError,
  InvitationNotFoundError,
  SchoolInvitationDTO,
  ValidateInvitationResult,
)
from apps.api.src.database.repositories.invite_school_repository import (
  InviteSchoolRepository,
)
from apps.api.src.database.session import SessionLocal
from apps.api.src.domains.exceptions import (
  AlreadyUsedInviteError,
  InvalidExpiredError,
  InvalidInviteError,
  InviteNotFoundException,
)
from apps.api.src.services.invite_service import InviteService
from graphql import GraphQLError
from strawberry.types import Info


async def _execute_validation(service: InviteService, clean_token: str) -> ValidateInvitationResult:
  try:
    entity = await service.validate(clean_token)
    return SchoolInvitationDTO.from_domain(entity)

  except InviteNotFoundException as exc:
    return InvitationNotFoundError(message=str(exc))

  except AlreadyUsedInviteError as exc:
    return InvitationAlreadyUsedError(message=str(exc))

  except InvalidExpiredError as exc:
    return InvitationExpiredError(message=str(exc))

  except InvalidInviteError as exc:
    return InvitationInvalidError(message=str(exc))


@strawberry.type
class InviteQuery:
  def __init__(self, invite_service: InviteService | None = None):
    self.invite_service = invite_service

  @strawberry.field
  async def validate_school_invitation(self, info: Info, token: str) -> ValidateInvitationResult:
    service = getattr(self, "invite_service", None)
    if service is None and info is not None:
      context = info.context or {}
      service = context.get("invite_service") if isinstance(context, dict) else None

    if not isinstance(token, str):
      raise GraphQLError(
        message="O 'token' fornecido não é uma string válida.",
        extensions={"code": "BAD_USER_INPUT", "argument": "token"},
      )

    clean_token = token.strip()
    if not clean_token or len(clean_token) > 128:
      raise GraphQLError(
        message="O 'token' fornecido é inválido ou excede o tamanho permitido.",
        extensions={"code": "BAD_USER_INPUT", "argument": "token"},
      )

    if service is None:
      async with SessionLocal() as session:
        repo = InviteSchoolRepository(session)
        service = InviteService(repo)
        return await _execute_validation(service, clean_token)

    return await _execute_validation(service, clean_token)
