# 用于学习通刷课
from selenium.webdriver.common.by import By

from time import sleep

import browser.launch as launch
import browser.browser_funcs as funcs

from cfg.myconfig import browser_config

driver = launch.get_driver(browser_config)#获取驱动器
url = 'https://mooc1.chaoxing.com/mycourse/studentstudy?chapterId=896818018&courseId=245474394&clazzid=104259339&cpi=261748473&enc=ea7de2c021003bc2c4dcd00a2fe53931&mooc2=1&openc=a2cd59af3156622da46978d66df66e2d'
driver.get(url)