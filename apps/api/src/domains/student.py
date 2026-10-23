from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from uuid import UUID, uuid4

from apps.api.src.domains.exceptions import InvalidScheduleException


@dataclass(slots=True)
class Routine:
  id: UUID
  student_id: UUID
  home_address: str
  habitual_departure: time
  habitual_return: time
  active: bool = True

  def update(
    self,
    home_address: str,
    habitual_departure: time,
    habitual_return: time,
  ) -> None:
    if habitual_departure >= habitual_return:
      raise InvalidScheduleException(
        "O horário habitual de volta deve ser posterior ao horário de saída."
      )
    clean_address = home_address.strip()
    if not clean_address:
      raise InvalidScheduleException("O endereço residencial não pode ser vazio.")
    self.home_address = clean_address
    self.habitual_departure = habitual_departure
    self.habitual_return = habitual_return
    self.active = True


@dataclass(slots=True)
class Student:
  id: UUID
  name: str
  grade: str
  device_status: str
  routine: Routine | None = None

  def update_schedule(
    self,
    home_address: str,
    habitual_departure: time,
    habitual_return: time,
  ) -> None:
    if self.routine is not None:
      self.routine.update(
        home_address=home_address,
        habitual_departure=habitual_departure,
        habitual_return=habitual_return,
      )
    else:
      if habitual_departure >= habitual_return:
        raise InvalidScheduleException(
          "O horário habitual de volta deve ser posterior ao horário de saída."
        )
      clean_address = home_address.strip()
      if not clean_address:
        raise InvalidScheduleException("O endereço residencial não pode ser vazio.")
      self.routine = Routine(
        id=uuid4(),
        student_id=self.id,
        home_address=clean_address,
        habitual_departure=habitual_departure,
        habitual_return=habitual_return,
        active=True,
      )
