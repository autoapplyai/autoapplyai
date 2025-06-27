#!/usr/bin/env python3
import os, json, requests
from bs4 import BeautifulSoup

# Disable any CI proxy env vars
for var in ("HTTP_PROXY","HTTPS_PROXY","http_proxy","https_proxy"):
    os.environ.pop(var, None)

HEADERS = {"User-Agent": "Mozilla/5.0"}
session = requests.Session()
session.trust_env = False

def scrape_wwr():
    url = "https://weworkremotely.com/"
    r = session.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    jobs = []
    for li in soup.select("section.jobs li.featured, section.jobs li:not(.view-all)"):
        a = li.find("a", href=True)
        if a:
            jobs.append({"url": "https://weworkremotely.com" + a["href"]})
    return jobs

def scrape_indeed():
    url = "https://www.indeed.com/q-Remote-jobs.html"
    r = session.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    jobs = []
    for a in soup.select("a.tapItem[href*='/rc/clk?jk=']"):
        jobs.append({"url": "https://www.indeed.com" + a["href"]})
    return jobs

def scrape_working_nomads():
    url = "https://www.workingnomads.com/jobs"
    r = session.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    jobs = []
    for a in soup.select("a.job-link"):
        href = a["href"]
        full = href if href.startswith("http") else "https://www.workingnomads.com" + href
        jobs.append({"url": full})
    return jobs

def main():
    all_jobs = []
    try:
        print("🔍 Scraping We Work Remotely…")
        all_jobs += scrape_wwr()
    except Exception as e:
        print(f"⚠️  WWR failed: {e}")
    try:
        print("🔍 Scraping Indeed Remote…")
        all_jobs += scrape_indeed()
    except Exception as e:
        print(f"⚠️  Indeed failed: {e}")
    try:
        print("🔍 Scraping Working Nomads…")
        all_jobs += scrape_working_nomads()
    except Exception as e:
        print(f"⚠️  WorkingNomads failed: {e}")

    # dedupe
    seen, unique = set(), []
    for j in all_jobs:
        if j["url"] not in seen:
            seen.add(j["url"])
            unique.append(j)

    with open("jobs.json", "w") as f:
        json.dump(unique, f, indent=2)
    print(f"✅ Wrote {len(unique)} jobs to jobs.json")

if __name__ == "__main__":
    main()
