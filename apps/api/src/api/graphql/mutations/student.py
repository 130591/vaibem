from __future__ import annotations

from uuid import UUID

import strawberry
from apps.api.src.api.graphql.types.student import (
  InvalidScheduleError,
  StudentDTO,
  StudentNotFoundError,
  StudentScheduleInput,
  UpdateStudentScheduleResult,
)
from apps.api.src.database.repositories.student_repository import StudentRepository
from apps.api.src.database.session import SessionLocal
from apps.api.src.domains.exceptions import (
  InvalidScheduleException,
  StudentNotFoundException,
)
from apps.api.src.services.student_service import StudentService
from graphql import GraphQLError
from strawberry.types import Info


@strawberry.type
class StudentMutation:
  def __init__(self, student_service: StudentService | None = None) -> None:
    self.student_service = student_service

  @strawberry.mutation
  async def update_student_schedule(
    self,
    info: Info,
    student_id: strawberry.ID,
    input: StudentScheduleInput,
  ) -> UpdateStudentScheduleResult:
    try:
      parsed_student_id = UUID(str(student_id))
    except (ValueError, AttributeError):
      raise GraphQLError(
        message="O 'student_id' fornecido não é um UUID válido.",
        extensions={"code": "BAD_USER_INPUT", "argument": "student_id"},
      )

    if not input.home_address:
      raise GraphQLError(
        message="O endereço residencial é obrigatório.",
        extensions={"code": "BAD_USER_INPUT", "argument": "home_address"},
      )

    service = getattr(self, "student_service", None)
    if service is None and info is not None:
      context = info.context or {}
      service = context.get("student_service") if isinstance(context, dict) else None

    async def _execute(svc: StudentService) -> UpdateStudentScheduleResult:
      try:
        student = await svc.update_schedule(
          student_id=parsed_student_id,
          habitual_departure=input.habitual_departure,
          habitual_return=input.habitual_return,
          home_address=input.home_address,
        )
        return StudentDTO.from_domain(student)
      except StudentNotFoundException as exc:
        return StudentNotFoundError(message=str(exc))
      except InvalidScheduleException as exc:
        return InvalidScheduleError(message=str(exc))

    if service is None:
      async with SessionLocal() as session:
        repo = StudentRepository(session)
        svc = StudentService(repo)
        return await _execute(svc)

    return await _execute(service)
