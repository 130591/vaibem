from __future__ import annotations

import strawberry
from apps.api.src.api.graphql.mutations.account import RegisterGuardianMutation
from apps.api.src.api.graphql.mutations.device import DeviceMutation
from apps.api.src.api.graphql.mutations.journey import Mutation as JourneyMutation
from apps.api.src.api.graphql.mutations.student import StudentMutation


@strawberry.type
class Mutation(JourneyMutation, RegisterGuardianMutation, StudentMutation, DeviceMutation):
  pass


__all__ = ["Mutation"]
