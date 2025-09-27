# send_file.py
import os
import time
from dotenv import load_dotenv

load_dotenv()

FB_USER = os.getenv("FB_USER")
FB_PASS = os.getenv("FB_PASS")
TARGET_ID = os.getenv("TARGET_ID")
FILE_PATH = "file.txt"

if not FB_USER or not FB_PASS:
    print("FB_USER/FB_PASS missing. Use .env or set env vars.")
    exit(1)

with open(FILE_PATH, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Will send {len(lines)} lines to target {TARGET_ID} (demo run).")
for i, line in enumerate(lines, 1):
    print(f"{i}: {line}")
    time.sleep(1)

print("Demo complete.")
