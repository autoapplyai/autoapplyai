import re

# List of red-flag keywords that often appear in scam listings
SCAM_KEYWORDS = [
    "quick money", "no experience needed", "whatsapp", "telegram",
    "processing fee", "startup fee", "bitcoin", "wire transfer", "gift card",
    "send your bank info", "no resume", "daily payout", "earn from home"
]

# List of sketchy domain extensions or patterns
SUSPECT_DOMAINS = [".xyz", ".top", ".click", ".gq", ".tk", ".ml"]

def is_scam(job_description, company_url=None):
    text = job_description.lower()

    for keyword in SCAM_KEYWORDS:
        if keyword in text:
            return True

    if company_url:
        for ext in SUSPECT_DOMAINS:
            if company_url.endswith(ext):
                return True

    # Check for shady redirect links
    if re.search(r"(bit\.ly|tinyurl\.com|rb\.gy|rebrand\.ly|shorturl\.at)", text):
        return True

    return False
