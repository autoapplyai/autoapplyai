import json
from scam_filter import is_scam

# Load jobs from JSON file
with open("jobs.json") as f:
    jobs = json.load(f)

safe_jobs = []

for job in jobs:
    description = job.get("description", "")
    link = job.get("link", "")
    if is_scam(description, link):
        print(f"❌ Skipping suspicious job: {job.get('title')}")
    else:
        print(f"✅ Passing safe job: {job.get('title')}")
        safe_jobs.append(job)

# Save filtered jobs to new file
with open("safe_jobs.json", "w") as f:
    json.dump(safe_jobs, f, indent=2)
