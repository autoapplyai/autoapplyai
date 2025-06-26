import os
import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# ─────────────────────────────────────────────────────────────────────────────
# 1) Load your personal info
# ─────────────────────────────────────────────────────────────────────────────
with open("config/user_config.json") as f:
    user = json.load(f)

# ─────────────────────────────────────────────────────────────────────────────
# 2) Load the list of safe jobs
# ─────────────────────────────────────────────────────────────────────────────
with open("safe_jobs.json") as f:
    jobs = json.load(f)

# ─────────────────────────────────────────────────────────────────────────────
# 3) Configure headless Chrome to use the system chromedriver
# ─────────────────────────────────────────────────────────────────────────────
options = Options()
options.add_argument("--headless")               # no browser UI
options.add_argument("--no-sandbox")             # required on many servers
options.add_argument("--disable-dev-shm-usage")  # overcome limited /dev/shm
options.add_argument("--disable-gpu")            # recommended with headless

# Point at the chromedriver binary installed on PythonAnywhere
service = Service("/usr/bin/chromedriver")
driver  = webdriver.Chrome(service=service, options=options)

# ─────────────────────────────────────────────────────────────────────────────
# 4) Loop through each job and apply
# ─────────────────────────────────────────────────────────────────────────────
for job in jobs:
    title   = job["title"]
    company = job["company"]
    url     = job["link"]

    # Build safe file paths
    safe_title   = title.replace(" ", "_")
    safe_company = company.replace(" ", "_").replace(".", "")
    resume_path  = os.path.abspath(f"output/resumes/{safe_company}_{safe_title}_resume.txt")
    cover_path   = os.path.abspath(f"output/cover_letters/{safe_company}_{safe_title}_cover_letter.txt")

    print(f"➡️  Applying to {title} at {company}")
    driver.get(url)
    time.sleep(2)  # let the page finish loading

    # ── Fill text fields (if present) ──────────────────────────────────────────
    try:
        driver.find_element(By.NAME, "name").send_keys(user["name"])
        driver.find_element(By.NAME, "email").send_keys(user["email"])
        driver.find_element(By.NAME, "phone").send_keys(user["phone"])
    except Exception:
        pass  # skip if those fields aren't on this form

    # ── Upload resume ─────────────────────────────────────────────────────────
    try:
        driver.find_element(By.NAME, "resume").send_keys(resume_path)
    except Exception:
        print("⚠️  Resume upload field not found. Check your selector.")

    # ── Upload cover letter ──────────────────────────────────────────────────
    try:
        driver.find_element(By.NAME, "cover_letter").send_keys(cover_path)
    except Exception:
        print("⚠️  Cover‐letter upload field not found. Check your selector.")

    # ── Submit the form ──────────────────────────────────────────────────────
    try:
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print(f"✔️  Applied to {title} at {company}")
    except Exception:
        print("❌  Failed to submit—check your submit-button selector.")

    time.sleep(1)  # short pause before the next loop

# ─────────────────────────────────────────────────────────────────────────────
# 5) Clean up
# ─────────────────────────────────────────────────────────────────────────────
driver.quit()


