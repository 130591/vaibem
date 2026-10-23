import httpx
import pytest
from apps.api.src.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint():
  transport = httpx.ASGITransport(app=app)
  async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_root_endpoint():
  transport = httpx.ASGITransport(app=app)
  async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "graphql" in data
    assert "health" in data


@pytest.mark.asyncio
async def test_graphql_health_query():
  transport = httpx.ASGITransport(app=app)
  async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
    response = await client.post(
      "/graphql",
      json={"query": "{ health }"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["health"] == "ok"
