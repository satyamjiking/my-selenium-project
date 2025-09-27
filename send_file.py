# send_file.py
import os
import time
import random
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Load env vars (locally .env or Render env vars)
load_dotenv()
FB_USER = os.getenv("FB_USER")
FB_PASS = os.getenv("FB_PASS")
TARGET_ID = os.getenv("TARGET_ID", "")
FILE_PATH = "file.txt"

if not (FB_USER and FB_PASS and TARGET_ID):
    print("[ERROR] FB_USER / FB_PASS / TARGET_ID missing in environment.")
    exit(1)

# Read lines from file.txt
if not os.path.exists(FILE_PATH):
    print(f"[ERROR] {FILE_PATH} not found.")
    exit(1)

with open(FILE_PATH, "r", encoding="utf-8") as f:
    messages = [line.strip() for line in f if line.strip()]

print(f"[INFO] Loaded {len(messages)} messages")

# Test limit: भेजने से पहले safety के लिए सिर्फ पहला N lines भेजेगा
MAX_TEST = 2
messages = messages[:MAX_TEST]

# Chrome headless options
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
# optional minor anti-detect flags (still detectable)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Start Chrome with webdriver-manager (downloads matching chromedriver)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 1) Login to Facebook
    print("[INFO] Opening Facebook login...")
    driver.get("https://www.facebook.com/login")
    time.sleep(3)

    email = driver.find_element(By.ID, "email")
    pwd = driver.find_element(By.ID, "pass")
    email.clear(); email.send_keys(FB_USER)
    pwd.clear(); pwd.send_keys(FB_PASS)
    pwd.send_keys(Keys.RETURN)
    print("[INFO] Submitted login form, waiting...")
    time.sleep(6)  # wait for login

    # optional: check if login succeeded (simple url check)
    if "login" in driver.current_url.lower():
        print("[WARN] Still on login page — possible checkpoint/2FA. Check manually.")
    else:
        print("[INFO] Login appears successful. Current URL:", driver.current_url)

    # 2) Open target chat (group or user)
    chat_url = f"https://www.facebook.com/messages/t/{TARGET_ID}"
    print(f"[INFO] Opening chat: {chat_url}")
    driver.get(chat_url)
    time.sleep(6)

    # 3) Find message input box and send messages
    # Note: Facebook markup can change; try a few locators
    for i, msg in enumerate(messages, start=1):
        try:
            # Try common contenteditable textbox locators
            try:
                box = driver.find_element(By.XPATH, "//div[@contenteditable='true' and @role='textbox']")
            except:
                box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")

            # Click, send message and Enter
            box.click()
            # small typing simulation
            for ch in msg:
                box.send_keys(ch)
                time.sleep(0.01)
            box.send_keys(Keys.RETURN)

            print(f"[SENT] {i}/{len(messages)}: {msg[:40]}...")
            # human-like delay
            time.sleep(3 + random.random()*2)
        except Exception as e:
            print(f"[ERROR] Sending message {i} failed: {e}")
            time.sleep(5)

finally:
    print("[INFO] Finished. Quitting browser.")
    driver.quit()
