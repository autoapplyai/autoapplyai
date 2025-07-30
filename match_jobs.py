import requests
import json
import os

def get_job_matches(profile_path="config/user_profile.json", max_results=10):
    """Get job matches from multiple sources"""
    
    # First try to use jobs from find_jobs.py
    if os.path.exists("jobs.json"):
        try:
            with open("jobs.json", "r") as f:
                existing_jobs = json.load(f)
            if existing_jobs:
                print(f"✅ Using {len(existing_jobs)} jobs from local jobs.json")
                return existing_jobs[:max_results]
        except Exception as e:
            print(f"⚠️ Could not load existing jobs.json: {e}")
    
    # Load user profile for filtering
    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
    except Exception as e:
        print(f"❌ Could not load profile from {profile_path}: {e}")
        return []

    # Extract search criteria from profile
    user_skills = [s.lower().strip() for s in profile.get("skills", [])]
    job_prefs = profile.get("job_preferences", {})
    preferred_titles = [t.lower().strip() for t in job_prefs.get("preferred_titles", [])]
    location = profile.get("location", "").lower().strip()
    
    print(f"🔍 Searching for jobs matching skills: {user_skills}")
    print(f"🎯 Preferred titles: {preferred_titles}")

    # Fetch from RemoteOK API as backup
    matches = fetch_from_remoteok(user_skills, preferred_titles, location, max_results)
    
    return matches

def fetch_from_remoteok(user_skills, preferred_titles, location, max_results):
    """Fetch jobs from RemoteOK API"""
    url = "https://remoteok.com/api"
    headers = {"User-Agent": "AutoapplyAI/1.0"}

    try:
        print("🌐 Fetching from RemoteOK API...")
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        # RemoteOK returns array with first item as metadata
        if isinstance(data, list) and len(data) > 1:
            jobs_data = data[1:]
        else:
            jobs_data = []

        print(f"📥 Fetched {len(jobs_data)} jobs from RemoteOK")

        matches = []
        for job in jobs_data:
            if not isinstance(job, dict):
                continue

            title = job.get("position", "").lower()
            company = job.get("company", "")
            tags = [t.lower() for t in job.get("tags", []) if isinstance(t, str)]
            job_location = job.get("location", "").lower()
            description = job.get("description", "").lower()

            # Scoring system for better matches
            score = 0
            
            # Check for preferred title matches (highest priority)
            title_match = any(pref_title in title for pref_title in preferred_titles)
            if title_match:
                score += 10
            
            # Check for skill matches in title (high priority)
            title_skill_match = any(skill in title for skill in user_skills)
            if title_skill_match:
                score += 8
            
            # Check for skill matches in tags (medium priority)
            tag_skill_match = any(skill in tags for skill in user_skills)
            if tag_skill_match:
                score += 5
            
            # Check for skill matches in description (low priority)
            desc_skill_match = any(skill in description for skill in user_skills)
            if desc_skill_match:
                score += 2
            
            # Location preference (if specified)
            if location and location in job_location:
                score += 3
            elif not location:  # No location preference
                score += 1

            # Only include jobs with some relevance
            if score > 0:
                job_url = job.get("url", "")
                if not job_url and job.get("id"):
                    job_url = f"https://remoteok.com/remote-jobs/{job.get('id')}"
                
                matches.append({
                    "title": job.get("position", "").strip(),
                    "company": company.strip(),
                    "url": job_url,
                    "description": job.get("description", ""),
                    "location": job.get("location", "Remote"),
                    "tags": job.get("tags", []),
                    "score": score,
                    "source": "RemoteOK"
                })

        # Sort by relevance score (highest first)
        matches.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Remove score from final output and limit results
        final_matches = []
        for match in matches[:max_results]:
            match.pop("score", None)  # Remove score field
            final_matches.append(match)
        
        print(f"✅ Found {len(final_matches)} relevant matches")
        return final_matches

    except Exception as e:
        print(f"❌ Failed to fetch from RemoteOK: {e}")
        return []

def save_matches_to_file(matches, filename="matched_jobs.json"):
    """Save matched jobs to a file"""
    try:
        with open(filename, "w") as f:
            json.dump(matches, f, indent=2)
        print(f"💾 Saved {len(matches)} matches to {filename}")
    except Exception as e:
        print(f"❌ Failed to save matches: {e}")

# Main execution
if __name__ == "__main__":
    print("🚀 Starting job matching process...")
    jobs = get_job_matches()
    
    print(f"\n🎯 Job matching results:")
    if jobs:
        save_matches_to_file(jobs)
        print(f"\nTop matches:")
        for idx, job in enumerate(jobs[:5], 1):
            print(f" {idx}. {job['title']} @ {job['company']}")
            print(f"    📍 {job.get('location', 'Remote')}")
            print(f"    🔗 {job['url']}")
            if job.get('tags'):
                print(f"    🏷️  Tags: {', '.join(job['tags'][:5])}")
            print()
    else:
        print(" ❌ No jobs matched your profile.")
    
    input("Press Enter to exit...")

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



