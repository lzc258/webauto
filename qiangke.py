# 用于whu自动选课
from selenium.webdriver.common.by import By

from time import sleep

import src.launch as launch
import src.browser_funcs as funcs

button_id = ""#按钮的id属性

browser_config = {'name':'chrome',#选择浏览器名
                  'port':'8222',#选择端口。空闲即可
                  'profile_path' : 'D:/data/website/chrome_profile',#用户希望浏览器配置文件的保存路径，该文件创建后，下次启动浏览器时会自动加载该配置文件
                  'directory_path': 'C:/Program Files/Google/Chrome/Application'#浏览器可执行文件路径
                  }

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