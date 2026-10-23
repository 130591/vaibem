from datetime import UTC, datetime
from uuid import uuid4

import pytest
from apps.api.src.domains.exceptions import InvalidJourneyTransition
from apps.api.src.domains.journey import Journey
from apps.api.src.domains.journey_status import JourneyStatus


def test_journey_initialization():
  journey_id = uuid4()
  student_id = uuid4()
  journey = Journey(id=journey_id, student_id=student_id)

  assert journey.id == journey_id
  assert journey.student_id == student_id
  assert journey.child_id == student_id
  assert journey.status == JourneyStatus.PLANNED
  assert journey.started_at is None
  assert journey.arrived_at is None


def test_start_journey_success():
  journey = Journey(id=uuid4(), student_id=uuid4())
  now = datetime.now(UTC)

  journey.start(when=now)

  assert journey.status == JourneyStatus.IN_PROGRESS
  assert journey.started_at == now


def test_start_journey_already_started_raises_exception():
  journey = Journey(
    id=uuid4(),
    student_id=uuid4(),
    status=JourneyStatus.IN_PROGRESS,
    started_at=datetime.now(UTC),
  )

  with pytest.raises(InvalidJourneyTransition) as exc_info:
    journey.start()

  assert "Não é possível iniciar uma jornada no estado in_progress" in str(exc_info.value)


def test_arrive_at_school_success():
  journey = Journey(id=uuid4(), student_id=uuid4())
  journey.start()

  arrival_time = datetime.now(UTC)
  journey.arrive_at_school(when=arrival_time)

  assert journey.status == JourneyStatus.ARRIVED_AT_SCHOOL
  assert journey.arrived_at == arrival_time


def test_arrive_at_school_from_planned_raises_exception():
  journey = Journey(id=uuid4(), student_id=uuid4())

  with pytest.raises(InvalidJourneyTransition):
    journey.arrive_at_school()


def test_complete_journey_success():
  journey = Journey(id=uuid4(), student_id=uuid4())
  journey.start()
  journey.arrive_at_school()

  journey.complete()

  assert journey.status == JourneyStatus.COMPLETED
