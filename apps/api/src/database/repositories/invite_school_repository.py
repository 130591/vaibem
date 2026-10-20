from apps.api.src.database.models.invitation import SchoolInvitation
from apps.api.src.database.repositories.base_repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class InviteSchoolRepository(BaseRepository[SchoolInvitation, SchoolInvitation]):
  model_cls = SchoolInvitation
  entity_name = "school_invitations"

  def _to_domain(self, model: SchoolInvitation) -> SchoolInvitation:
    return model

  async def get_by_token_hash(self, token_hash: str) -> SchoolInvitation | None:
    async with self._translate_db_errors():
      stmt = (
        select(SchoolInvitation)
        .options(
          joinedload(SchoolInvitation.school),
          joinedload(SchoolInvitation.student),
        )
        .where(SchoolInvitation.token_hash == token_hash)
      )
      result = await self.session.execute(stmt)
      model = result.scalar_one_or_none()
      return self._to_domain(model) if model is not None else None