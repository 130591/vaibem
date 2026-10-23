from __future__ import annotations

import strawberry
from apps.api.src.api.graphql.types.invitation import (
  InvitationAlreadyUsedError,
  InvitationExpiredError,
  InvitationInvalidError,
  InvitationNotFoundError,
)
from apps.api.src.api.graphql.types.register import (
  AccountAlreadyExistsError,
  AuthPayload,
  RegisterGuardianResult,
)
from apps.api.src.database.repositories.invite_school_repository import (
  InviteSchoolRepository,
)
from apps.api.src.database.repositories.profile_repository import ProfileRepository
from apps.api.src.database.session import SessionLocal
from apps.api.src.domains.exceptions import (
  AccountAlreadyExistsError as DomainAccountAlreadyExistsError,
)
from apps.api.src.domains.exceptions import (
  AlreadyUsedInviteError,
  InvalidExpiredError,
  InvalidInviteError,
  InviteNotFoundException,
)
from apps.api.src.services.profile_service import ProfileService
from graphql import GraphQLError
from strawberry.types import Info


@strawberry.input
class RegisterGuardianInfo:
  token: str
  phone: str
  password: str
  guardian_name: str | None = strawberry.field(name="guardian_name", default=None)
  guardian_name_camel: str | None = strawberry.field(name="guardianName", default=None)

  @property
  def name(self) -> str:
    return (self.guardian_name or self.guardian_name_camel or "").strip()


async def _execute_registration(
  service: ProfileService, register_guardian: RegisterGuardianInfo
) -> RegisterGuardianResult:
  try:
    tokens = await service.register(register_guardian)
    return AuthPayload.from_tokens(
      access_token=tokens.access_token,
      refresh_token=tokens.refresh_token,
    )
  except InviteNotFoundException as exc:
    return InvitationNotFoundError(message=str(exc))
  except AlreadyUsedInviteError as exc:
    return InvitationAlreadyUsedError(message=str(exc))
  except InvalidExpiredError as exc:
    return InvitationExpiredError(message=str(exc))
  except InvalidInviteError as exc:
    return InvitationInvalidError(message=str(exc))
  except DomainAccountAlreadyExistsError as exc:
    return AccountAlreadyExistsError(message=str(exc))


@strawberry.type
class RegisterGuardianMutation:
  def __init__(self, profile_service: ProfileService | None = None):
    self.profile_service = profile_service

  @strawberry.mutation
  async def register_guardian_from_invitation(
    self, info: Info, input: RegisterGuardianInfo
  ) -> RegisterGuardianResult:
    if not input.token or not input.token.strip() or len(input.token.strip()) > 128:
      raise GraphQLError(
        message="O 'token' fornecido é inválido ou excede o tamanho permitido.",
        extensions={"code": "BAD_USER_INPUT", "argument": "token"},
      )

    if not input.name:
      raise GraphQLError(
        message="O nome do responsável é obrigatório.",
        extensions={"code": "BAD_USER_INPUT", "argument": "guardian_name"},
      )

    if not input.phone or not input.phone.strip():
      raise GraphQLError(
        message="O telefone do responsável é obrigatório.",
        extensions={"code": "BAD_USER_INPUT", "argument": "phone"},
      )

    if not input.password or len(input.password) < 8:
      raise GraphQLError(
        message="A senha deve conter no mínimo 8 caracteres.",
        extensions={"code": "BAD_USER_INPUT", "argument": "password"},
      )

    service = getattr(self, "profile_service", None)
    if service is None and info is not None:
      context = info.context or {}
      service = context.get("profile_service") if isinstance(context, dict) else None

    if service is None:
      async with SessionLocal() as session:
        invite_repo = InviteSchoolRepository(session)
        profile_repo = ProfileRepository(session)
        service = ProfileService(
          profile_repository=profile_repo,
          invite_repository=invite_repo,
          session=session,
        )
        return await _execute_registration(service, input)

    return await _execute_registration(service, input)
