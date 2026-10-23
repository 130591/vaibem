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


class InviteNotFoundException(DomainException):
  """Levantado quando o convite não é encontrado pelo token informado."""

  code: str = "INVITATION_NOT_FOUND"

  def __init__(self, message: str = "Convite não encontrado."):
    super().__init__(message)


class InvalidExpiredError(DomainException):
  """Levantado quando o convite expirou no tempo."""

  code: str = "INVITATION_EXPIRED"

  def __init__(self, message: str = "Este convite expirou."):
    super().__init__(message)


class InvalidInviteError(DomainException):
  """Levantado para outras falhas na validação do convite."""

  code: str = "INVITATION_INVALID"

  def __init__(self, message: str = "Convite inválido."):
    super().__init__(message)


class AlreadyUsedInviteError(DomainException):
  """Levantado quando o convite já foi aceito/utilizado."""

  code: str = "INVITATION_ALREADY_USED"

  def __init__(self, message: str = "Este convite já foi utilizado."):
    super().__init__(message)


class AccountAlreadyExistsError(DomainException):
  """Levantado quando o responsável já possui conta/cadastro."""

  code: str = "ACCOUNT_EXISTS"

  def __init__(self, message: str = "Responsável já possui conta cadastrada."):
    super().__init__(message)
