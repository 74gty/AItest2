from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.common.exceptions import TimeoutException

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

driver.get("https://www.baidu.com")

# 处理可能的遮罩弹窗（百度首页经常有 cookie 提示条或广告遮罩）
try:
    # 尝试关闭常见的 cookie 弹窗
    cookie_close = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'cclose')]"))
    )
    cookie_close.click()
    time.sleep(0.5)
except TimeoutException:
    pass  # 没有弹窗则跳过

# 等待搜索框可交互
search_box = wait.until(EC.element_to_be_clickable((By.ID, "kw")))

# 先用 ActionChains 点击，更稳健
ActionChains(driver).move_to_element(search_box).click().perform()
time.sleep(0.3)
search_box.clear()
search_box.send_keys("软件测试")

search_button = wait.until(EC.element_to_be_clickable((By.ID, "su")))
search_button.click()

time.sleep(2)
driver.save_screenshot("result.png")
print("搜索完成，截图已保存！")

driver.quit()
