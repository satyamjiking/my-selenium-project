# send_file.py  (Termux-ready)
import os
import time
import json
import shutil
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Load .env from current dir or home
load_dotenv()  

FB_USER   = os.getenv("FB_USER")
FB_PASS   = os.getenv("FB_PASS")
TARGET_ID = os.getenv("TARGET_ID")
DELAY     = float(os.getenv("DELAY", "40"))

if not (FB_USER and FB_PASS and TARGET_ID):
    print("[ERROR] Missing FB_USER / FB_PASS / TARGET_ID in environment.")
    raise SystemExit(1)

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
FILE_PATH = os.path.join(PROJECT_DIR, "file.txt")
QUEUE_PATH = os.path.join(PROJECT_DIR, "queue.txt")

# detect chrome / chromedriver paths
def detect_binaries():
    chrome_bin = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
    chromedriver_bin = shutil.which("chromedriver") or "/usr/bin/chromedriver" or "/data/data/com.termux/files/usr/bin/chromedriver"
    return chrome_bin, chromedriver_bin

CHROME_BIN, CHROMEDRIVER_BIN = detect_binaries()
print("[INFO] chrome_bin:", CHROME_BIN, "chromedriver:", CHROMEDRIVER_BIN)

def create_driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    if CHROME_BIN:
        opts.binary_location = CHROME_BIN
    service = Service(CHROMEDRIVER_BIN) if CHROMEDRIVER_BIN else None
    if service:
        return webdriver.Chrome(service=service, options=opts)
    else:
        return webdriver.Chrome(options=opts)

# helper: network check
def is_online(url="https://www.google.com", timeout=5):
    try:
        requests.get(url, timeout=timeout)
        return True
    except:
        return False

# infinite generator for file messages
def messages_infinite(path):
    while True:
        if not os.path.exists(path):
            yield None
            time.sleep(5)
            continue
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield line
        # file exhausted -> repeat from top
        time.sleep(0.1)

# queue helpers
def queue_append(message):
    with open(QUEUE_PATH, "a", encoding="utf-8") as q:
        q.write(message.replace("\n"," ") + "\n")

def queue_pop_all():
    if not os.path.exists(QUEUE_PATH):
        return []
    with open(QUEUE_PATH, "r", encoding="utf-8") as q:
        lines = [l.strip() for l in q if l.strip()]
    # clear queue file
    open(QUEUE_PATH, "w", encoding="utf-8").close()
    return lines

# fb login (mbasic) and send functions
def fb_login(driver):
    print("[INFO] Logging in to mbasic.facebook.com ...")
    driver.get("https://mbasic.facebook.com/login")
    time.sleep(2)
    try:
        email = driver.find_element(By.NAME, "email")
        pwd = driver.find_element(By.NAME, "pass")
        email.clear(); email.send_keys(FB_USER)
        pwd.clear(); pwd.send_keys(FB_PASS)
        # click login
        try:
            driver.find_element(By.NAME, "login").click()
        except:
            pwd.send_keys("\n")
        time.sleep(5)
        print("[INFO] login current_url:", driver.current_url)
    except Exception as e:
        print("[ERROR] Login failed:", e)
        raise

def send_to_thread(driver, target_id, text):
    # open thread (mbasic)
    thread_url = f"https://mbasic.facebook.com/messages/read/?tid={target_id}"
    driver.get(thread_url)
    time.sleep(2)
    # try common textarea locators
    try:
        # name="body" is common on mbasic
        try:
            box = driver.find_element(By.NAME, "body")
        except:
            box = driver.find_element(By.XPATH, "//textarea")  # fallback
        box.clear()
        box.send_keys(text)
        # submit via send button or enter
        try:
            driver.find_element(By.NAME, "send").click()
        except:
            box.send_keys("\n")
        time.sleep(2)
        print("[SENT]", text[:80])
        return True
    except Exception as e:
        print("[WARN] send failed:", e)
        return False

def main_loop():
    # ensure driver created with retries
    driver = None
    for attempt in range(3):
        try:
            driver = create_driver()
            break
        except Exception as e:
            print("[WARN] create_driver failed:", e)
            time.sleep(3)
    if driver is None:
        print("[FATAL] Could not start webdriver")
        return

    try:
        # login once
        try:
            fb_login(driver)
        except Exception as e:
            print("[ERROR] login issue:", e)
            driver.quit()
            return

        msg_gen = messages_infinite(FILE_PATH)

        for message in msg_gen:
            if message is None:
                time.sleep(5)
                continue

            # if offline: queue and keep looping until online
            if not is_online():
                print("[INFO] Offline -> queueing message")
                queue_append(message)
                # try to send queued messages later
                time.sleep(DELAY)
                continue

            # first send any queued messages
            queued = queue_pop_all()
            for qmsg in queued:
                ok = send_to_thread(driver, TARGET_ID, qmsg)
                if not ok:
                    print("[WARN] queued send failed, re-queueing")
                    queue_append(qmsg)

            # now send current message
            ok = send_to_thread(driver, TARGET_ID, message)
            if not ok:
                print("[WARN] send failed -> queueing")
                queue_append(message)

            time.sleep(DELAY)

    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    # keep running forever; wrap in try to restart on crash
    while True:
        try:
            main_loop()
        except Exception as e:
            print("[ERROR] main_loop crashed:", e)
            time.sleep(10)
            print("[INFO] Restarting main_loop")
