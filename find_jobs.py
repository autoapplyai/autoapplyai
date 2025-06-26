#!/usr/bin/env python3
import requests, yaml, json

# load your skills & threshold
cfg = yaml.safe_load(open("config.yaml"))
skills = set(cfg["skills"])
threshold = cfg["threshold"]

# fetch RemoteOK’s public API
resp = requests.get("https://remoteok.com/api").json()[1:]  # skip metadata
jobs = []

for j in resp:
    tags = {t.lower() for t in j.get("tags", [])}
    # simple match: overlap / total skills
    match_score = len(skills & tags) / len(skills)
    if j.get("remote") and match_score >= threshold:
        jobs.append({
            "company":       j.get("company"),
            "title":         j.get("position"),
            "apply_url":     j.get("url"),
            "site":          "remoteok",
            "score":         match_score
        })

# write out a base jobs.json
with open("jobs.json", "w") as f:
    json.dump(jobs, f, indent=2)

print(f"Found {len(jobs)} jobs ≥ {threshold*100:.0f}% match")
