from __future__ import annotations

from typing import Annotated

import strawberry


@strawberry.input
class DeviceTokenInput:
  platform: str
  device_token_snake: str | None = strawberry.field(name="device_token", default=None)
  device_token_camel: str | None = strawberry.field(name="deviceToken", default=None)
  guardian_id_snake: strawberry.ID | None = strawberry.field(name="guardian_id", default=None)
  guardian_id_camel: strawberry.ID | None = strawberry.field(name="guardianId", default=None)

  @property
  def device_token(self) -> str:
    return (self.device_token_snake or self.device_token_camel or "").strip()

  @property
  def guardian_id(self) -> strawberry.ID | None:
    return self.guardian_id_snake or self.guardian_id_camel


@strawberry.type
class DeviceTokenPayload:
  success: bool
  notifications_enabled: bool


@strawberry.type
class GuardianNotFoundError:
  message: str = "Responsável não encontrado."


@strawberry.type
class InvalidDeviceTokenError:
  message: str = "Token de dispositivo ou plataforma inválido."


RegisterDeviceTokenResult = Annotated[
  DeviceTokenPayload | GuardianNotFoundError | InvalidDeviceTokenError,
  strawberry.union("RegisterDeviceTokenResult"),
]
