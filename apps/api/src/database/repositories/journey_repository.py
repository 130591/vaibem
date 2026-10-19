
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
                model = JourneyModel(
                    id=journey.id,
                    student_id=journey.student_id,
                    status=journey.status,
                )
                self.session.add(model)

            model.student_id = journey.student_id
            model.status = journey.status
            model.left_home = journey.started_at
            model.arrived_time = journey.arrived_at
            await self.session.commit()

    def _to_domain(self, model: JourneyModel) -> Journey:
        status = JourneyStatus(model.status) if isinstance(model.status, str) else model.status
        return Journey(
            id=model.id,
            student_id=model.student_id,
            status=status,
            started_at=model.left_home,
            arrived_at=model.arrived_time,
        )