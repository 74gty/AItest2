from urllib.parse import parse_qs, urlparse

from selenium.webdriver.common.by import By

from suitecrm.ui.pages.base_page import BasePage


class SuiteCrmModulePage(BasePage):
    SAVE_BUTTON = (By.ID, "SAVE")

    def open_create_form(self, base_url, module_name):
        self.driver.get(f"{base_url.rstrip('/')}/index.php?module={module_name}&action=EditView")

    def open_edit_form(self, base_url, module_name, record_id):
        self.driver.get(
            f"{base_url.rstrip('/')}/index.php?module={module_name}&action=EditView&record={record_id}"
        )

    def open_delete_action(self, base_url, module_name, record_id):
        self.driver.get(
            f"{base_url.rstrip('/')}/index.php?module={module_name}&action=Delete&record={record_id}"
        )

    def fill_text_field(self, field_name, value):
        self.fill((By.NAME, field_name), value)

    def save(self):
        self.click(self.SAVE_BUTTON)

    def current_record_id(self):
        query = parse_qs(urlparse(self.driver.current_url).query)
        record_id = query.get("record", [""])[0]
        assert record_id
        return record_id

    def page_contains(self, text):
        return text in self.driver.page_source
