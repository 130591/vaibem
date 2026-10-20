import pytest
from apps.api.src.database.session import engine

pytest_plugins = [
  "apps.api.tests.fixtures.invitations",
  "apps.api.tests.fixtures.client"
]


@pytest.fixture(autouse=True)
async def cleanup_database_pool():
  yield
  await engine.dispose()
