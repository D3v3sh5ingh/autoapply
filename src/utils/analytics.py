import re
from collections import Counter
from ..database.models import Job

# Common stopwords to ignore in job descriptions
STOPWORDS = set([
    "the", "and", "to", "of", "a", "in", "for", "is", "on", "with", "as", "be", "at", 
    "an", "or", "by", "we", "are", "you", "that", "it", "from", "will", "can", "this",
    "experience", "team", "work", "skills", "knowledge", "years", "development",
    "design", "business", "data", "software", "applications", "using", "application",
    "working", "role", "requirements", "support", "technical", "solutions", "environment",
    "strong", "engineering", "systems", "project", "degree", "computer", "science",
    "ability", "must", "have", "preferred", "understanding", "good", "excellent",
    "communication", "job", "position", "description", "responsibilities", "qualifications",
    "looking", "candidate", "remote", "company", "location", "full", "time"
])

def extract_keywords(text):
    if not text: return []
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    words = text.lower().split()
    return [w for w in words if w not in STOPWORDS and len(w) > 2]

def analyze_skill_gaps(jobs, user_skills):
    """
    Analyzes job descriptions to find common keywords missing from user skills.
    Returns: List of (keyword, count) tuples.
    """
    if not jobs: return []

    user_skills_set = set(s.lower().strip() for s in user_skills)
    corpus = []
    for job in jobs:
        corpus.extend(extract_keywords(job.description))
            
    counts = Counter(corpus)
    gaps = []
    for word, count in counts.most_common(50):
        if word not in user_skills_set:
            gaps.append((word, count))
    return gaps[:10]

def get_top_companies(jobs):
    companies = [j.company for j in jobs if j.company and "unknown" not in j.company.lower()]
    return Counter(companies).most_common(10)

def get_market_skills(jobs):
    """Returns the most frequent keywords across ALL jobs (Market Demand)."""
    corpus = []
    for job in jobs:
        corpus.extend(extract_keywords(job.description))
    return Counter(corpus).most_common(10)
