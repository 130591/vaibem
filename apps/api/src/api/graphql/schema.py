import strawberry
from apps.api.src.api.graphql.extensions import DatabaseErrorSanitizerExtension
from apps.api.src.api.graphql.mutation import Mutation
from apps.api.src.api.graphql.query import Query
from strawberry.fastapi import GraphQLRouter

schema = strawberry.Schema(
  query=Query,
  mutation=Mutation,
  extensions=[DatabaseErrorSanitizerExtension],
)

graphql_router = GraphQLRouter(schema)
