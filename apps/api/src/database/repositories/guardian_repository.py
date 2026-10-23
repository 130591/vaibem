from apps.api.src.database.models.guardian import GuardianModel
from apps.api.src.database.repositories.base_repository import BaseRepository
from apps.api.src.domains.guardian import Guardian


class GuardianRepository(BaseRepository[GuardianModel, Guardian]):
  model_cls = Guardian
  entity_name = "guardian"

  def _to_domain(self, model: GuardianModel) -> Guardian:
    return model
