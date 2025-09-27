from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os

# ===== Chrome Options =====
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Binary location set karna zaroori hai (Render ke liye)
chrome_options.binary_location = "/usr/bin/chromium-browser"

# ===== Chrome Service =====
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

# ===== Example Logic =====
try:
    driver.get("https://www.google.com")
    print("Page Title:", driver.title)

    # agar env se user / pass lena ho
    fb_user = os.getenv("FB_USER")
    fb_pass = os.getenv("FB_PASS")

    # just test ke liye print
    print("FB_USER:", fb_user)
    print("FB_PASS:", fb_pass)

    time.sleep(3)

finally:
    driver.quit()
