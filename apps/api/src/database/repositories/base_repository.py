from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TypeVar
from uuid import UUID

import structlog
from apps.api.src.database.base import Base
from apps.api.src.database.exceptions import (
  DatabaseConnectionError,
  RecordIntegrityError,
  RecordNotFoundError,
)
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

ModelT = TypeVar("ModelT", bound=Base)
DomainT = TypeVar("DomainT")


class BaseRepository[ModelT: Base, DomainT](ABC):
  model_cls: type[ModelT]
  entity_name: str

  def __init__(self, session: AsyncSession):
    self.session = session

  @asynccontextmanager
  async def _translate_db_errors(self, **log_ctx) -> AsyncIterator[None]:
    try:
      yield
    except IntegrityError as exc:
      await self.session.rollback()
      logger.warning("integrity_violation", error=str(exc), **log_ctx)
      raise RecordIntegrityError("Violação de integridade") from exc
    except OperationalError as exc:
      await self.session.rollback()
      logger.error("database_connection_error", error=str(exc), **log_ctx)
      raise DatabaseConnectionError("Não foi possível conectar ao banco de dados") from exc
    except SQLAlchemyError:
      await self.session.rollback()
      logger.exception("unexpected_database_error", **log_ctx)
      raise

  async def get(self, entity_id: UUID) -> DomainT:
    async with self._translate_db_errors(entity_id=str(entity_id)):
      model = await self.session.get(self.model_cls, entity_id)

    if model is None:
      logger.warning("not_found", entity=self.entity_name, entity_id=str(entity_id))
      raise RecordNotFoundError(f"{self.entity_name} {entity_id} não encontrada")

    return self._to_domain(model)

  @abstractmethod
  def _to_domain(self, model: ModelT) -> DomainT: ...
