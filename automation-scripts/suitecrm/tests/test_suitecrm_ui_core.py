from uuid import uuid4

import pytest
from selenium.common.exceptions import WebDriverException

from suitecrm.ui.pages.login_page import SuiteCrmLoginPage
from suitecrm.ui.pages.module_page import SuiteCrmModulePage


pytestmark = [pytest.mark.suitecrm, pytest.mark.ui]


def login_to_suitecrm(driver, config):
    login_page = SuiteCrmLoginPage(driver)
    try:
        login_page.open(config["suitecrm_url"])
    except WebDriverException as error:
        # SuiteCRM 环境由本地单独部署，未启动时跳过业务用例并给出明确原因
        pytest.skip(f"无法访问 SuiteCRM：{error.msg}")

    if not login_page.is_loaded():
        pytest.skip("SuiteCRM 登录页不可用，请先完成安装并确认 suitecrm_url")

    login_page.login(config["suitecrm_username"], config["suitecrm_password"])
    assert login_page.is_logged_in()


def test_suitecrm_ui_login(suitecrm_driver, suitecrm_config):
    login_to_suitecrm(suitecrm_driver, suitecrm_config)


def test_suitecrm_ui_account_crud_flow(suitecrm_driver, suitecrm_config):
    login_to_suitecrm(suitecrm_driver, suitecrm_config)

    module_page = SuiteCrmModulePage(suitecrm_driver)
    account_name = f"EUTL UI Account {uuid4().hex[:8]}"
    updated_name = f"{account_name} Updated"
    record_id = None

    try:
        module_page.open_create_form(suitecrm_config["suitecrm_url"], "Accounts")
        module_page.fill_text_field("name", account_name)
        module_page.save()
        record_id = module_page.current_record_id()
        assert module_page.page_contains(account_name)

        module_page.open_edit_form(suitecrm_config["suitecrm_url"], "Accounts", record_id)
        module_page.fill_text_field("name", updated_name)
        module_page.save()
        assert module_page.page_contains(updated_name)
    finally:
        if record_id:
            module_page.open_delete_action(suitecrm_config["suitecrm_url"], "Accounts", record_id)
