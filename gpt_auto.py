import browser.launch as launch
import browser.browser_funcs as funcs

from cfg.myconfig import browser_config
import json
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

INPUT_JSON = "data/questions.json"
OUTPUT_JSON_WITHOUT = "data/answers"
WAIT_TIMEOUT = 120
SLEEP_BETWEEN_QUESTIONS = 5
BATCH_SIZE = 2
driver = launch.get_driver(browser_config,is_handle_login=True)

# =========================
# 页面操作函数
# =========================
def get_input_box():
    wait = WebDriverWait(driver, 30)
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
    driver.get("https://chat.openai.com")
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
            is_resume = False
            print("Resuming from last status:", status_info)
    except:
        is_resume = True
        status_info = {}

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    if is_resume:
        start_index = status_info.get("start", 0)
    else:
        start_index = 0
    for i in range(start_index, len(data), BATCH_SIZE):
        batch_ask(data[i:i+BATCH_SIZE],i,BATCH_SIZE)

    

# =========================
# 入口
# =========================
if __name__ == "__main__":
    ask()
