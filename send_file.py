import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 🔹 Env variables (Replit Secrets se set करना)
FB_USER = os.getenv("FB_USER")
FB_PASS = os.getenv("FB_PASS")
TARGET_ID = os.getenv("TARGET_ID")
DELAY = int(os.getenv("DELAY", "40"))   # default 40 sec
MAX_TEST = int(os.getenv("MAX_TEST", "0"))  # 0 = unlimited

# 🔹 file.txt से सारे messages read करो
with open("file.txt", "r", encoding="utf-8") as f:
    messages = [line.strip() for line in f if line.strip()]

# 🔹 Chrome options (Replit/Headless env ke liye)
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def login_facebook():
    driver.get("https://mbasic.facebook.com/")  # Lite version fast hai
    time.sleep(2)

    # login form fill
    driver.find_element(By.NAME, "email").send_keys(FB_USER)
    driver.find_element(By.NAME, "pass").send_keys(FB_PASS)
    driver.find_element(By.NAME, "login").click()
    time.sleep(3)

def send_message(msg):
    chat_url = f"https://mbasic.facebook.com/messages/read/?tid=cid.c.{TARGET_ID}"
    driver.get(chat_url)
    time.sleep(2)

    try:
        box = driver.find_element(By.NAME, "body")
        box.send_keys(msg)
        driver.find_element(By.NAME, "send").click()
        print(f"[+] Sent: {msg}")
    except Exception as e:
        print(f"[!] Error sending: {e}")

def main():
    login_facebook()

    count = 0
    while True:
        for msg in messages:
            send_message(msg)
            count += 1

            if MAX_TEST and count >= MAX_TEST:
                print("Max limit reached, stopping.")
                driver.quit()
                return

            time.sleep(DELAY)  # wait before next message

if __name__ == "__main__":
    main()
