from enum import StrEnum


class JourneyStatus(StrEnum):
  PLANNED = "planned"
  IN_PROGRESS = "in_progress"
  ARRIVED_AT_SCHOOL = "arrived_at_school"
  COMPLETED = "completed"
