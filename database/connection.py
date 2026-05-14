import os

import pymysql

from utils.config_loader import load_config


def mysql_config():
    config = load_config()
    return {
        "host": os.getenv("MYSQL_HOST") or config.get("mysql_host") or "127.0.0.1",
        "port": int(os.getenv("MYSQL_PORT") or config.get("mysql_port") or 3306),
        "user": os.getenv("MYSQL_USER") or config.get("mysql_user") or "eutl",
        "password": os.getenv("MYSQL_PASSWORD") or config.get("mysql_password") or "eutl123456",
        "database": os.getenv("MYSQL_DATABASE") or config.get("mysql_database") or "eutl_test",
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": False,
    }


def get_connection():
    # 统一创建 MySQL 连接，便于测试环境切换账号和数据库
    return pymysql.connect(**mysql_config())
