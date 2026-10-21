from __future__ import annotations

from typing import Annotated

import strawberry
from apps.api.src.database.models.invitation import SchoolInvitation


@strawberry.type
class SchoolInvitationDTO:
  status: str
  school_name: str
  student_name: str
  guardian_email: str

  @classmethod
  def from_domain(cls, invitation: SchoolInvitation) -> SchoolInvitationDTO:
    return cls(
      status=invitation.status,
      school_name=invitation.school.name,
      student_name=invitation.student.name,
      guardian_email=invitation.guardian_email,
    )


# --- Erros de Domínio como Tipos do Schema ---


@strawberry.type
class InvitationNotFoundError:
  message: str = "Convite não encontrado."


@strawberry.type
class InvitationExpiredError:
  message: str = "Este convite expirou."


@strawberry.type
class InvitationAlreadyUsedError:
  message: str = "Este convite já foi utilizado."


@strawberry.type
class InvitationInvalidError:
  message: str = "Convite inválido."


# Union de retorno da operação
ValidateInvitationResult = Annotated[
  SchoolInvitationDTO
  | InvitationNotFoundError
  | InvitationExpiredError
  | InvitationAlreadyUsedError
  | InvitationInvalidError,
  strawberry.union("ValidateInvitationResult"),
]
