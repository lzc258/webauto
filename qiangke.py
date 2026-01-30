# 用于whu自动选课
from selenium.webdriver.common.by import By

from time import sleep

import browser.launch as launch
import browser.browser_funcs as funcs

button_id = "btn-xk-17E86A1135B96DEBE0630207010AC4ED"#按钮的id属性

from cfg.myconfig import browser_config

driver = launch.get_driver(browser_config)#获取驱动器
all_handles = driver.window_handles
driver.switch_to.window(all_handles[0])
while(1):
    t = funcs.wait_for_elements(driver, (By.ID, button_id), 60)
    if t != 0:
        button = driver.find_element(By.ID, button_id)
        button_text = button.text
        if button_text == "选课":
            button.click()
        else:
            break
    t = funcs.wait_for_elements(driver, (By.ID, "btn_ok"), 60)
    if t == 0:
        continue
    button = driver.find_element(By.ID, "btn_ok")
    button.click()