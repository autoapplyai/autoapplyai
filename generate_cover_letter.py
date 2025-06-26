import json, os

# 1) load your profile
with open("config/user_config.json") as f:
    user = json.load(f)

# 2) load the filtered jobs
with open("safe_jobs.json") as f:
    jobs = json.load(f)

# 3) plain-text cover-letter template
CL_TEMPLATE = """Dear {company},

I’m excited to apply for the {job_title} position at {company}. With my background in {skills} and experience summarized as:
“{job_description}”
I’m confident I can help {company} succeed.

Thank you for considering my application.

Best regards,
{name}
"""

# 4) ensure output folder exists
os.makedirs("output/cover_letters", exist_ok=True)

# 5) render one cover letter per job
for job in jobs:
    skills_str = ", ".join(user["skills"])
    desc = job["description"]
    snippet = desc if len(desc) < 120 else desc[:120] + "..."
    content = CL_TEMPLATE.format(
        company=job["company"],
        job_title=job["title"],
        skills=skills_str,
        job_description=snippet,
        name=user["name"]
    )
    # safe filename
    fname = f"output/cover_letters/{job['company']}_{job['title'].replace(' ','_')}_cover_letter.txt"
    with open(fname, "w") as out:
        out.write(content)
    print(f"Generated cover letter → {fname}")



