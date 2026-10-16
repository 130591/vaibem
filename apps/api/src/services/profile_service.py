from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(slots=True)
class Profile:
  id: UUID
  name: str
  email: str


class ProfileService:
  def __init__(self, profile_repository: Any = None):
    self.profile_repository = profile_repository

  async def get_profile_by_id(self, guardian_id: UUID) -> Profile | None:
    if self.profile_repository is None:
      return None
    profile = await self.profile_repository.get(guardian_id)
    return profile