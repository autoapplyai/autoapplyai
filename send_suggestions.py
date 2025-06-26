import json
import os
import csv
import smtplib
from email.mime.text import MIMEText
from match_jobs import get_job_matches
from datetime import datetime, timezone

# ——— Brevo SMTP Credentials ———————————————————————————
SENDER = "autoapplyai22@gmail.com"
PASSWORD = "kVG0Sq4FbRXYgZtN"
RECEIVER = SENDER  # Change if needed

print("📨 Sending via Brevo as:", SENDER)

# ——— Fetch job matches ————————————————————————————————
jobs = get_job_matches("config/user_profile.json", max_results=3)

# ——— Build email body ————————————————————————————————
if jobs:
    lines = ["Your Daily AutoapplyAI Job Suggestions", ""]
    for job in jobs:
        lines.append(f"• {job['title']} @ {job['company']}")
        lines.append(f"    → {job['url']}")
        lines.append("")
    body_text = "\n".join(lines)
else:
    body_text = "No matches found today. Check your profile or try again later."

# ——— Log suggestions to CSV ————————————————————————————
log_path = "sent_jobs_log.csv"
new_file = not os.path.exists(log_path)

with open(log_path, "a", newline="", encoding="utf-8") as csvf:
    writer = csv.writer(csvf)
    if new_file:
        writer.writerow(["timestamp", "title", "company", "url"])
    ts = datetime.now(timezone.utc).isoformat()
    for job in jobs:
        writer.writerow([ts, job["title"], job["company"], job["url"]])

# ——— Compose and send email using Brevo SMTP ——————————————
msg = MIMEText(body_text)
msg["From"] = SENDER
msg["To"] = RECEIVER
msg["Subject"] = "AutoapplyAI Daily Jobs"

try:
    with smtplib.SMTP("smtp-relay.brevo.com", 587) as server:
        server.starttls()
        server.login(SENDER, PASSWORD)
        server.send_message(msg)
    print("✅ Sent via Brevo successfully!")
except Exception as e:
    print("❌ Failed to send with Brevo:", e)

