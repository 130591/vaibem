import structlog
from apps.api.src.database.exceptions import (
  DatabaseConnectionError,
  RecordIntegrityError,
)
from graphql import GraphQLError
from strawberry.extensions import SchemaExtension

logger = structlog.get_logger(__name__)


class DatabaseErrorSanitizerExtension(SchemaExtension):
  async def on_operation(self):
    yield
    result = self.execution_context.result
    if not result or not result.errors:
      return

    sanitized_errors = []
    for err in result.errors:
      orig = err.original_error

      if isinstance(orig, DatabaseConnectionError):
        logger.critical("graphql_database_connection_failure", error=str(orig), exc_info=orig)
        sanitized_errors.append(
          GraphQLError(
            message="Serviço temporariamente indisponível. Tente novamente em instantes.",
            extensions={"code": "SERVICE_UNAVAILABLE"},
          )
        )

      elif isinstance(orig, RecordIntegrityError):
        logger.error("graphql_database_integrity_error", error=str(orig), exc_info=orig)
        sanitized_errors.append(
          GraphQLError(
            message="Conflito de integridade ao persistir os dados.",
            extensions={"code": "CONFLICT"},
          )
        )

      # GraphQLError (validações como o UUID) ou outros passam inalterados
      else:
        sanitized_errors.append(err)

    result.errors = sanitized_errors
