import yaml
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import streamlit as st

# Load config and job data
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

with open('jobs.json', 'r') as f:
    jobs = json.load(f)

# Define a function to extract skills from job descriptions
def extract_skills(job_description):
    # Tokenize the job description and remove stopwords
    tokens = word_tokenize(job_description.lower())
    tokens = [t for t in tokens if t not in stopwords.words('english')]
    # Extract skills (e.g., using a predefined list of skills)
    skills = [t for t in tokens if t in config['skills']]
    return skills

# Define a function to calculate similarity between job skills and applicant skills
def calculate_similarity(job_skills, applicant_skills):
    # Use cosine similarity or Jaccard similarity
    vectorizer = CountVectorizer()
    job_skills_vector = vectorizer.fit_transform([' '.join(job_skills)])
    applicant_skills_vector = vectorizer.transform([' '.join(applicant_skills)])
    similarity = cosine_similarity(job_skills_vector, applicant_skills_vector)
    return similarity[0][0]

# Define a function to generate a cover letter
def generate_cover_letter(job_title, company, matching_skills):
    # Use a template engine to generate the cover letter
    template = jinja2.Template('cover_letter_template.html')
    cover_letter = template.render(job_title=job_title, company=company, matching_skills=matching_skills)
    return cover_letter

# Streamlit app
st.title('Job Application Automator')

# Get user input (e.g., job search query)
job_search_query = st.text_input('Job Search Query')

# Filter jobs based on similarity score
filtered_jobs = []
for job in jobs:
    job_skills = extract_skills(job['description'])
    similarity = calculate_similarity(job_skills, config['skills'])
    if similarity >= 0.75:
        filtered_jobs.append(job)

# Generate cover letters and apply to jobs
for job in filtered_jobs:
    matching_skills = [skill for skill in job['skills'] if skill in config['skills']]
    cover_letter = generate_cover_letter(job['title'], job['company'], matching_skills)
    # Apply to job using the script's existing logic
