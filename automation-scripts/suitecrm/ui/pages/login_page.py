from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from suitecrm.ui.pages.base_page import BasePage


class SuiteCrmLoginPage(BasePage):
    USERNAME_INPUT = (By.ID, "user_name")
    PASSWORD_INPUT = (By.ID, "username_password")
    LOGIN_BUTTON = (By.ID, "bigbutton")
    SUITE8_USERNAME_INPUT = (By.NAME, "username")
    SUITE8_PASSWORD_INPUT = (By.NAME, "password")
    SUITE8_LOGIN_BUTTON = (By.ID, "login-button")

    def open(self, base_url):
        # 访问根地址，让 SuiteCRM 7/8 按自身路由进入登录页
        self.driver.get(base_url.rstrip("/"))

    def is_loaded(self):
        try:
            self.wait.until(
                lambda driver: driver.find_elements(*self.USERNAME_INPUT)
                or driver.find_elements(*self.SUITE8_USERNAME_INPUT)
            )
            return True
        except TimeoutException:
            return False

    def login(self, username, password):
        # 兼容 SuiteCRM 7 旧模板与 SuiteCRM 8 SPA 登录页
        if self.driver.find_elements(*self.SUITE8_USERNAME_INPUT):
            self.fill(self.SUITE8_USERNAME_INPUT, username)
            self.fill(self.SUITE8_PASSWORD_INPUT, password)
            self.click(self.SUITE8_LOGIN_BUTTON)
            return

        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def is_logged_in(self):
        login_markers = "#globalLinks, .navbar, #moduleTab_Home, scrm-navbar-ui"
        try:
            self.wait.until(
                lambda driver: "Login" not in driver.current_url
                and driver.find_elements(By.CSS_SELECTOR, login_markers)
            )
            return True
        except TimeoutException:
            return False
