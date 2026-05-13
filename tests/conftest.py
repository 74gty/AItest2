import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import MaxRetryError

from utils.config_loader import load_config


def pytest_addoption(parser):
    parser.addoption("--run-ui", action="store_true", help="运行需要 Docker Chrome 的 UI 测试")
    parser.addoption("--remote-url", default=None, help="Docker Selenium Remote 地址")
    parser.addoption("--base-url", default=None, help="被测系统地址")
    parser.addoption("--gitea-url", default=None, help="Gitea 被测服务地址")
    parser.addoption("--gitea-username", default=None, help="Gitea 登录用户名")
    parser.addoption("--gitea-password", default=None, help="Gitea 登录密码")


@pytest.fixture(scope="session")
def test_config(pytestconfig):
    config = load_config()
    remote_url = pytestconfig.getoption("--remote-url")
    base_url = pytestconfig.getoption("--base-url")
    gitea_url = pytestconfig.getoption("--gitea-url")
    gitea_username = pytestconfig.getoption("--gitea-username")
    gitea_password = pytestconfig.getoption("--gitea-password")

    if remote_url:
        config["remote_url"] = remote_url
    if base_url:
        config["base_url"] = base_url
    if gitea_url:
        config["gitea_url"] = gitea_url
    if gitea_username:
        config["gitea_username"] = gitea_username
    if gitea_password:
        config["gitea_password"] = gitea_password

    return config


@pytest.fixture
def driver(pytestconfig, test_config):
    if not pytestconfig.getoption("--run-ui"):
        pytest.skip("UI 测试需要 Docker Chrome，使用 --run-ui 启用")

    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1365,768")

    try:
        driver = webdriver.Remote(
            command_executor=test_config["remote_url"],
            options=options,
        )
    except (MaxRetryError, WebDriverException) as error:
        pytest.skip(f"无法连接 Docker Chrome：{error}")

    yield driver
    driver.quit()
