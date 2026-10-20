import httpx
import pytest
from apps.api.src.main import app


@pytest.fixture
async def client():
  transport = httpx.ASGITransport(app=app)
  async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
    yield client