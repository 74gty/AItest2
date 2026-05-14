import pymysql

from utils.config_loader import load_config


def mysql_config():
    config = load_config()
    return {
        "host": config.get("mysql_host", "127.0.0.1"),
        "port": int(config.get("mysql_port", 3306)),
        "user": config.get("mysql_user", "eutl"),
        "password": config.get("mysql_password", "eutl123456"),
        "database": config.get("mysql_database", "eutl_test"),
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": False,
    }


def get_connection():
    # 统一创建 MySQL 连接，便于测试环境切换账号和数据库
    return pymysql.connect(**mysql_config())

