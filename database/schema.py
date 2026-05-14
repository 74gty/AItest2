from database.connection import get_connection


CREATE_FINDATA_USERS = """
CREATE TABLE IF NOT EXISTS findata_users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(64) NOT NULL UNIQUE,
    display_name VARCHAR(128) NOT NULL,
    role_name VARCHAR(32) NOT NULL DEFAULT 'tester',
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

CREATE_FINDATA_WATCHLIST = """
CREATE TABLE IF NOT EXISTS findata_watchlist (
    item_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    item_type VARCHAR(16) NOT NULL,
    symbol VARCHAR(32) NOT NULL,
    name VARCHAR(128) NOT NULL,
    created_by VARCHAR(64) NOT NULL DEFAULT 'tester',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_findata_watchlist_symbol (item_type, symbol, created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

CREATE_TEST_RUN_LOGS = """
CREATE TABLE IF NOT EXISTS test_run_logs (
    run_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    suite_name VARCHAR(128) NOT NULL,
    passed_count INT NOT NULL DEFAULT 0,
    failed_count INT NOT NULL DEFAULT 0,
    duration_seconds DECIMAL(10, 3) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


def init_database():
    # 建表语句可重复执行，适合本地和 CI 测试前初始化
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_FINDATA_USERS)
            cursor.execute(CREATE_FINDATA_WATCHLIST)
            cursor.execute(CREATE_TEST_RUN_LOGS)
        connection.commit()

