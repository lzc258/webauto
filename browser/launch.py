from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

import os
import subprocess
from time import sleep
import msvcrt

from browser.browser_config import Config


def get_driver(browser_config_part,is_handle_login=True):
    browser_config = Config().get_browser_config(browser_config_part)
    original_directory = os.getcwd()

    if browser_config['name'] == 'chrome':
        options = ChromeOptions()
        if is_handle_login:
            os.chdir(browser_config['directory_path'])
            process = subprocess.Popen(browser_config['command'], shell=True)
            sleep(2)
            process.terminate()
            print("Log in to the website you need to log in to,then press any key to continue")
            options.add_experimental_option("debuggerAddress", "127.0.0.1:" + browser_config['port'] )
            msvcrt.getch()  # 等待用户按键
            print("process continue...")
        else:
            options.add_argument(f"user-data-dir={browser_config['profile_path']}")  # 必须
            options.add_argument(f"profile-directory={browser_config['profile']}")             # 可选
            print("Skipping login handling as per configuration.")
            sleep(2)
        driver = webdriver.Chrome(options=options)
    elif browser_config['name'] == 'edge':
        options = EdgeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:" + browser_config['port'] )
        print("Log in to the website you need to log in to,then press any key to continue")
        msvcrt.getch()  # 等待用户按键
        print("process continue...")
        driver = webdriver.Edge(options=options)
    else:
        raise ValueError("Invalid browser choice")
    os.chdir(original_directory)
    return driver

