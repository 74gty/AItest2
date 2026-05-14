from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class FindataDashboardPage:
    def __init__(self, driver):
        self.driver = driver
        self.username_input = (By.ID, "username")
        self.password_input = (By.ID, "password")
        self.login_button = (By.CSS_SELECTOR, "#login-form button[type='submit']")
        self.health_status = (By.ID, "health-status")
        self.quote_symbol = (By.ID, "quote-symbol")
        self.quote_result = (By.ID, "quote-result")
        self.watchlist_count = (By.ID, "watchlist-count")
        self.watchlist_symbol = (By.ID, "watchlist-symbol")
        self.watchlist_name = (By.ID, "watchlist-name")
        self.watchlist_submit = (By.CSS_SELECTOR, "#watchlist-form button[type='submit']")

    def open_login(self, base_url):
        self.driver.get(f"{base_url}/login")

    def login(self, username, password):
        # 登录动作封装在 Page Object 内，UI 用例只表达业务步骤
        self.driver.find_element(*self.username_input).send_keys(username)
        self.driver.find_element(*self.password_input).send_keys(password)
        self.driver.find_element(*self.login_button).click()

    def wait_for_dashboard(self, timeout=8):
        WebDriverWait(self.driver, timeout).until(EC.url_contains("/dashboard"))
        WebDriverWait(self.driver, timeout).until(EC.text_to_be_present_in_element(self.health_status, "ok"))

    def query_stock(self, symbol):
        input_element = self.driver.find_element(*self.quote_symbol)
        input_element.clear()
        input_element.send_keys(symbol)
        input_element.submit()
        WebDriverWait(self.driver, 8).until(EC.text_to_be_present_in_element(self.quote_result, symbol))
        return self.driver.find_element(*self.quote_result).text

    def add_watchlist_item(self, symbol, name):
        symbol_input = self.driver.find_element(*self.watchlist_symbol)
        symbol_input.clear()
        symbol_input.send_keys(symbol)
        name_input = self.driver.find_element(*self.watchlist_name)
        name_input.clear()
        name_input.send_keys(name)
        self.driver.find_element(*self.watchlist_submit).click()
        WebDriverWait(self.driver, 8).until(EC.text_to_be_present_in_element(self.watchlist_count, "1"))
