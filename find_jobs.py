#!/usr/bin/env python3
import requests, yaml, json, os
from requests.exceptions import ProxyError

# remove any HTTP_PROXY/HTTPS_PROXY so we try direct first
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)

cfg       = yaml.safe_load(open("config.yaml"))
skills    = set(cfg["skills"])
threshold = cfg["threshold"]

def fetch_remoteok():
    try:
        data = requests.get("https://remoteok.com/api", timeout=20).json()[1:]
        return data
    except ProxyError:
        print("⚠️  Proxy blocked. Skipping live fetch. Use CI or run locally.")
        return []

resp = fetch_remoteok()
jobs = []
for j in resp:
    tags = {t.lower() for t in j.get("tags", [])}
    score = len(skills & tags) / len(skills)
    if j.get("remote") and score >= threshold:
        jobs.append({
            "company":   j["company"],
            "title":     j["position"],
            "apply_url": j["url"],
            "score":     score
        })

# if we got no live jobs, fall back to your existing jobs.json
if not jobs:
    print("ℹ️  No live jobs found; falling back to previous jobs.json")
    jobs = json.load(open("jobs.json"))

with open("jobs.json", "w") as f:
    json.dump(jobs, f, indent=2)

print(f"🏁  Final job list: {len(jobs)} entries")
