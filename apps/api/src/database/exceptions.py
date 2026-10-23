class RepositoryError(Exception):
  """Erro base para falhas na camada de persistência."""


class RecordNotFoundError(RepositoryError):
  """Levantado quando um registro esperado não é encontrado."""


class DatabaseConnectionError(RepositoryError):
  """Levantado quando não é possível falar com o banco (conexão caiu,
  timeout, pool esgotado, etc.)."""


class RecordIntegrityError(RepositoryError):
  """Levantado quando uma constraint do banco é violada (FK inválida,
  unique constraint, not null, etc.)."""
