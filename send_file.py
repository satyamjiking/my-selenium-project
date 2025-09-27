import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

# load env vars (FB_USER, FB_PASS वगैरह future में काम आएंगे)
load_dotenv()

FILE_PATH = "file.txt"

# File पढ़ो
with open(FILE_PATH, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"[INFO] Loaded {len(lines)} lines from file.txt")

# Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# Render पर chromium install होगा, उसका path fixed होता है
service = Service("/usr/bin/chromedriver")

# Driver start
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    for i, line in enumerate(lines, 1):
        print(f"[INFO] Searching: {line}")
        driver.get("https://www.google.com")
        time.sleep(2)

        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(line)
        search_box.submit()

        time.sleep(2)
        print(f"[DONE] Line {i}: searched '{line}'")

finally:
    driver.quit()
    print("[INFO] Browser closed. Script finished.")
