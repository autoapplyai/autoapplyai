#!/usr/bin/env python3
import os
import time
import json
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from jinja2 import Environment, FileSystemLoader
import weasyprint

def setup_driver():
    """
    Launch headless Chromium (from ubuntu-latest) with a matching driver.
    """
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # Point to the APT-installed Chromium binary
    opts.binary_location = "/usr/bin/chromium-browser"
    # Auto-download the correct ChromeDriver
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)

def render_cover_letter(context, template_path, output_dir="output"):
    """
    Render HTML template with Jinja2, convert to PDF with WeasyPrint.
    """
    env = Environment(loader=FileSystemLoader(os.getcwd()))
    template = env.get_template(template_path)
    html = template.render(context)

    os.makedirs(output_dir, exist_ok=True)
    out_pdf = os.path.join(output_dir, f"{context['applicant_name']}_CL.pdf")
    weasyprint.HTML(string=html).write_pdf(out_pdf)
    return out_pdf

def main():
    # Load user/config data
    cfg = yaml.safe_load(open("config.yaml"))
    applicant = cfg["applicant"]
    resume_pdf = cfg["resume_pdf"]
    cl_template = cfg["cover_letter_template"]  # e.g. "cover_letter.html"
    cl_context_base = cfg["cover_letter_context"]  # dict of static fields

    # Load jobs to apply for
    with open("jobs.json") as f:
        jobs = json.load(f)

    driver = setup_driver()

    for job in jobs:
        url = job["url"]
        title = job.get("title", "")
        company = job.get("company", "")
        print(f"➡️  Applying to {url}")

        driver.get(url)
        time.sleep(1)  # let page load

        # === Fill out basic fields ===
        # Update these selectors to match the application form you’re targeting
        driver.find_element("name", "name").send_keys(applicant["name"])
        driver.find_element("name", "email").send_keys(applicant["email"])
        driver.find_element("name", "resume").send_keys(os.path.abspath(resume_pdf))

        # === Generate & upload cover letter PDF ===
        cl_context = {
            **cl_context_base,
            "applicant_name": applicant["name"],
            "job_title": title,
            "company": company
        }
        cl_pdf = render_cover_letter(cl_context, cl_template)
        driver.find_element("name", "cover_letter").send_keys(os.path.abspath(cl_pdf))

        # === Submit ===
        driver.find_element("css selector", "button[type=submit]").click()
        time.sleep(2)

        print("✅  Submitted successfully\n")

    driver.quit()

if __name__ == "__main__":
    main()
