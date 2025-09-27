import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# ===== Environment Variables =====
FB_ID = os.getenv("FB_ID")
FB_P = os.getenv("FB_P")
TARGET_ID = os.getenv("TARGET_ID")

# ===== Selenium Chrome Options =====
chrome_options = Options()
chrome_options.add_argument("--headless")        # Headless mode
chrome_options.add_argument("--no-sandbox")      # Sandbox disable (Render fix)
chrome_options.add_argument("--disable-dev-shm-usage")

# ===== Chrome Service =====
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

# ===== Facebook Login =====
driver.get("https://mbasic.facebook.com")

driver.find_element(By.NAME, "email").send_keys(FB_ID)
driver.find_element(By.NAME, "pass").send_keys(FB_P)
driver.find_element(By.NAME, "login").click()

time.sleep(3)

# ===== Target Chat Open =====
chat_url = f"https://mbasic.facebook.com/messages/read/?tid={TARGET_ID}"
driver.get(chat_url)

time.sleep(3)

# ===== Read File =====
with open("file.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

# ===== Send Messages =====
for line in lines:
    textarea = driver.find_element(By.NAME, "body")
    textarea.clear()
    textarea.send_keys(line.strip())

    driver.find_element(By.NAME, "send").click()
    time.sleep(40)   # 40 sec delay between messages

driver.quit()
