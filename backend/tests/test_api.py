"""
Integration tests for Groww Lens FastAPI endpoints.
Tests complete request-response flow for Watchlists and Dashboard.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import UUID

from app.main import app
from app.database.session import engine, Base


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_watchlists_crud_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as client:
        # 1. Create a watchlist
        create_res = await client.post(
            "/watchlists/",
            json={"name": "EV Tech Leaders", "description": "Future mobility stocks"}
        )
        assert create_res.status_code == 201
        wl = create_res.json()
        assert wl["name"] == "EV Tech Leaders"
        watchlist_id = wl["id"]

        # 2. Add stocks to the watchlist
        stock_res = await client.post(
            f"/watchlists/{watchlist_id}/stocks",
            json={"symbol": "TATAMOTORS.NS", "company_name": "Tata Motors Limited"}
        )
        assert stock_res.status_code == 201
        assert stock_res.json()["symbol"] == "TATAMOTORS.NS"

        # 3. List stocks
        list_stocks_res = await client.get(f"/watchlists/{watchlist_id}/stocks")
        assert list_stocks_res.status_code == 200
        stocks = list_stocks_res.json()
        assert len(stocks) == 1
        assert stocks[0]["symbol"] == "TATAMOTORS.NS"

        # 4. List watchlists
        list_wl_res = await client.get("/watchlists/")
        assert list_wl_res.status_code == 200
        watchlists = list_wl_res.json()
        assert any(w["id"] == watchlist_id for w in watchlists)

        # 5. Delete watchlist
        del_res = await client.delete(f"/watchlists/{watchlist_id}")
        assert del_res.status_code == 200
        assert del_res.json()["success"] is True


@pytest.mark.asyncio
async def test_dashboard_pulse_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as client:
        res = await client.get("/dashboard/pulse")
        assert res.status_code == 200
        data = res.json()
        assert "market_mood" in data
        assert "strongest_sector" in data


@pytest.mark.asyncio
async def test_dashboard_while_away_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as client:
        res = await client.get("/dashboard/while-away")
        assert res.status_code == 200
        data = res.json()
        assert "stats" in data
        assert "events" in data
        assert "total_events" in data["stats"]
        assert "hours_away" in data["stats"]
        assert isinstance(data["events"], list)
