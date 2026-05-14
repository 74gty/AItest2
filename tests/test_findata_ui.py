import pytest
import requests
from selenium.common.exceptions import WebDriverException

from pages.findata_dashboard_page import FindataDashboardPage


pytestmark = [pytest.mark.findata, pytest.mark.ui]


def clear_watchlist(base_url):
    # UI 用例运行前清理演示数据，避免重复执行时受上一次服务状态影响
    response = requests.get(f"{base_url}/api/watchlist", timeout=5)
    if response.status_code != 200:
        return
    for item in response.json()["data"]:
        requests.delete(f"{base_url}/api/watchlist/{item['item_id']}", timeout=5)


def test_findata_ui_login_and_dashboard(driver, test_config):
    page = FindataDashboardPage(driver)
    try:
        page.open_login(test_config["findata_url"])
    except WebDriverException as error:
        # 金融平台服务需先启动，未启动时跳过 UI 用例并保留清晰原因
        pytest.skip(f"无法访问金融数据平台：{error.msg}")

    page.login(test_config["findata_username"], test_config["findata_password"])
    page.wait_for_dashboard()

    assert "金融行情数据聚合与风险监控" in driver.page_source


def test_findata_ui_quote_and_watchlist(driver, test_config):
    clear_watchlist(test_config["findata_url"])

    page = FindataDashboardPage(driver)
    try:
        page.open_login(test_config["findata_url"])
    except WebDriverException as error:
        pytest.skip(f"无法访问金融数据平台：{error.msg}")

    page.login(test_config["findata_username"], test_config["findata_password"])
    page.wait_for_dashboard()

    quote_result = page.query_stock("600519")
    assert "600519" in quote_result

    page.add_watchlist_item("600519", "贵州茅台")
    assert "贵州茅台" in driver.page_source
