from __future__ import annotations

import strawberry
from apps.api.src.api.graphql.extensions import DatabaseErrorSanitizerExtension
from apps.api.src.api.graphql.mutation import Mutation
from apps.api.src.api.graphql.query import Query
from apps.api.src.security import decode_token
from fastapi import Request
from strawberry.fastapi import GraphQLRouter


async def get_context(request: Request) -> dict:
  context = {"request": request}
  auth_header = request.headers.get("Authorization")
  if auth_header and auth_header.startswith("Bearer "):
    raw_token = auth_header.split(" ", 1)[1].strip()
    try:
      context["current_user"] = decode_token(raw_token)
    except Exception:  # noqa: BLE001
      context["current_user"] = None
  return context


schema = strawberry.Schema(
  query=Query,
  mutation=Mutation,
  extensions=[DatabaseErrorSanitizerExtension],
)

graphql_router = GraphQLRouter(schema, context_getter=get_context)
