from uuid import UUID


class DomainException(Exception):
  """Classe base para erros de regra de negócio."""


class JourneyNotFoundException(DomainException):
  def __init__(self, journey_id: UUID):
    self.journey_id = journey_id
    super().__init__(f"Jornada {journey_id} não encontrada.")


class JourneyAlreadyStartedException(DomainException):
  def __init__(self, journey_id: UUID):
    self.journey_id = journey_id
    super().__init__(f"Jornada {journey_id} já está em andamento.")

class InvalidJourneyTransition(DomainException):
  """Levantado quando uma transição de estado da jornada é inválida."""

  def __init__(self, message: str = "Transição de estado inválida para a jornada."):
    super().__init__(message)
