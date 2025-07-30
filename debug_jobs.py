#!/usr/bin/env python3
"""
Debug script to identify job finding issues
"""
import json
import os
import requests
import feedparser

def check_files():
    """Check if required files exist"""
    print("📁 Checking file structure...")
    
    required_files = [
        "config/user_profile.json",
        "config/user_config.json", 
        "config/job_list.json"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                print(f"✅ {file_path} - OK ({len(data)} items)")
            except Exception as e:
                print(f"❌ {file_path} - Invalid JSON: {e}")
        else:
            print(f"❌ {file_path} - Missing")
    
    # Check output files
    output_files = ["jobs.json", "safe_jobs.json"]
    for file_path in output_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                print(f"📄 {file_path} - Found ({len(data)} jobs)")
                if data:
                    print(f"   Sample: {data[0].get('title', 'No title')} @ {data[0].get('company', 'No company')}")
            except Exception as e:
                print(f"❌ {file_path} - Invalid JSON: {e}")
        else:
            print(f"📄 {file_path} - Not found")

def test_wwr_rss():
    """Test We Work Remotely RSS feed"""
    print("\n🔍 Testing WeWorkRemotely RSS...")
    
    url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
    try:
        feed = feedparser.parse(url)
        print(f"✅ RSS parsed successfully")
        print(f"   Entries found: {len(feed.entries)}")
        
        if feed.entries:
            entry = feed.entries[0]
            print(f"   Sample entry: {entry.title}")
            print(f"   Link: {entry.link}")
        else:
            print("⚠️ No entries in RSS feed")
            
    except Exception as e:
        print(f"❌ RSS parsing failed: {e}")

def test_remoteok_api():
    """Test RemoteOK API"""
    print("\n🌐 Testing RemoteOK API...")
    
    url = "https://remoteok.com/api"
    headers = {"User-Agent": "AutoapplyAI/1.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✅ API response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Data type: {type(data)}")
            print(f"   Items count: {len(data) if isinstance(data, list) else 'N/A'}")
            
            if isinstance(data, list) and len(data) > 1:
                sample_job = data[1]  # Skip metadata
                print(f"   Sample job: {sample_job.get('position', 'No title')}")
                print(f"   Company: {sample_job.get('company', 'No company')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API request failed: {e}")

def analyze_user_profile():
    """Analyze user profile for job matching"""
    print("\n👤 Analyzing user profile...")
    
    try:
        with open("config/user_profile.json", 'r') as f:
            profile = json.load(f)
        
        skills = profile.get("skills", [])
        job_prefs = profile.get("job_preferences", {})
        preferred_titles = job_prefs.get("preferred_titles", [])
        
        print(f"✅ Profile loaded")
        print(f"   Skills: {skills}")
        print(f"   Preferred titles: {preferred_titles}")
        print(f"   Location: {profile.get('location', 'Not set')}")
        print(f"   Remote preference: {job_prefs.get('remote', 'Not set')}")
        
    except Exception as e:
        print(f"❌ Profile analysis failed: {e}")

def run_job_search_test():
    """Run a complete job search test"""
    print("\n🚀 Running complete job search test...")
    
    try:
        # Import and run find_jobs
        print("   Importing find_jobs module...")
        import find_jobs
        
        print("   Running job search...")
        find_jobs.main()
        
        # Check results
        if os.path.exists("jobs.json"):
            with open("jobs.json", 'r') as f:
                jobs = json.load(f)
            print(f"✅ Job search completed: {len(jobs)} jobs found")
            
            if jobs:
                print("   Top 3 results:")
                for i, job in enumerate(jobs[:3], 1):
                    print(f"   {i}. {job.get('title', 'No title')} @ {job.get('company', 'No company')}")
        else:
            print("❌ No jobs.json created")
            
    except Exception as e:
        print(f"❌ Job search test failed: {e}")

def main():
    print("🐛 AutoApplyAI Job Finding Debugger")
    print("=" * 50)
    
    check_files()
    test_wwr_rss()
    test_remoteok_api()
    analyze_user_profile()
    run_job_search_test()
    
    print("\n" + "=" * 50)
    print("🏁 Debug analysis complete!")
    print("\nRecommendations:")
    print("1. Ensure all config files exist and have valid JSON")
    print("2. Check your internet connection for API access")
    print("3. Update your user profile with relevant skills")
    print("4. Run the fixed find_jobs.py script")

if __name__ == "__main__":
    main()
