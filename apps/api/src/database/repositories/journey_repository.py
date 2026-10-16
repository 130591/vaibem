
from apps.api.src.database.models.journey import JourneyModel
from apps.api.src.database.repositories.base_repository import BaseRepository
from apps.api.src.domains.journey import Journey
from apps.api.src.domains.journey_status import JourneyStatus


class JourneyRepository(BaseRepository[JourneyModel, Journey]):
    model_cls = JourneyModel
    entity_name = "Journey"

    async def save(self, journey: Journey) -> None:
        async with self._translate_db_errors(journey_id=str(journey.id)):
            model = await self.session.get(JourneyModel, journey.id)
            if model is None:
                model = JourneyModel(id=journey.id, student_id=journey.student_id)
                self.session.add(model)

            model.student_id = journey.student_id
            model.left_home = journey.started_at
            model.arrived_time = journey.arrived_at
            await self.session.commit()

    def _to_domain(self, model: JourneyModel) -> Journey:
        raw = getattr(model.status, "status_lost_name", model.status)
        try:
            status = JourneyStatus(raw)
        except ValueError:
            status = JourneyStatus.PLANNED

        return Journey(
            id=model.id,
            student_id=model.student_id,
            status=status,
            started_at=model.left_home,
            arrived_at=model.arrived_time,
        )