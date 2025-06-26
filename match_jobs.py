import requests
import json

def get_job_matches(profile_path="config/user_profile.json", max_results=3):
    # — Load your filter profile —
    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    keywords = [kw.lower().strip() for kw in profile.get("job_titles", [])]
    location = profile.get("location", "").lower().strip()
    skills   = [s.lower().strip() for s in profile.get("skills", [])]

    # — Fetch from RemoteOK API —
    url     = "https://remoteok.com/api"
    headers = {"User-Agent": "AutoapplyAI/1.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # — DEBUG: show raw fetch stats —
        print(f"\nDEBUG: fetched {len(data)} total postings from RemoteOK")
        for i, job in enumerate(data[:5], 1):
            pos  = job.get("position", "<no title>")
            comp = job.get("company", "<no company>")
            loc  = job.get("location", "<no location>")
            print(f"  {i}. {pos} @ {comp} — loc: {loc}")

    except Exception as e:
        print("❌ Failed to fetch jobs:", e)
        return []

    # — Filter by title keywords OR skills, plus location —
    matches = []
    for job in data:
        if not isinstance(job, dict):
            continue

        title = job.get("position", "").lower()
        tags  = [t.lower() for t in job.get("tags", [])]
        loc   = job.get("location", "").lower()

        title_match = any(kw in title for kw in keywords)
        tag_match   = any(kw in tags for kw in keywords)
        skill_match = any(s in title or s in tags for s in skills)
        loc_match   = not location or (location in loc)

        if loc_match and (title_match or tag_match or skill_match):
            matches.append({
                "title":   job.get("position", "").strip(),
                "company": job.get("company",  "").strip(),
                "url":     job.get("url",      "").strip()
            })

        if len(matches) >= max_results:
            break

    return matches

# ——— MAIN — allows direct execution and pauses for you to read ——————
if __name__ == "__main__":
    jobs = get_job_matches()
    print("\n🔍 Jobs returned by get_job_matches():")
    if jobs:
        for idx, job in enumerate(jobs, 1):
            print(f" {idx}. {job['title']} @ {job['company']}")
            print(f"     → {job['url']}\n")
    else:
        print(" (No jobs matched your profile.)")
    input("Press Enter to exit…")



