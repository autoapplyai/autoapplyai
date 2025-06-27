#!/usr/bin/env python3
import os
import sys
import time
import json
import yaml

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """
    Launch headless Ubuntu Chromium with webdriver-manager.
    """
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # Point at the APT-installed Chromium
    opts.binary_location = "/usr/bin/chromium-browser"
    # Auto-download & install matching ChromeDriver
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)

def main():
    # 1) Load config.yaml
    try:
        cfg = yaml.safe_load(open("config.yaml"))
    except Exception as e:
        print(f"❌ Failed to load config.yaml: {e}")
        sys.exit(1)

    # 2) Extract your name & email
    name  = cfg.get("applicant_name")
    email = cfg.get("applicant_email")
    if not name or not email:
        print("❌ config.yaml must define applicant_name and applicant_email")
        sys.exit(1)

    # 3) Compute PDF paths (from output/)
    resume_pdf = os.path.abspath(f"output/{name}_resume.pdf")
    cl_pdf     = os.path.abspath(f"output/{name}_CL.pdf")
    for path in (resume_pdf, cl_pdf):
        if not os.path.exists(path):
            print(f"❌ Required file not found: {path}")
            sys.exit(1)

    # 4) Load list of jobs
    try:
        jobs = json.load(open("jobs.json"))
    except Exception as e:
        print(f"❌ Failed to load jobs.json: {e}")
        sys.exit(1)

    if not jobs:
        print("⚠️ No jobs found in jobs.json; exiting.")
        sys.exit(0)

    # 5) Start Selenium
    driver = setup_driver()

    # 6) Loop through each job and submit
    for job in jobs:
        url     = job.get("url")
        print(f"➡️  Applying to {url}")
        try:
            driver.get(url)
            time.sleep(1)  # allow page load

            # Fill out form fields (update selectors if needed)
            driver.find_element("name", "name").send_keys(name)
            driver.find_element("name", "email").send_keys(email)
            driver.find_element("name", "resume").send_keys(resume_pdf)
            driver.find_element("name", "cover_letter").send_keys(cl_pdf)

            # Click submit
            driver.find_element("css selector", "button[type=submit]").click()
            time.sleep(2)

            print("✅  Submitted successfully\n")
        except Exception as e:
            print(f"❌  Failed to apply: {e}\n")

    driver.quit()

if __name__ == "__main__":
    main()
