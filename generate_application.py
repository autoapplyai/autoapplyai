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
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.binary_location = "/usr/bin/chromium-browser"
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)

def main():
    # Determine repo root (one level up)
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    cfg_path  = os.path.join(repo_root, "config.yaml")
    try:
        cfg = yaml.safe_load(open(cfg_path))
    except Exception as e:
        print(f"❌ Failed to load {cfg_path}: {e}")
        sys.exit(1)

    name  = cfg.get("applicant_name")
    email = cfg.get("applicant_email")
    if not name or not email:
        print("❌ config.yaml must define applicant_name and applicant_email")
        sys.exit(1)

    output_dir = os.path.join(repo_root, "output")
    resume_pdf = os.path.join(output_dir, f"{name}_resume.pdf")
    cl_pdf     = os.path.join(output_dir, f"{name}_CL.pdf")
    for p in (resume_pdf, cl_pdf):
        if not os.path.exists(p):
            print(f"❌ Required file not found: {p}")
            sys.exit(1)

    jobs_path = os.path.join(repo_root, "jobs.json")
    try:
        jobs = json.load(open(jobs_path))
    except Exception as e:
        print(f"❌ Failed to load {jobs_path}: {e}")
        sys.exit(1)
    if not jobs:
        print("⚠️ No jobs found; exiting.")
        sys.exit(0)

    driver = setup_driver()

    for job in jobs:
        url = job.get("url")
        print(f"➡️  Applying to {url}")
        try:
            driver.get(url)
            time.sleep(1)
            driver.find_element("name", "name").send_keys(name)
            driver.find_element("name", "email").send_keys(email)
            driver.find_element("name", "resume").send_keys(resume_pdf)
            driver.find_element("name", "cover_letter").send_keys(cl_pdf)
            driver.find_element("css selector", "button[type=submit]").click()
            time.sleep(2)
            print("✅  Submitted successfully\\n")
        except Exception as e:
            print(f"❌  Failed to apply to {url}: {e}\\n")

    driver.quit()

if __name__ == "__main__":
    main()
