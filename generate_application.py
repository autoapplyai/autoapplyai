#!/usr/bin/env python3
import os, sys, time, json, yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--remote-debugging-port=9222")
    opts.add_argument("--single-process")
    opts.add_argument("--disable-extensions")
    opts.binary_location = "/usr/bin/chromium-browser"
    svc = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=svc, options=opts)

def fill_form(driver, url, name, email, resume, cl):
    try:
        driver.get(url)
        time.sleep(1)

        # Find fields by placeholder or label
        fields = {
            "name": None,
            "email": None,
            "resume": None,
            "cover_letter": None
        }

        for field_name, field_value in fields.items():
            try:
                field = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, f"//input[@placeholder*='{field_name}' or @name='{field_name}']"))
                )
                fields[field_name] = field
            except TimeoutException:
                print(f"Field '{field_name}' not found")

        # Fill out fields
        if fields["name"]: fields["name"].send_keys(name)
        if fields["email"]: fields["email"].send_keys(email)

        # Handle file uploads
        if fields["resume"]: fields["resume"].send_keys(resume)
        if fields["cover_letter"]: fields["cover_letter"].send_keys(cl)

        # Submit form
        try:
            submit_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            submit_button.click()
            time.sleep(2)
            print("✅  Submitted successfully\n")
        except TimeoutException:
            print("❌  Submit button not found")

    except WebDriverException as e:
        msg = e.msg.splitlines()[0]
        print(f"❌ Cannot reach {url}: {msg} – skipping\n")

def main():
    root = os.getcwd()
    cfg_path = os.path.join(root, "config.yaml")
    try:
        cfg = yaml.safe_load(open(cfg_path))
    except Exception as e:
        print(f"❌ Could not load config.yaml: {e}")
        sys.exit(1)

    name  = cfg.get("applicant_name")
    email = cfg.get("applicant_email")
    if not name or not email:
        print("❌ config.yaml must define applicant_name and applicant_email")
        sys.exit(1)

    resume = os.path.join(root, "output", f"{name}_resume.pdf")
    cl     = os.path.join(root, "output", f"{name}_CL.pdf")
    for p in (resume, cl):
        if not os.path.exists(p):
            print(f"❌ Missing file: {p}")
            sys.exit(1)

    jobs = json.load(open(os.path.join(root, "jobs.json")))
    if not jobs:
        print("⚠️  No jobs found in jobs.json")
        sys.exit(0)

    driver = setup_driver()
    for job in jobs:
        url = job["url"]
        print(f"➡️  Applying to {url}")
        fill_form(driver, url, name, email, resume, cl)
    driver.quit()

if __name__ == "__main__":
    main()
