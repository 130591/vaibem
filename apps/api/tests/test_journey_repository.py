from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from apps.api.src.database.exceptions import RecordNotFoundError
from apps.api.src.database.models.journey import JourneyModel
from apps.api.src.database.models.journey_status import (
  JourneyStatus as JourneyStatusModel,
)
from apps.api.src.database.repositories.journey_repository import (
  JourneyRepository,
)
from apps.api.src.domains.journey import Journey, JourneyStatus


@pytest.mark.asyncio
async def test_journey_repository_get_success():
  mock_session = AsyncMock()
  repo = JourneyRepository(mock_session)

  journey_id = uuid4()
  student_id = uuid4()
  now = datetime.now(UTC)

  status_model = JourneyStatusModel(
    id=1,
    status_lost_name="in_progress",
    status_lost_message="Em andamento",
  )

  model = JourneyModel(
    id=journey_id,
    student_id=student_id,
    left_home=now,
    arrived_time=None,
    status=status_model,
  )

  mock_session.get.return_value = model

  journey = await repo.get(journey_id)

  assert isinstance(journey, Journey)
  assert journey.id == journey_id
  assert journey.student_id == student_id
  assert journey.status == JourneyStatus.IN_PROGRESS
  assert journey.started_at == now
  mock_session.get.assert_awaited_once_with(JourneyModel, journey_id)


@pytest.mark.asyncio
async def test_journey_repository_get_not_found():
  mock_session = AsyncMock()
  mock_session.get.return_value = None

  repo = JourneyRepository(mock_session)
  journey_id = uuid4()

  with pytest.raises(RecordNotFoundError) as exc_info:
    await repo.get(journey_id)

  assert f"Journey {journey_id} não encontrada" in str(exc_info.value)


@pytest.mark.asyncio
async def test_journey_repository_save():
  mock_session = AsyncMock()
  mock_session.add = MagicMock()
  mock_session.get.return_value = None

  repo = JourneyRepository(mock_session)
  journey_id = uuid4()
  student_id = uuid4()
  now = datetime.now(UTC)

  journey = Journey(
    id=journey_id,
    student_id=student_id,
    status=JourneyStatus.IN_PROGRESS,
    started_at=now,
  )

  await repo.save(journey)

  mock_session.add.assert_called_once()
  mock_session.commit.assert_awaited_once()
