from datetime import UTC, datetime
from uuid import UUID

from apps.api.src.database.exceptions import RecordNotFoundError
from apps.api.src.domains.exceptions import JourneyNotFoundException
from apps.api.src.domains.journey import Journey
from apps.api.src.event import JourneyStarted


class JourneyService:
  def __init__(self, journey_repository, event_publisher):
    self.journey_repository = journey_repository
    self.event_publisher = event_publisher

  async def start_journey(self, journey_id: UUID) -> Journey:
    try:
      journey = await self.journey_repository.get(journey_id)
    except RecordNotFoundError as exc:
      raise JourneyNotFoundException(journey_id) from exc

    journey.start(datetime.now(UTC))
    await self.journey_repository.save(journey)

    await self.event_publisher.publish(
      JourneyStarted(
        journey_id=journey.id,
        child_id=journey.child_id,
      )
    )

    return journey
