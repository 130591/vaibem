from __future__ import annotations

from uuid import UUID

import strawberry
from apps.api.src.api.graphql.types.device import (
  DeviceTokenInput,
  DeviceTokenPayload,
  GuardianNotFoundError,
  InvalidDeviceTokenError,
  RegisterDeviceTokenResult,
)
from apps.api.src.database.repositories.device_repository import DeviceRepository
from apps.api.src.database.repositories.guardian_repository import GuardianRepository
from apps.api.src.database.session import SessionLocal
from apps.api.src.domains.exceptions import (
  GuardianNotFoundException,
  InvalidDeviceTokenException,
)
from apps.api.src.services.device_service import DeviceService
from graphql import GraphQLError
from strawberry.types import Info


@strawberry.type
class DeviceMutation:
  def __init__(self, device_service: DeviceService | None = None) -> None:
    self.device_service = device_service

  @strawberry.mutation
  async def register_device_token(
    self,
    info: Info,
    input: DeviceTokenInput,
  ) -> RegisterDeviceTokenResult:
    context = info.context or {} if info else {}
    current_user = context.get("current_user", {}) if isinstance(context, dict) else {}

    raw_guardian_id = input.guardian_id or (
      current_user.get("guardian_id") if isinstance(current_user, dict) else None
    )
    if not raw_guardian_id:
      raise GraphQLError(
        message="O identificador do responsável ('guardian_id') é obrigatório.",
        extensions={"code": "BAD_USER_INPUT", "argument": "guardian_id"},
      )

    try:
      parsed_guardian_id = UUID(str(raw_guardian_id))
    except (ValueError, AttributeError):
      raise GraphQLError(
        message="O 'guardian_id' fornecido não é um UUID válido.",
        extensions={"code": "BAD_USER_INPUT", "argument": "guardian_id"},
      )

    if not input.device_token:
      raise GraphQLError(
        message="O 'device_token' é obrigatório.",
        extensions={"code": "BAD_USER_INPUT", "argument": "device_token"},
      )

    service = getattr(self, "device_service", None)
    if service is None and info is not None:
      service = context.get("device_service") if isinstance(context, dict) else None

    async def _execute(svc: DeviceService) -> RegisterDeviceTokenResult:
      try:
        await svc.register_device(
          guardian_id=parsed_guardian_id,
          device_token=input.device_token,
          platform=input.platform,
        )
        return DeviceTokenPayload(success=True, notifications_enabled=True)
      except GuardianNotFoundException as exc:
        return GuardianNotFoundError(message=str(exc))
      except InvalidDeviceTokenException as exc:
        return InvalidDeviceTokenError(message=str(exc))

    if service is None:
      async with SessionLocal() as session:
        guardian_repo = GuardianRepository(session)
        device_repo = DeviceRepository(session)
        svc = DeviceService(
          guardian_repository=guardian_repo,
          device_repository=device_repo,
        )
        return await _execute(svc)

    return await _execute(service)
