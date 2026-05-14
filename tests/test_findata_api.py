import pytest
from fastapi.testclient import TestClient

from findata_service.app import app, service


pytestmark = [pytest.mark.findata, pytest.mark.api]


@pytest.fixture
def client():
    service.watchlist.clear()
    service.holdings.clear()
    return TestClient(app)


def test_findata_health_api(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"


def test_findata_stock_realtime_api(client):
    response = client.get("/api/stock/realtime", params={"symbol": "600519"})
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["symbol"] == "600519"
    assert body["data"]["source"] == "mock"


def test_findata_watchlist_api_crud(client):
    create_response = client.post(
        "/api/watchlist",
        json={"item_type": "stock", "symbol": "600519", "name": "贵州茅台"},
    )
    created = create_response.json()["data"]

    assert create_response.status_code == 200
    assert created["symbol"] == "600519"

    list_response = client.get("/api/watchlist")
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]) == 1

    delete_response = client.delete(f"/api/watchlist/{created['item_id']}")
    assert delete_response.status_code == 200
    assert client.get("/api/watchlist").json()["data"] == []


def test_findata_portfolio_and_risk_api(client):
    holding_response = client.post(
        "/api/portfolio/holding",
        json={"item_type": "stock", "symbol": "600519", "quantity": 1, "cost_price": 1600},
    )
    summary_response = client.get("/api/portfolio/summary")
    risk_response = client.get("/api/risk/alerts")

    assert holding_response.status_code == 200
    assert summary_response.json()["data"]["total_market_value"] > 0
    assert risk_response.status_code == 200
    assert risk_response.json()["data"]


def test_findata_login_and_dashboard_flow(client):
    login_response = client.post(
        "/api/auth/login",
        json={"username": "tester", "password": "tester123"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["success"] is True
    assert client.get("/dashboard").status_code == 200


def test_findata_login_rejects_wrong_password(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "tester", "password": "bad-password"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_LOGIN"
