#!/usr/bin/env python3
import json
import feedparser

def scrape_wwr_rss():
    url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
    feed = feedparser.parse(url)
    jobs = []
    for entry in feed.entries:
        jobs.append({
            "title": entry.title,
            "url": entry.link,
            "published": entry.published if 'published' in entry else ''
        })
    return jobs

def main():
    all_jobs = []
    try:
        print("🔍 Scraping We Work Remotely RSS…")
        all_jobs += scrape_wwr_rss()
    except Exception as e:
        print(f"⚠️  WWR RSS failed: {e}")

    # dedupe by URL
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
