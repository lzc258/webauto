import browser.launch as launch
import browser.browser_funcs as funcs

from cfg.myconfig import browser_config
import json
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = launch.get_driver(browser_config,is_handle_login=True)
wait = WebDriverWait(driver, 30)

INPUT_JSON = "questions.json"
OUTPUT_JSON = "answers.json"
WAIT_TIMEOUT = 120
SLEEP_BETWEEN_QUESTIONS = 5

wait = WebDriverWait(driver, 30)

# =========================
# 页面操作函数
# =========================
def get_input_box():
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


def wait_for_answer(timeout=120):
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
def batch_ask():
    # new_chat()
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        questions = json.load(f)

    results = []

    for idx, item in enumerate(questions, 1):
        qid = item.get("id", idx)
        question = item.get("question")

        if not question:
            continue

        print(f"\n[{idx}/{len(questions)}] Asking ID={qid}")
        print("Q:", question)

        try:
            send_question(question)
            answer = wait_for_answer()

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

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[✓] Finished. Results saved to {OUTPUT_JSON}")

# =========================
# 入口
# =========================
if __name__ == "__main__":
    batch_ask()
