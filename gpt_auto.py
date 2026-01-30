import browser.launch as launch
import browser.browser_funcs as funcs

from cfg.myconfig import browser_config
import json
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

INPUT_JSON = "data/questions.json"
OUTPUT_JSON_WITHOUT = "data/answers"
WAIT_TIMEOUT = 120
SLEEP_BETWEEN_QUESTIONS = 5
BATCH_SIZE = 2
NEW_CHAT_WAIT_TIME = 1
NEW_PAGE_WAIT_TIME = 20
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
    # 必须先 click 激活
    input_box.click()
    time.sleep(0.2)

    # ProseMirror 不支持 clear()，用 Ctrl+A + Delete
    input_box.send_keys(Keys.CONTROL, "a")
    input_box.send_keys(Keys.DELETE)

    input_box.send_keys(question)
    input_box.send_keys(Keys.ENTER)


def wait_for_answer(driver,timeout=120):
    start = time.time()
    last_text = ""

    while True:
        time.sleep(1)

        answers = driver.find_elements(
            By.CSS_SELECTOR,
            'div[data-message-author-role="assistant"]'
        )

        if not answers:
            continue

        current = answers[-1].text.strip()

        if current and current == last_text:
            return current

        last_text = current

        if time.time() - start > timeout:
            return current


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
        driver = launch.relink_browser(driver,browser_config)

        qid = item.get("id", idx)
        question = item.get("question")

        if not question:
            continue

        print(f"\n[{idx}/{len(questions)}] Asking ID={qid}")
        print("Q:", question)

        try:
            send_question(question)
            answer = wait_for_answer(driver,timeout=WAIT_TIMEOUT)

            print("A:", answer[:200], "..." if len(answer) > 200 else "")

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
                print(f"Updated status file for batch starting at index {idx_start}")

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
        batch_ask(data[i:i+BATCH_SIZE],i,BATCH_SIZE)

    

# =========================
# 入口
# =========================
if __name__ == "__main__":
    ask()
