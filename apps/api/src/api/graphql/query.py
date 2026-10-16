from __future__ import annotations

from uuid import UUID

import strawberry
from strawberry.types import Info


@strawberry.type
class ProfileDTO:
  id: strawberry.ID
  name: str
  email: str


@strawberry.type
class Query:
  @strawberry.field
  def health(self) -> str:
    return "ok"

  @strawberry.field
  async def profile(
    self, info: Info, guardian_id: strawberry.ID
  ) -> ProfileDTO | None:
    context = info.context or {}
    profile_service = (
      context.get("profile_service") if isinstance(context, dict) else None
    )
    if not profile_service:
      return None

    try:
      parsed_uuid = UUID(str(guardian_id))
    except (ValueError, AttributeError):
      return None

    profile = await profile_service.get_profile_by_id(parsed_uuid)
    if not profile:
      return None

    return ProfileDTO(
      id=strawberry.ID(str(profile.id)),
      name=profile.name,
      email=profile.email,
    )