import json, os

# 1) load your profile
with open("config/user_config.json") as f:
    user = json.load(f)

# 2) load the filtered jobs
with open("safe_jobs.json") as f:
    jobs = json.load(f)

# 3) plain-text resume template
RESUME_TEMPLATE = """Name: {name}
Email: {email}
Phone: {phone}

Applying for: {job_title} at {company}

Professional Summary:
{experience_summary}

Key Skills:
{skills}
"""

# 4) ensure output folder exists
os.makedirs("output/resumes", exist_ok=True)

# 5) render one resume per job
for job in jobs:
    skills_str = ", ".join(user["skills"])
    content = RESUME_TEMPLATE.format(
        name=user["name"],
        email=user["email"],
        phone=user["phone"],
        job_title=job["title"],
        company=job["company"],
        experience_summary=user["experience_summary"],
        skills=skills_str
    )
    # safe filename
    fname = f"output/resumes/{job['company']}_{job['title'].replace(' ','_')}_resume.txt"
    with open(fname, "w") as out:
        out.write(content)
    print(f"Generated resume → {fname}")

