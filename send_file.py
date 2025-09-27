import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ===== Environment Variables =====
FB_ID = os.getenv("FB_ID")
FB_P = os.getenv("FB_P")
TARGET_ID = os.getenv("TARGET_ID")   # group id ya user id

# ===== Selenium Chrome Options =====
chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# ===== Facebook Login =====
driver.get("https://mbasic.facebook.com/")

# Login
driver.find_element(By.NAME, "email").send_keys(FB_ID)
driver.find_element(By.NAME, "pass").send_keys(FB_P)
driver.find_element(By.NAME, "login").click()

time.sleep(3)

# ===== Target Chat Open =====
chat_url = f"https://mbasic.facebook.com/messages/t/{TARGET_ID}"
driver.get(chat_url)

time.sleep(3)

# ===== Read File =====
with open("file.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

# ===== Send Messages One by One =====
for line in lines:
    msg_box = driver.find_element(By.NAME, "body")
    msg_box.clear()
    msg_box.send_keys(line.strip())

    send_btn = driver.find_element(By.NAME, "send")
    send_btn.click()

    print(f"Sent: {line.strip()}")
    time.sleep(40)   # 40 second delay

driver.quit()
