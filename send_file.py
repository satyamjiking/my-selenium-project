# send_file.py
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --------- Config from environment ----------
FB_USER = os.getenv("FB_USER")
FB_PASS = os.getenv("FB_PASS")
TARGET_ID = os.getenv("TARGET_ID")
DELAY = float(os.getenv("DELAY", "40"))            # seconds between messages
MAX_TEST = int(os.getenv("MAX_TEST", "0"))         # 0 => send all

if not (FB_USER and FB_PASS and TARGET_ID):
    print("[ERROR] Missing FB_USER / FB_PASS / TARGET_ID in environment.")
    raise SystemExit(1)

# --------- Chrome options (headless for Render) ----------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
# Try common chromium binary locations
for path in ("/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"):
    if os.path.exists(path):
        chrome_options.binary_location = path
        break

# Try to create driver robustly (two fallbacks)
driver = None
service_paths = ["/usr/bin/chromedriver", "/usr/local/bin/chromedriver"]

for svc_path in service_paths:
    try:
        if os.path.exists(svc_path):
            service = Service(svc_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            break
    except Exception as e:
        print(f"[WARN] chromedriver via Service {svc_path} failed: {e}")

if driver is None:
    try:
        # fallback: let selenium find it (if chromedriver on PATH)
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print("[ERROR] Could not start Chrome webdriver:", e)
        raise SystemExit(1)

wait = WebDriverWait(driver, 20)

def safe_find_textarea():
    """Try multiple locators for mbasic messenger textarea"""
    # mbasic usually uses name="body" for message textarea in messages/read page
    locators = [
        (By.NAME, "body"),
        (By.NAME, "message_body"),
        (By.XPATH, "//textarea"),
        (By.XPATH, "//input[@name='body']"),
        (By.XPATH, "//div[@contenteditable='true']"),
    ]
    for by, val in locators:
        try:
            el = wait.until(EC.presence_of_element_located((by, val)))
            return el
        except:
            continue
    return None

def login_facebook():
    print("[INFO] Opening mbasic.facebook.com/login")
    driver.get("https://mbasic.facebook.com/login")
    # email and pass fields
    try:
        email = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        pwd = driver.find_element(By.NAME, "pass")
        email.clear(); email.send_keys(FB_USER)
        pwd.clear(); pwd.send_keys(FB_PASS)
        # submit
        try:
            login_btn = driver.find_element(By.NAME, "login")
            login_btn.click()
        except:
            pwd.send_keys("\n")
        # wait for either login success or checkpoint
        time.sleep(5)
        print("[INFO] After login, current URL:", driver.current_url)
    except Exception as e:
        print("[ERROR] Login failed:", e)
        raise

def open_thread():
    # Use mbasic thread URL format
    thread_url = f"https://mbasic.facebook.com/messages/read/?tid={TARGET_ID}"
    print("[INFO] Opening thread:", thread_url)
    driver.get(thread_url)
    # wait for page load
    time.sleep(4)

def send_messages_from_file():
    if not os.path.exists("file.txt"):
        print("[ERROR] file.txt not found in repo root.")
        return

    with open("file.txt", "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    if not lines:
        print("[INFO] file.txt empty.")
        return

    total = len(lines)
    to_send = lines if MAX_TEST == 0 else lines[:min(MAX_TEST, total)]
    print(f"[INFO] Sending {len(to_send)} / {total} messages with {DELAY}s delay")

    for idx, text in enumerate(to_send, start=1):
        try:
            # ensure thread page loaded and textarea present
            textarea = safe_find_textarea()
            if textarea is None:
                print(f"[ERROR] Message box not found for message {idx}.")
                return

            # For mbasic, often textarea is an <input> or <textarea> with name 'body'
            try:
                textarea.clear()
            except:
                pass
            try:
                textarea.send_keys(text)
            except Exception:
                # sometimes editable div requires JS
                driver.execute_script("arguments[0].innerText = arguments[1];", textarea, text)

            # try to click send: name=send or value=Send
            sent = False
            send_selectors = [
                (By.NAME, "send"),
                (By.XPATH, "//input[@type='submit' or @type='button' and (contains(@value,'Send') or contains(@value,'send'))]"),
                (By.XPATH, "//button[contains(., 'Send') or contains(., 'send') or contains(., 'Send Message')]"),
                (By.XPATH, "//input[@type='submit']"),
            ]
            for by, val in send_selectors:
                try:
                    btn = driver.find_element(by, val)
                    btn.click()
                    sent = True
                    break
                except:
                    continue

            if not sent:
                # fallback: press Enter in textarea if possible
                try:
                    textarea.send_keys("\n")
                    sent = True
                except:
                    pass

            if sent:
                print(f"[SENT] {idx}/{len(to_send)}: {text[:80]}")
            else:
                print(f"[WARN] Could not send message {idx} via click/enter. Text: {text[:80]}")
            # human-like random delay around configured DELAY
            delay = DELAY + (random.random() * 3 - 1.5)
            time.sleep(max(1, delay))
        except Exception as e:
            print(f"[ERROR] Exception sending message {idx}: {e}")
            time.sleep(5)

def main():
    try:
        login_facebook()
        open_thread()
        send_messages_from_file()
    finally:
        print("[INFO] Done — quitting driver")
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()
