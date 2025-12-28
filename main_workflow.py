from src.scraper.hn_scraper import HNScraper
from src.matcher.simple_matcher import KeywordMatcher
from src.notification.email_service import EmailService
from src.database.models import Job, Profile, Application
from src.database.db import get_db, init_db
from sqlalchemy.orm import Session
import datetime

def run_workflow():
    print("Starting AutoApply Workflow...")
    
    # 1. Setup Mock Profile
    profile = Profile(
        name="Devesh Singh",
        email="d3v3sh.singh@gmail.com",
        skills=["Python", "SQL", "PySpark", "Snowflake", "AWS", "Airflow", "Data Engineer"]
    )
    
    # 2. Scrape (Fastest one for demo)
    print("Scraping Jobs...")
    scraper = HNScraper()
    jobs = scraper.scrape(limit=100) # Get a few
    print(f"Scraped {len(jobs)} jobs.")

    # 3. Match
    print("Matching Jobs...")
    matcher = KeywordMatcher()
    matched_jobs = []
    
    for job in jobs:
        score, details = matcher.match(job, profile)
        job.match_score = score
        job.keywords_matched = details.get('matched_keywords')
        
        # Filter only good matches for notification (e.g. > 0 for demo, usually > 50)
        if score > 0:
            matched_jobs.append(job)

    matched_jobs.sort(key=lambda x: x.match_score, reverse=True)
    print(f"Found {len(matched_jobs)} matches.")

    # 4. Notify
    print("Sending Notification...")
    notifier = EmailService() # Will use Mock mode
    notifier.send_matches_alert(profile.email, matched_jobs)
    
    print("Workflow Complete.")

if __name__ == "__main__":
    run_workflow()
