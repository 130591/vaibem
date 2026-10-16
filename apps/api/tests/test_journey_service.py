from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from apps.api.src.database.exceptions import RecordNotFoundError
from apps.api.src.domains.exceptions import JourneyNotFoundException
from apps.api.src.domains.journey import Journey
from apps.api.src.domains.journey_status import JourneyStatus
from apps.api.src.event import JourneyStarted
from apps.api.src.services.journey_service import JourneyService


@pytest.mark.asyncio
async def test_start_journey_service_success():
  journey_id = uuid4()
  student_id = uuid4()
  planned_journey = Journey(id=journey_id, student_id=student_id)

  mock_repository = AsyncMock()
  mock_repository.get.return_value = planned_journey
  mock_repository.save = AsyncMock()

  mock_publisher = AsyncMock()
  mock_publisher.publish = AsyncMock()

  service = JourneyService(
    journey_repository=mock_repository,
    event_publisher=mock_publisher,
  )

  started_journey = await service.start_journey(journey_id)

  assert started_journey.status == JourneyStatus.IN_PROGRESS
  assert started_journey.started_at is not None

  mock_repository.get.assert_awaited_once_with(journey_id)
  mock_repository.save.assert_awaited_once_with(planned_journey)

  mock_publisher.publish.assert_awaited_once()
  event_arg = mock_publisher.publish.await_args[0][0]
  assert isinstance(event_arg, JourneyStarted)
  assert event_arg.journey_id == journey_id
  assert event_arg.child_id == student_id


@pytest.mark.asyncio
async def test_start_journey_service_not_found():
  journey_id = uuid4()

  mock_repository = AsyncMock()
  mock_repository.get.side_effect = RecordNotFoundError("Not found")

  mock_publisher = AsyncMock()

  service = JourneyService(
    journey_repository=mock_repository,
    event_publisher=mock_publisher,
  )

  with pytest.raises(JourneyNotFoundException) as exc_info:
    await service.start_journey(journey_id)

  assert exc_info.value.journey_id == journey_id
