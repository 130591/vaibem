from __future__ import annotations

import strawberry
from apps.api.src.database.repositories.invite_school_repository import (
    InviteSchoolRepository,
)
from apps.api.src.database.session import SessionLocal
from apps.api.src.domains.exceptions import (
    AlreadyUsedInviteError,
    InvalidInviteError,
    InviteNotFoundException,
)
from apps.api.src.services.invite_service import InviteService
from graphql import GraphQLError
from strawberry.types import Info


@strawberry.type
class SchoolInvitationDTO:
    status: str
    school_name: str
    student_name: str
    guardian_email: str


async def _execute_validation(
    service: InviteService, clean_token: str
) -> SchoolInvitationDTO:
    try:
        entity = await service.validate(clean_token)
        return SchoolInvitationDTO(
            status=entity.status,
            school_name=entity.school.name,
            student_name=entity.student.name,
            guardian_email=entity.guardian_email,
        )
    except (
        InviteNotFoundException,
        AlreadyUsedInviteError,
        InvalidInviteError,
    ) as exc:
        code = getattr(exc, "code", "INVITATION_ERROR")
        raise GraphQLError(
            message=str(exc),
            extensions={"code": code},
        ) from exc


async def resolve_validate_school_invitation(
    info: Info, token: str
) -> SchoolInvitationDTO:
    if not isinstance(token, str):
        raise GraphQLError("Token inválido.", extensions={"code": "BAD_USER_INPUT"})

    clean_token = token.strip()
    if not clean_token or len(clean_token) > 128:
        raise GraphQLError(
            "Token vazio ou excede o limite permitido.",
            extensions={"code": "BAD_USER_INPUT"},
        )

    context = info.context if isinstance(info.context, dict) else {}
    service: InviteService | None = context.get("invite_service")

    if service is not None:
        return await _execute_validation(service, clean_token)

    async with SessionLocal() as session:
        repo = InviteSchoolRepository(session)
        service = InviteService(repo)
        return await _execute_validation(service, clean_token)
