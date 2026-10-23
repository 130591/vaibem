from __future__ import annotations

from datetime import datetime, time
from uuid import UUID

from apps.api.src.database.repositories.student_repository import StudentRepository
from apps.api.src.domains.exceptions import (
  InvalidScheduleException,
  StudentNotFoundException,
)
from apps.api.src.domains.student import Student


class StudentService:
  def __init__(self, student_repository: StudentRepository) -> None:
    self.student_repository = student_repository

  @staticmethod
  def parse_time(time_str: str) -> time:
    try:
      return datetime.strptime(time_str.strip(), "%H:%M").time()
    except ValueError:
      raise InvalidScheduleException(
        f"Formato de horário inválido: '{time_str}'. Esperado 'HH:MM'."
      )

  async def update_schedule(
    self,
    student_id: UUID,
    habitual_departure: str,
    habitual_return: str,
    home_address: str,
  ) -> Student:
    dep_time = self.parse_time(habitual_departure)
    ret_time = self.parse_time(habitual_return)

    student = await self.student_repository.find_by_id(student_id)
    if student is None:
      raise StudentNotFoundException()

    student.update_schedule(
      home_address=home_address,
      habitual_departure=dep_time,
      habitual_return=ret_time,
    )

    await self.student_repository.save(student)
    return student
