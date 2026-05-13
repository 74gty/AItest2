import sys
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import MaxRetryError

from utils.config_loader import load_config


AUTOMATION_ROOT = Path(__file__).resolve().parent
if str(AUTOMATION_ROOT) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_ROOT))


def pytest_addoption(parser):
    parser.addoption("--run-suitecrm-ui", action="store_true", help="运行 SuiteCRM UI 测试")
    parser.addoption("--run-suitecrm-api", action="store_true", help="运行 SuiteCRM API 测试")
    parser.addoption("--suitecrm-url", default=None, help="SuiteCRM Web 地址")
    parser.addoption("--suitecrm-api-url", default=None, help="SuiteCRM API 地址，通常以 /Api 结尾")
    parser.addoption("--suitecrm-username", default=None, help="SuiteCRM 登录用户名")
    parser.addoption("--suitecrm-password", default=None, help="SuiteCRM 登录密码")
    parser.addoption("--suitecrm-client-id", default=None, help="SuiteCRM OAuth2 client_id")
    parser.addoption("--suitecrm-client-secret", default=None, help="SuiteCRM OAuth2 client_secret")


@pytest.fixture(scope="session")
def suitecrm_config(pytestconfig):
    config = load_config()
    option_map = {
        "suitecrm_url": "--suitecrm-url",
        "suitecrm_api_url": "--suitecrm-api-url",
        "suitecrm_username": "--suitecrm-username",
        "suitecrm_password": "--suitecrm-password",
        "suitecrm_client_id": "--suitecrm-client-id",
        "suitecrm_client_secret": "--suitecrm-client-secret",
    }

    for key, option_name in option_map.items():
        value = pytestconfig.getoption(option_name)
        if value:
            config[key] = value

    return config


@pytest.fixture
def suitecrm_driver(pytestconfig, suitecrm_config):
    if not pytestconfig.getoption("--run-suitecrm-ui"):
        pytest.skip("SuiteCRM UI 测试需要使用 --run-suitecrm-ui 启用")

    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1365,768")

    try:
        driver = webdriver.Remote(
            command_executor=suitecrm_config["remote_url"],
            options=options,
        )
    except (MaxRetryError, WebDriverException) as error:
        pytest.skip(f"无法连接 Docker Chrome：{error}")

    yield driver
    driver.quit()


@pytest.fixture
def suitecrm_api_client(pytestconfig, suitecrm_config):
    if not pytestconfig.getoption("--run-suitecrm-api"):
        pytest.skip("SuiteCRM API 测试需要使用 --run-suitecrm-api 启用")

    from suitecrm.api.client import SuiteCrmApiClient

    return SuiteCrmApiClient(
        api_url=suitecrm_config["suitecrm_api_url"],
        username=suitecrm_config.get("suitecrm_username"),
        password=suitecrm_config.get("suitecrm_password"),
        client_id=suitecrm_config.get("suitecrm_client_id"),
        client_secret=suitecrm_config.get("suitecrm_client_secret"),
    )
