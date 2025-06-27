#!/usr/bin/env python3
import os, sys, time, json, yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
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
        try:
            driver.get(url)
        except WebDriverException as e:
            msg = e.msg.splitlines()[0]
            print(f"❌ Cannot reach {url}: {msg} – skipping\n")
            continue
        time.sleep(1)
        try:
            driver.find_element("name","name").send_keys(name)
            driver.find_element("name","email").send_keys(email)
            driver.find_element("name","resume").send_keys(resume)
            driver.find_element("name","cover_letter").send_keys(cl)
            driver.find_element("css selector","button[type=submit]").click()
            time.sleep(2)
            print("✅  Submitted successfully\n")
        except Exception as e:
            print(f"❌  Failed on {url}: {e}\n")
    driver.quit()

if __name__ == "__main__":
    main()
