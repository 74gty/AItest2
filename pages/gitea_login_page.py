from selenium.webdriver.common.by import By


class GiteaLoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.username_input = (By.ID, "user_name")
        self.password_input = (By.ID, "password")
        self.sign_in_button = (By.XPATH, "//button[contains(., 'Sign In') or contains(., '登录')]")

    def open(self, base_url):
        self.driver.get(f"{base_url}/user/login")

    def is_login_form_displayed(self):
        # Gitea 首次启动未初始化时可能跳转安装页，这里只判断登录表单是否出现
        return bool(self.driver.find_elements(*self.username_input))

    def login(self, username, password):
        # 封装 Gitea 登录动作，方便后续扩展仓库创建、权限测试
        self.driver.find_element(*self.username_input).send_keys(username)
        self.driver.find_element(*self.password_input).send_keys(password)
        self.driver.find_element(*self.sign_in_button).click()
