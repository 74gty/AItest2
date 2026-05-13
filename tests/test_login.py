import pytest

from pages.login_page import LoginPage


pytestmark = pytest.mark.ui


def test_login(driver, test_config):
    driver.get(f"{test_config['base_url']}/login")

    login_page = LoginPage(driver)
    login_page.login("tomsmith", "SuperSecretPassword!")

    assert "/secure" in driver.current_url
