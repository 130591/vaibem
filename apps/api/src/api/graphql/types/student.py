from __future__ import annotations

from typing import Annotated

import strawberry
from apps.api.src.database.models.student import Student


@strawberry.input
class StudentScheduleInput:
  home_address_input: str | None = strawberry.field(name="home_address", default=None)
  home_address_camel: str | None = strawberry.field(name="homeAddress", default=None)
  habitual_departure_input: str | None = strawberry.field(name="habitual_departure", default=None)
  habitual_departure_camel: str | None = strawberry.field(name="habitualDeparture", default=None)
  habitual_return_input: str | None = strawberry.field(name="habitual_return", default=None)
  habitual_return_camel: str | None = strawberry.field(name="habitualReturn", default=None)

  @property
  def home_address(self) -> str:
    return (self.home_address_input or self.home_address_camel or "").strip()

  @property
  def habitual_departure(self) -> str:
    return (self.habitual_departure_input or self.habitual_departure_camel or "").strip()

  @property
  def habitual_return(self) -> str:
    return (self.habitual_return_input or self.habitual_return_camel or "").strip()


@strawberry.type
class StudentRoutineDTO:
  home_address: str
  habitual_departure: str
  habitual_return: str
  active: bool


@strawberry.type
class StudentDTO:
  id: strawberry.ID
  name: str
  grade: str
  device_status: str
  routine: StudentRoutineDTO | None = None

  @classmethod
  def from_domain(cls, student: Student) -> StudentDTO:
    routine_dto = None
    if student.routine is not None:
      routine_dto = StudentRoutineDTO(
        home_address=student.routine.home_address,
        habitual_departure=student.routine.habitual_departure.strftime("%H:%M")
        if hasattr(student.routine.habitual_departure, "strftime")
        else str(student.routine.habitual_departure),
        habitual_return=student.routine.habitual_return.strftime("%H:%M")
        if hasattr(student.routine.habitual_return, "strftime")
        else str(student.routine.habitual_return),
        active=student.routine.active,
      )

    return cls(
      id=strawberry.ID(str(student.id)),
      name=student.name,
      grade=student.grade,
      device_status=student.device_status,
      routine=routine_dto,
    )


@strawberry.type
class StudentNotFoundError:
  message: str = "Aluno não encontrado."


@strawberry.type
class InvalidScheduleError:
  message: str = "Horário de rotina inválido."


UpdateStudentScheduleResult = Annotated[
  StudentDTO | StudentNotFoundError | InvalidScheduleError,
  strawberry.union("UpdateStudentScheduleResult"),
]
