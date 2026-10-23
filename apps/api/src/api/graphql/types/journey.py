from __future__ import annotations

from datetime import datetime
from typing import Annotated

import strawberry
from apps.api.src.domains.journey import Journey


@strawberry.type
class JourneyDTO:
  id: strawberry.ID
  child_id: strawberry.ID
  status: str
  started_at: datetime | None
  arrived_at: datetime | None

  @classmethod
  def from_domain(cls, journey: Journey) -> JourneyDTO:
    return cls(
      id=strawberry.ID(str(journey.id)),
      child_id=strawberry.ID(str(journey.child_id)),
      status=journey.status.value,
      started_at=journey.started_at,
      arrived_at=journey.arrived_at,
    )


# --- Erros de Domínio como Tipos do Schema ---


@strawberry.type
class JourneyNotFoundError:
  message: str
  journey_id: strawberry.ID


@strawberry.type
class JourneyAlreadyStartedError:
  message: str = "A jornada já foi iniciada anteriormente."


# Union de retorno da operação
StartJourneyResult = Annotated[
  JourneyDTO | JourneyNotFoundError | JourneyAlreadyStartedError,
  strawberry.union("StartJourneyResult"),
]
