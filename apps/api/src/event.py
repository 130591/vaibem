from dataclasses import dataclass
from uuid import UUID


@dataclass
class JourneyStarted:
  journey_id: UUID
  child_id: UUID
