import uuid

import pymysql
import pytest

from database import repository
from database.connection import get_connection
from database.schema import init_database


pytestmark = [pytest.mark.findata, pytest.mark.api]


@pytest.fixture(scope="module", autouse=True)
def mysql_ready():
    try:
        init_database()
    except pymysql.MySQLError as error:
        pytest.skip(f"MySQL 测试数据库不可用：{error}")


def test_mysql_tables_are_initialized():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE 'findata_watchlist'")
            watchlist_table = cursor.fetchone()
            cursor.execute("SHOW TABLES LIKE 'test_run_logs'")
            test_run_table = cursor.fetchone()

    assert watchlist_table
    assert test_run_table


def test_mysql_user_upsert_and_query():
    username = f"tester_{uuid.uuid4().hex[:8]}"

    user = repository.upsert_user(username, "数据库测试用户", role_name="qa")
    queried = repository.get_user(username)

    assert user["username"] == username
    assert queried["display_name"] == "数据库测试用户"
    assert queried["role_name"] == "qa"


def test_mysql_watchlist_crud():
    created_by = f"case_{uuid.uuid4().hex[:8]}"
    repository.clear_watchlist_items(created_by)

    item = repository.add_watchlist_item("stock", "600519", "贵州茅台", created_by)
    rows = repository.list_watchlist_items(created_by)
    deleted = repository.delete_watchlist_item(item["item_id"])

    assert item["symbol"] == "600519"
    assert len(rows) == 1
    assert rows[0]["name"] == "贵州茅台"
    assert deleted["item_id"] == item["item_id"]
    assert repository.list_watchlist_items(created_by) == []


def test_mysql_records_test_run_log():
    log = repository.add_test_run_log(
        suite_name="findata-mysql-demo",
        passed_count=3,
        failed_count=0,
        duration_seconds=1.25,
    )

    assert log["suite_name"] == "findata-mysql-demo"
    assert log["passed_count"] == 3
    assert log["failed_count"] == 0
