from selenium.webdriver.common.by import By
from time import sleep
import json

import src.launch as launch
import src.browser_funcs as funcs
from cfg.myconfig import browser_config

import re

def split_by_punctuation(text: str):
    return re.split(r"[，。；；,\.!\?…]+", text)

def get_longest_segment(text: str):
    segments = split_by_punctuation(text)
    segments = [s.strip() for s in segments if s.strip()]
    if not segments:
        return ""
    return max(segments, key=len)

def normalize(text: str):
    text = text.lower()
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[^\w\u4e00-\u9fa5]", "", text)
    return text


# 1. 读取 JSON
with open(
    r"D:\BaiduSyncdisk\projects\毕业论文\本科毕设选题-舆情驱动的新型电力系统APT狩猎假设生成方法-20251025\数据库模块\数据收集\social_events\初步处理json\social_events_sx.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

item_sx = []

# 2. 只创建一个浏览器
driver = launch.get_driver(browser_config)

try:
    for item in data:
        url_list = item.get("source_urls", [])
        relevance_description = item.get("relevance_description", "")

        # 空值保护
        if not relevance_description or not url_list:
            continue

        matched = False  # 标记该 item 是否已匹配

        for url in url_list:
            try:
                driver.get(url)
                sleep(2)  # 给页面一点加载时间（可换 WebDriverWait）

                page_text = driver.find_element(By.TAG_NAME, "body").text

                longest_seg = get_longest_segment(relevance_description)

                if not longest_seg:
                    continue

                if normalize(longest_seg) in normalize(page_text):
                    item_sx.append(item)
                    matched = True
                    break  # 不再检查该 item 的其他 url

            except Exception as e:
                # 单个 url 出错不影响整体流程
                continue

        # 可选：已经匹配的 item 不做任何事，进入下一个 item
        if matched:
            continue

finally:
    driver.quit()


# 3. 写回新的 JSON 文件
with open(
    r"D:\BaiduSyncdisk\projects\毕业论文\本科毕设选题-舆情驱动的新型电力系统APT狩猎假设生成方法-20251025\数据库模块\数据收集\social_events\初步处理json\social_events_sx.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(item_sx, f, ensure_ascii=False, indent=2)
