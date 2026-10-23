from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from apps.api.src.domains.exceptions import InvalidJourneyTransition
from apps.api.src.domains.journey_status import JourneyStatus


@dataclass(slots=True, kw_only=True)
class Journey:
  id: UUID
  student_id: UUID
  status: JourneyStatus = JourneyStatus.PLANNED
  started_at: datetime | None = None
  arrived_at: datetime | None = None

  @property
  def child_id(self) -> UUID:
    """Alias para compatibilidade com DTOs e eventos."""
    return self.student_id

  def start(self, when: datetime | None = None) -> None:
    if self.status is not JourneyStatus.PLANNED:
      raise InvalidJourneyTransition(
        f"Não é possível iniciar uma jornada no estado {self.status.value}"
      )
    self.status = JourneyStatus.IN_PROGRESS
    self.started_at = when or datetime.now(UTC)

  def arrive_at_school(self, when: datetime | None = None) -> None:
    if self.status is not JourneyStatus.IN_PROGRESS:
      raise InvalidJourneyTransition(
        f"Transição inválida: jornada no estado {self.status.value} não pode chegar à escola."
      )
    self.status = JourneyStatus.ARRIVED_AT_SCHOOL
    self.arrived_at = when or datetime.now(UTC)

  def complete(self) -> None:
    if self.status is not JourneyStatus.ARRIVED_AT_SCHOOL:
      raise InvalidJourneyTransition(
        f"Transição inválida: jornada precisa estar em {JourneyStatus.ARRIVED_AT_SCHOOL.value} para ser concluída."
      )
    self.status = JourneyStatus.COMPLETED
