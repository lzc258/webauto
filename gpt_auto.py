import browser.launch as launch
import browser.browser_funcs as funcs
import browser.log as my_log

from cfg.myconfig import browser_config
import json
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# 启用log
my_log.start_logging()

INPUT_JSON = "data/event_backgrounds_questions.json"
OUTPUT_JSON_WITHOUT = "data/event_backgrounds_answers/event_backgrouds_answers"
WAIT_TIMEOUT = 120
SLEEP_BETWEEN_QUESTIONS = 5
BATCH_SIZE = 30
NEW_CHAT_WAIT_TIME = 1
NEW_PAGE_WAIT_TIME = 20
last_answer = ''
driver = launch.get_driver(browser_config,is_handle_login=True)

# =========================
# 页面操作函数
# =========================
def get_input_box():
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    # 等待左侧栏元素出现，保证页面加载完成
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.group.__menu-item.hoverable"))
    )
    return wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'div.ProseMirror[contenteditable="true"]')
        )
    )


def send_question(question: str):
    input_box = get_input_box()
    time.sleep(1)
    input_box.click()
    time.sleep(0.2)

    # 清空内容
    input_box.send_keys(Keys.CONTROL, "a")
    input_box.send_keys(Keys.DELETE)

    # 分行发送，每行后用 Shift+Enter
    for line in question.splitlines():
        input_box.send_keys(line)
        input_box.send_keys(Keys.SHIFT, Keys.ENTER)

    # 最后回车提交
    input_box.send_keys(Keys.ENTER)


def wait_for_answer(driver, timeout=180, stable_time=3, poll_interval=1):
    """
    等待 ChatGPT 回答完成
    返回新增文本（增量）
    """
    global last_answer
    start_time = time.time()
    last_text = ""
    last_change_time = time.time()

    while True:
        time.sleep(poll_interval)

        # 找到所有 assistant 回答块
        answers = driver.find_elements(
            By.CSS_SELECTOR,
            'div[data-message-author-role="assistant"]'
        )
        if not answers:
            continue

        # 滚动到最后一个 block，确保渲染
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'end'});", answers[-1])
        except Exception:
            pass

        # 拼接所有 block 内部文本
        current_text = ""
        for a in answers:
            try:
                # 优先抓 <code> 或 <pre> 内文本
                code_blocks = a.find_elements(By.CSS_SELECTOR, "pre, code")
                if code_blocks:
                    for c in code_blocks:
                        t = driver.execute_script("return arguments[0].innerText;", c)
                        if t:
                            current_text += t
                else:
                    # 没有 <code>/<pre> 时抓整个 block
                    t = driver.execute_script("return arguments[0].innerText;", a)
                    if t:
                        current_text += t
            except Exception:
                pass

        current_text = current_text.strip()

        # 计算增量
        if current_text != last_text:
            last_text = current_text
            last_change_time = time.time()

        # 内容稳定一段时间，认为完成
        if time.time() - last_change_time >= stable_time:
            now_answer = current_text[len(last_answer):]
            last_answer = current_text
            if len(now_answer) > 3: # 过滤掉空回答
                return now_answer

        # 总超时兜底
        if time.time() - start_time > timeout:
            print("Warning: wait_for_answer timeout")
            now_answer = current_text[len(last_answer):]
            last_answer = current_text
            return now_answer


def new_chat():
    # 等待元素可见
    print("Creating new chat...")

    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL).key_down(Keys.SHIFT).send_keys('O').key_up(Keys.SHIFT).key_up(Keys.CONTROL).perform()
    time.sleep(NEW_CHAT_WAIT_TIME)
    print("Created new chat done.")
    
    get_input_box()   # 等真正的 ProseMirror 可用

# =========================
# 主流程
# =========================
def batch_ask(questions, idx_start, batch_size):
    results = []
    OUTPUT_JSON = OUTPUT_JSON_WITHOUT + f"_{idx_start}_{idx_start+batch_size-1}.json"
    new_chat()
    for idx, item in enumerate(questions, 1):
        global driver
        while True:
            try:               
                driver = launch.relink_browser(driver,browser_config)
                break
            except Exception as e:
                print(f"连接失败：{e}")
                time.sleep(1)  # 等待1秒再重试
                continue

        qid = item.get("id", idx)
        question = item.get("question")

        if not question:
            continue

        print(f"\n[{idx}/{len(questions)}] Asking ID={qid}")
        print(f"Q:{question}")

        try:
            send_question(question)
            answer = wait_for_answer(driver,timeout=WAIT_TIMEOUT)
            processed_answer = answer#[:200], "..." if len(answer) > 200 else ""
            print(f"A:{processed_answer}")

            results.append({
                "id": qid,
                "question": question,
                "answer": answer
            })

        except Exception as e:
            print(f"[!] Failed ID={qid}: {e}")
            results.append({
                "id": qid,
                "question": question,
                "answer": "",
                "error": str(e)
            })

        time.sleep(SLEEP_BETWEEN_QUESTIONS)

    with open("data/status.json", "w", encoding="utf-8") as f:
                json.dump({
                    "start": idx_start + batch_size,
                    }, f, ensure_ascii=False, indent=4, default=str)
                print(f"Updated status file for batch starting at index {idx_start + batch_size}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[✓] Finished. Results saved to {OUTPUT_JSON}")

def ask():
    try:
        with open("data/status.json", "r", encoding="utf-8") as f:
            status_info = json.load(f)
            is_resume = True
            print("Resuming from last status:", status_info)
    except:
        is_resume = False
        status_info = {}

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    if is_resume:
        print("Starting fresh from the beginning.")
        start_index = status_info.get("start", 0)
    else:
        start_index = 0
    # driver.get("https://chat.openai.com")
    # time.sleep(NEW_PAGE_WAIT_TIME)  # 等待页面加载,以及手动绕过真人检验

    # 也可以使用手动的方式直接打开openai chat页面，登录后再运行脚本
    for i in range(start_index, len(data), BATCH_SIZE):
        global last_answer
        last_answer = ''
        batch_ask(data[i:i+BATCH_SIZE],i,BATCH_SIZE)

    

# =========================
# 入口
# =========================
if __name__ == "__main__":
    ask()
