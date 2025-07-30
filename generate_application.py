#!/usr/bin/env python3
import os, sys, time, json, yaml
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

def setup_driver():
    opts = uc.ChromeOptions()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--headless")
    driver = uc.Chrome(options=opts)
    return driver

def extract_skills(job_description, skills):
    tokens = word_tokenize(job_description.lower())
    tokens = [t for t in tokens if t not in stopwords.words('english')]
    job_skills = [t for t in tokens if t in [skill.lower() for skill in skills]]
    return job_skills

def calculate_similarity(job_skills, applicant_skills):
    vectorizer = CountVectorizer()
    job_skills_vector = vectorizer.fit_transform([' '.join(job_skills)])
    applicant_skills_vector = vectorizer.transform([' '.join(applicant_skills)])
    similarity = cosine_similarity(job_skills_vector, applicant_skills_vector)
    return similarity[0][0]

def generate_cover_letter(job_title, company, matching_skills):
    # Use a simple template for now
    cover_letter = f"Dear Hiring Manager,\n\nI am excited to apply for the {job_title} role at {company}.\n\nWith my skills in {', '.join(matching_skills)}, I believe I would be a great fit for this position.\n\nThank you for considering my application.\n\nSincerely,\n[Your Name]"
    return cover_letter

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
        msg = str(e).splitlines()[0]
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
    skills = cfg.get("skills")
    if not name or not email or not skills:
        print("❌ config.yaml must define applicant_name, applicant_email, and skills")
        sys.exit(1)

    resume = os.path.join(root, "output", f"{name}_resume.pdf")
    for p in (resume,):
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
        job_description = job.get("description", "")
        job_skills = extract_skills(job_description, skills)
        similarity = calculate_similarity(job_skills, [skill.lower() for skill in skills])
        if similarity >= 0.75:
            print(f"➡️  Applying to {url}")
            cl = generate_cover_letter(job.get("title", ""), job.get("company", ""), job_skills)
            fill_form(driver, url, name, email, resume, cl)
    driver.quit()

if __name__ == "__main__":
    main()
