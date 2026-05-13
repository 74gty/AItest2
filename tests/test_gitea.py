import pytest

from pages.gitea_login_page import GiteaLoginPage


pytestmark = pytest.mark.ui


def test_gitea_login_page(driver, test_config):
    login_page = GiteaLoginPage(driver)
    login_page.open(test_config["gitea_url"])

    assert login_page.is_login_form_displayed()


def test_gitea_login(driver, test_config):
    username = test_config.get("gitea_username")
    password = test_config.get("gitea_password")
    if not username or not password:
        pytest.skip("未配置 Gitea 账号，使用 --gitea-username 和 --gitea-password 后运行")

    login_page = GiteaLoginPage(driver)
    login_page.open(test_config["gitea_url"])

    if not login_page.is_login_form_displayed():
        pytest.skip("Gitea 可能仍在首次安装页，请先完成初始化")

    login_page.login(username, password)

    assert "/user/login" not in driver.current_url
