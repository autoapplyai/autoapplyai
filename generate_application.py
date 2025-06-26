#!/usr/bin/env python3
import json, time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

def load_jobs(path="jobs.json"):
    with open(path) as f:
        return json.load(f)

def setup_driver():
    opts = Options()
    opts.add_argument("--headless=new")       # headless
    opts.add_argument("--no-sandbox")         # required in Actions
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(30)
    return driver

def apply_job(driver, job):
    url = job.get("apply_url")
    company = job.get("company", "<unknown>")
    title   = job.get("title", "<unknown>")
    print(f"\n➡️  Applying to {title} at {company}")

    # 1) Try loading the page
    try:
        driver.get(url)
    except WebDriverException as e:
        print(f"⚠️  Skipping {company}: cannot load URL ({e.msg.splitlines()[0]})")
        return

    sel = job.get("selectors", {})
    # 2) Upload resume
    try:
        resume_input = driver.find_element("css selector", sel["resume"])
        resume_input.send_keys(job.get("resume_path", "resume.pdf"))
    except (KeyError, NoSuchElementException):
        print("⚠️  Resume upload field not found. Check your selector.")

    # 3) Upload cover letter
    try:
        cover_input = driver.find_element("css selector", sel["cover_letter"])
        cover_input.send_keys(job.get("cover_letter_path", "cover_letter.pdf"))
    except (KeyError, NoSuchElementException):
        print("⚠️  Cover-letter upload field not found. Check your selector.")

    # 4) Hit submit
    try:
        submit_btn = driver.find_element("css selector", sel["submit"])
        submit_btn.click()
        time.sleep(2)
        print("✅  Submitted successfully")
    except (KeyError, NoSuchElementException):
        print("❌  Failed to submit—check your submit-button selector.")

def main():
    jobs = load_jobs()
    driver = setup_driver()
    for job in jobs:
        apply_job(driver, job)
    driver.quit()

if __name__ == "__main__":
    main()
