from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

#等待网页加载出locato元素，返回1表示成功，0表示超时
def wait_for_elements(driver, locator, timeout=10):
    wait = WebDriverWait(driver, timeout)
    try:
        wait.until(EC.presence_of_all_elements_located(locator))
        return 1
    except TimeoutException:
        return 0
    
#退出当前页面，并切换至指定页面(0表示第一个页面,1表示第二个页面...-1表示最后一个页面...)
def exit_page(driver,n):
    driver.close()
    handles = driver.window_handles
    driver.switch_to.window(handles[n]) 