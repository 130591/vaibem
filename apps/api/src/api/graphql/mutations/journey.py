from uuid import UUID

import strawberry
from apps.api.src.api.graphql.types.journey import (
  JourneyAlreadyStartedError,
  JourneyDTO,
  JourneyNotFoundError,
  StartJourneyResult,
)
from apps.api.src.database.exceptions import RecordNotFoundError
from apps.api.src.domains.exceptions import (
  InvalidJourneyTransition,
  JourneyAlreadyStartedException,
  JourneyNotFoundException,
)
from graphql import GraphQLError
from strawberry.types import Info


@strawberry.type
class Mutation:
  def __init__(self, journey_service=None):
    self.journey_service = journey_service

  @strawberry.mutation
  async def start_journey(
    self, info: Info, journey_id: strawberry.ID
  ) -> StartJourneyResult:
    service = self.journey_service
    if service is None and info is not None:
      context = info.context or {}
      service = (
        context.get("journey_service") if isinstance(context, dict) else None
      )

    if service is None:
      raise GraphQLError("JourneyService não configurado no contexto.")

    try:
      parsed_uuid = UUID(str(journey_id))
    except (ValueError, AttributeError):
      raise GraphQLError(
        message="O 'journey_id' fornecido não é um UUID válido.",
        extensions={"code": "BAD_USER_INPUT", "argument": "journey_id"},
      )

    try:
      journey = await service.start_journey(parsed_uuid)
      return JourneyDTO.from_domain(journey)

    except (RecordNotFoundError, JourneyNotFoundException):
      return JourneyNotFoundError(
        message=f"Jornada {journey_id} não encontrada.",
        journey_id=journey_id,
      )

    except (JourneyAlreadyStartedException, InvalidJourneyTransition) as exc:
      return JourneyAlreadyStartedError(message=str(exc))
