#!/usr/bin/env python3
import json
import feedparser
import requests
import time
from datetime import datetime

def scrape_wwr_rss():
    """Scrape We Work Remotely RSS feed"""
    url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
    try:
        print("Fetching WWR RSS feed...")
        feed = feedparser.parse(url)
        jobs = []
        
        if not feed.entries:
            print("⚠️ No entries found in RSS feed")
            return jobs
            
        for entry in feed.entries:
            # Extract company and title from RSS title format
            title_parts = entry.title.split(': ', 1)
            if len(title_parts) >= 2:
                company = title_parts[0].strip()
                job_title = title_parts[1].strip()
            else:
                company = "Unknown Company"
                job_title = entry.title.strip()
            
            jobs.append({
                "title": job_title,
                "company": company,
                "url": entry.link,
                "description": getattr(entry, 'summary', ''),
                "published": getattr(entry, 'published', ''),
                "location": "Remote",
                "source": "WeWorkRemotely"
            })
        
        print(f"✅ Found {len(jobs)} jobs from WWR RSS")
        return jobs
    except Exception as e:
        print(f"⚠️ WWR RSS failed: {e}")
        return []

def scrape_remoteok_api():
    """Scrape RemoteOK API"""
    url = "https://remoteok.com/api"
    headers = {
        "User-Agent": "AutoapplyAI/1.0 (Educational Purpose)"
    }
    
    try:
        print("Fetching RemoteOK API...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # RemoteOK returns array, first item is usually metadata
        if isinstance(data, list) and len(data) > 1:
            jobs_data = data[1:]  # Skip metadata
        else:
            jobs_data = data if isinstance(data, list) else []
        
        jobs = []
        for job_data in jobs_data[:20]:  # Limit to first 20 jobs
            if not isinstance(job_data, dict):
                continue
                
            jobs.append({
                "title": job_data.get("position", "Unknown Position"),
                "company": job_data.get("company", "Unknown Company"),
                "url": f"https://remoteok.com/remote-jobs/{job_data.get('id', '')}",
                "description": job_data.get("description", ""),
                "location": job_data.get("location", "Remote"),
                "tags": job_data.get("tags", []),
                "source": "RemoteOK"
            })
        
        print(f"✅ Found {len(jobs)} jobs from RemoteOK")
        return jobs
    except Exception as e:
        print(f"⚠️ RemoteOK API failed: {e}")
        return []

def load_fallback_jobs():
    """Load jobs from config/job_list.json as fallback"""
    try:
        with open("config/job_list.json", "r") as f:
            fallback_jobs = json.load(f)
        
        # Convert to expected format
        formatted_jobs = []
        for job in fallback_jobs:
            formatted_jobs.append({
                "title": job.get("title", ""),
                "company": job.get("company", ""),
                "description": job.get("description", ""),
                "url": f"mailto:{job.get('email', '')}",  # Convert email to URL format
                "location": "Various",
                "source": "Local Config"
            })
        
        print(f"✅ Loaded {len(formatted_jobs)} fallback jobs from config")
        return formatted_jobs
    except Exception as e:
        print(f"⚠️ Failed to load fallback jobs: {e}")
        return []

def filter_jobs_by_profile(jobs):
    """Filter jobs based on user profile"""
    try:
        with open("config/user_profile.json", "r") as f:
            profile = json.load(f)
        
        user_skills = [skill.lower() for skill in profile.get("skills", [])]
        preferred_titles = [title.lower() for title in profile.get("job_preferences", {}).get("preferred_titles", [])]
        
        filtered_jobs = []
        for job in jobs:
            title_lower = job["title"].lower()
            desc_lower = job["description"].lower()
            
            # Check if job matches user skills or preferred titles
            skill_match = any(skill in title_lower or skill in desc_lower for skill in user_skills)
            title_match = any(pref_title in title_lower for pref_title in preferred_titles)
            
            if skill_match or title_match or not user_skills:  # Include all if no skills specified
                filtered_jobs.append(job)
        
        print(f"✅ Filtered to {len(filtered_jobs)} relevant jobs")
        return filtered_jobs
    except Exception as e:
        print(f"⚠️ Profile filtering failed, keeping all jobs: {e}")
        return jobs

def main():
    all_jobs = []
    
    # Try multiple sources
    print("🔍 Starting job search from multiple sources...")
    
    # Source 1: We Work Remotely RSS
    wwr_jobs = scrape_wwr_rss()
    all_jobs.extend(wwr_jobs)
    
    # Small delay between API calls
    time.sleep(1)
    
    # Source 2: RemoteOK API
    remoteok_jobs = scrape_remoteok_api()
    all_jobs.extend(remoteok_jobs)
    
    # If no jobs found, use fallback
    if not all_jobs:
        print("⚠️ No jobs found from external sources, using fallback...")
        all_jobs = load_fallback_jobs()
    
    if not all_jobs:
        print("❌ No jobs found from any source!")
        return
    
    # Remove duplicates by URL
    seen_urls = set()
    unique_jobs = []
    for job in all_jobs:
        if job["url"] not in seen_urls:
            seen_urls.add(job["url"])
            unique_jobs.append(job)
    
    # Filter jobs based on user profile
    filtered_jobs = filter_jobs_by_profile(unique_jobs)
    
    # Save to jobs.json
    with open("jobs.json", "w") as f:
        json.dump(filtered_jobs, f, indent=2)
    
    print(f"✅ Successfully wrote {len(filtered_jobs)} jobs to jobs.json")
    
    # Also create the simple URL format that some scripts expect
    simple_urls = [job["url"] for job in filtered_jobs]
    with open("job_urls.json", "w") as f:
        json.dump(simple_urls, f, indent=2)
    
    # Display summary
    print("\n📊 Job Search Summary:")
    print(f"Total jobs found: {len(all_jobs)}")
    print(f"After deduplication: {len(unique_jobs)}")
    print(f"After filtering: {len(filtered_jobs)}")
    
    if filtered_jobs:
        print("\n🎯 Sample jobs found:")
        for i, job in enumerate(filtered_jobs[:3], 1):
            print(f"{i}. {job['title']} at {job['company']} ({job['source']})")

if __name__ == "__main__":
    main()
            seen.add(j["url"])
            unique.append(j)

    with open("jobs.json", "w") as f:
        json.dump(unique, f, indent=2)
    print(f"✅ Wrote {len(unique)} jobs to jobs.json")

if __name__ == "__main__":
    main()
