import uuid

import pymysql
import pytest
from fastapi.testclient import TestClient

from database import repository
from database.schema import init_database
from findata_service.app import app


pytestmark = [pytest.mark.findata, pytest.mark.api]


@pytest.fixture
def client():
    try:
        init_database()
    except pymysql.MySQLError as error:
        pytest.skip(f"MySQL 测试数据库不可用：{error}")
    return TestClient(app)


def test_findata_db_watchlist_api(client):
    created_by = f"api_{uuid.uuid4().hex[:8]}"
    repository.clear_watchlist_items(created_by)

    create_response = client.post(
        "/api/db/watchlist",
        json={"item_type": "stock", "symbol": "600519", "name": "贵州茅台", "created_by": created_by},
    )
    list_response = client.get("/api/db/watchlist", params={"created_by": created_by})

    assert create_response.status_code == 200
    assert create_response.json()["data"]["symbol"] == "600519"
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]) == 1

    item_id = create_response.json()["data"]["item_id"]
    delete_response = client.delete(f"/api/db/watchlist/{item_id}")

    assert delete_response.status_code == 200
    assert client.get("/api/db/watchlist", params={"created_by": created_by}).json()["data"] == []


def test_findata_db_test_run_log_api(client):
    response = client.post(
        "/api/db/test-run-logs",
        json={
            "suite_name": "findata-db-api",
            "passed_count": 5,
            "failed_count": 0,
            "duration_seconds": 2.5,
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["suite_name"] == "findata-db-api"
