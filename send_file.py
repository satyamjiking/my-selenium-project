from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # chromium binary का path
    chrome_options.binary_location = "/usr/bin/chromium"

    # chromedriver का path
    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://www.google.com")
        print("✅ Browser opened successfully")
        print("Page Title:", driver.title)
        time.sleep(3)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
