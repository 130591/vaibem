from uuid import UUID

import structlog
from apps.api.src.database.exceptions import (
  DatabaseConnectionError,
  RecordIntegrityError,
  RecordNotFoundError,
)
from apps.api.src.database.models.journey import JourneyModel
from apps.api.src.domains.journey import Journey
from apps.api.src.domains.journey_status import JourneyStatus
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)


class JourneyRepository:
  def __init__(self, session: AsyncSession):
    self.session = session

  async def get(self, journey_id: UUID) -> Journey:
    try:
      result = await self.session.execute(
        select(JourneyModel).where(
          JourneyModel.id == journey_id
        )
      )
      model = result.scalar_one()

    except NoResultFound as exc:
      logger.warning("journey_not_found", journey_id=str(journey_id))
      raise RecordNotFoundError(
        f"Journey {journey_id} não encontrada"
      ) from exc

    except OperationalError as exc:
      logger.error(
        "database_connection_error", journey_id=str(journey_id), error=str(exc)
      )
      raise DatabaseConnectionError(
        "Não foi possível conectar ao banco de dados"
      ) from exc

    except SQLAlchemyError as exc:
      logger.error(
        "unexpected_database_error", journey_id=str(journey_id), error=str(exc)
      )
      raise

    status_val = JourneyStatus.PLANNED
    if hasattr(model, "status") and model.status is not None:
      if isinstance(model.status, str):
        status_val = JourneyStatus(model.status)
      elif hasattr(model.status, "status_lost_name"):
        try:
          status_val = JourneyStatus(model.status.status_lost_name)
        except ValueError:
          status_val = JourneyStatus.PLANNED

    return Journey(
      id=model.id,
      student_id=model.student_id,
      status=status_val,
      started_at=model.left_home,
      arrived_at=model.arrived_time,
    )

  async def save(self, journey: Journey) -> None:
    try:
      model = await self.session.get(
        JourneyModel,
        journey.id,
      )

      if model is None:
        model = JourneyModel(
          id=journey.id,
          student_id=journey.student_id,
        )
        self.session.add(model)

      model.student_id = journey.student_id
      model.left_home = journey.started_at
      model.arrived_time = journey.arrived_at

      await self.session.commit()


    except IntegrityError as exc:
      await self.session.rollback()
      logger.warning(
        "journey_integrity_violation", journey_id=str(journey.id), error=str(exc)
      )
      raise RecordIntegrityError(
        f"Violação de integridade ao salvar journey {journey.id}"
      ) from exc

    except OperationalError as exc:
      await self.session.rollback()
      logger.error(
        "database_connection_error", journey_id=str(journey.id), error=str(exc)
      )
      raise DatabaseConnectionError(
        "Não foi possível conectar ao banco de dados"
      ) from exc

    except SQLAlchemyError as exc:
      await self.session.rollback()
      logger.error(
        "unexpected_database_error", journey_id=str(journey.id), error=str(exc)
      )
      raise