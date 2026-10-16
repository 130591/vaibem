from apps.api.src.api.graphql.schema import graphql_router
from apps.api.src.api.health_check import router as health_router
from apps.api.src.config import settings
from fastapi import FastAPI

app = FastAPI(
  title=settings.app_title,
  version=settings.app_version,
)

app.include_router(graphql_router, prefix="/graphql")

app.include_router(health_router)


@app.get("/")
async def root():
  return {
    "title": settings.app_title,
    "version": settings.app_version,
    "graphql": "/graphql",
    "health": "/health",
  }
