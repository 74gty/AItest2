import os
import secrets

from utils.config_loader import load_config


SESSION_COOKIE = "findata_session"


def findata_auth_config():
    # 金融平台演示登录账号集中放在配置里，后续可替换为数据库查询
    config = load_config()
    return {
        "username": os.getenv("FINDATA_USERNAME") or config.get("findata_username") or "tester",
        "password": os.getenv("FINDATA_PASSWORD") or config.get("findata_password") or "tester123",
        "session_token": os.getenv("FINDATA_SESSION_TOKEN") or config.get("findata_session_token") or "findata-demo-session",
    }


def authenticate(username, password):
    config = findata_auth_config()
    return secrets.compare_digest(username, config["username"]) and secrets.compare_digest(password, config["password"])


def is_authenticated(request):
    config = findata_auth_config()
    session_token = request.cookies.get(SESSION_COOKIE, "")
    return secrets.compare_digest(session_token, config["session_token"])
