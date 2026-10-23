from __future__ import annotations

from uuid import UUID

from apps.api.src.database.models.routine import Routine as RoutineModel
from apps.api.src.database.models.student import Student as StudentModel
from apps.api.src.database.repositories.base_repository import BaseRepository
from apps.api.src.domains.student import Routine as RoutineDomain
from apps.api.src.domains.student import Student as StudentDomain
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class StudentRepository(BaseRepository[StudentModel, StudentDomain]):
  model_cls = StudentModel
  entity_name = "Student"

  def _to_domain(self, model: StudentModel) -> StudentDomain:
    routine_domain = None
    if model.routine is not None:
      routine_domain = RoutineDomain(
        id=model.routine.id,
        student_id=model.routine.student_id,
        home_address=model.routine.home_address,
        habitual_departure=model.routine.habitual_departure,
        habitual_return=model.routine.habitual_return,
        active=model.routine.active,
      )

    return StudentDomain(
      id=model.id,
      name=model.name,
      grade=model.grade,
      device_status=model.device_status,
      routine=routine_domain,
    )

  async def find_by_id(self, student_id: UUID) -> StudentDomain | None:
    async with self._translate_db_errors(student_id=str(student_id)):
      stmt = (
        select(StudentModel)
        .options(joinedload(StudentModel.routine))
        .where(StudentModel.id == student_id)
      )
      result = await self.session.execute(stmt)
      model = result.scalar_one_or_none()
      return self._to_domain(model) if model is not None else None

  async def save(self, student: StudentDomain) -> None:
    async with self._translate_db_errors(student_id=str(student.id)):
      stmt = (
        select(StudentModel)
        .options(joinedload(StudentModel.routine))
        .where(StudentModel.id == student.id)
      )
      result = await self.session.execute(stmt)
      model = result.scalar_one_or_none()

      if model is None:
        model = StudentModel(
          id=student.id,
          name=student.name,
          grade=student.grade,
          device_status=student.device_status,
        )
        self.session.add(model)
      else:
        model.name = student.name
        model.grade = student.grade
        model.device_status = student.device_status

      if student.routine is not None:
        if model.routine is None:
          routine_model = RoutineModel(
            id=student.routine.id,
            student_id=student.id,
            home_address=student.routine.home_address,
            habitual_departure=student.routine.habitual_departure,
            habitual_return=student.routine.habitual_return,
            active=student.routine.active,
          )
          self.session.add(routine_model)
          model.routine = routine_model
        else:
          model.routine.home_address = student.routine.home_address
          model.routine.habitual_departure = student.routine.habitual_departure
          model.routine.habitual_return = student.routine.habitual_return
          model.routine.active = student.routine.active

      await self.session.commit()
