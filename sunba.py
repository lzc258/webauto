#实现孙吧的全自动水贴
from selenium.webdriver.common.by import By

from time import sleep

import src.launch as launch
import src.browser_funcs as funcs


browser_config = {'name':'your/browser/name',#选择浏览器名
                  'port':'your/browser/port',#选择端口。空闲即可
                  'profile_path' : 'your/profile/path',#用户希望浏览器配置文件的保存路径，该文件创建后，下次启动浏览器时会自动加载该配置文件
                  'directory_path': 'your/browser/path'#浏览器可执行文件路径
                  }

url = 'your/url'#输入吧网址
page = 1#从第几页开始
n = 99999#循环次数，可以根据需要设置，建议不要太大，防止被封IP

driver = launch.get_driver(browser_config)
driver.get(url)
for i in range(1,page):
    t=funcs.wait_for_elements(driver, (By.XPATH, "//a[@class='next pagination-item ']"), 10)
    link = driver.find_element(By.XPATH, "//a[@class='next pagination-item ']")
    driver.execute_script("arguments[0].scrollIntoView();", link)
    driver.execute_script("window.scrollBy(0, -150);")  # 向上滚动一点以避免头部固定元素遮挡
    link.click()  # 点击链接
    sleep(1)
    
while(n):
    funcs.wait_for_elements(driver, (By.XPATH, "//a[contains(@class, 'j_th_tit') ]"), 10)
    links = driver.find_elements(By.XPATH, "//a[contains(@class, 'j_th_tit') ]")
    for link in links:
        driver.execute_script("arguments[0].scrollIntoView();", link)
        driver.execute_script("window.scrollBy(0, -150);")  # 向上滚动一点以避免头部固定元素遮挡
        link.click()  # 点击链接
        handles = driver.window_handles          #获取当前浏览器的所有窗口句柄
        driver.switch_to.window(handles[-1]) #切换到最新打开的窗口
        try:
            t=funcs.wait_for_elements(driver, (By.ID, "quick_reply"), 5)

            reply_button = driver.find_element(By.ID, "quick_reply")#定位回复按钮
            reply_button.click()

            t=funcs.wait_for_elements(driver, (By.ID, "ueditor_replace"), 10)

            editable_div = driver.find_element(By.ID, "ueditor_replace")#定位编辑区域
            t=funcs.wait_for_elements(driver, (By.XPATH, "//div[@class='tb_poster_placeholder']"), 10)

            ele = driver.find_element(By.XPATH, "//div[@class='tb_poster_placeholder']")
            style = ''
            sleep(1)
            while(style != 'display: none;'):
                editable_div.click()  # 点击以激活编辑区域
                style = ele.get_attribute("style")

            editable_div.send_keys("加三")  # 输入文本
            t=funcs.wait_for_elements(driver, (By.XPATH, "//a[.//em[text()='发 表']]"), 10)

            submit_button = driver.find_element(By.XPATH, "//a[.//em[text()='发 表']]")
            submit_button.click()
            sleep(1)
            funcs.exit_page(driver,0)
        except Exception as e:
            funcs.exit_page(driver,0)
    t=funcs.wait_for_elements(driver, (By.XPATH, "//a[@class='next pagination-item ']"), 10)
    link = driver.find_element(By.XPATH, "//a[@class='next pagination-item ']")
    driver.execute_script("arguments[0].scrollIntoView();", link)
    driver.execute_script("window.scrollBy(0, -150);")  # 向上滚动一点以避免头部固定元素遮挡
    link.click()  # 点击链接
    sleep(1)
    n -= 1
driver.quit()

