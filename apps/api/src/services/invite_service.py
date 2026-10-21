from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

from apps.api.src.constant import InviteStatus
from apps.api.src.domains.exceptions import (
    AlreadyUsedInviteError,
    InvalidExpiredError,
    InvalidInviteError,
    InviteNotFoundException,
)

if TYPE_CHECKING:
    from apps.api.src.database.models.invitation import SchoolInvitation
    from apps.api.src.database.repositories.invite_school_repository import (
        InviteSchoolRepository,
    )


class InviteService:
    def __init__(self, invite_repository: InviteSchoolRepository) -> None:
        self.invite_repository = invite_repository

    @staticmethod
    def calculate_hash(raw_token: str) -> str:
        return hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()

    async def validate(self, token: str) -> SchoolInvitation:
        token_hash = self.calculate_hash(token)
        entity = await self.invite_repository.get_by_token_hash(token_hash)

        if not entity:
            raise InviteNotFoundException()

        if entity.status == InviteStatus.ACCEPTED:
            raise AlreadyUsedInviteError()

        if entity.is_expired():
            raise InvalidExpiredError()

        if entity.status != InviteStatus.PENDING:
            raise InvalidInviteError(f"Convite inválido (status: {entity.status}).")

        return entity