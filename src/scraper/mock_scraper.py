from typing import List, Optional
from datetime import datetime, timedelta
from .base import BaseScraper
from ..database.models import Job

class MockScraper(BaseScraper):
    """
    Mock Scraper that returns hardcoded jobs for testing and demo purposes.
    """
    def __init__(self):
        super().__init__("mock://")

    def scrape(self, query: str = "", location: str = "", limit: int = 10) -> List[Job]:
        print(f"MockScraper: Generating jobs for query='{query}'...")
        
        base_jobs = [
            Job(title="Senior Python Developer", company="TechCorp", location="Remote", 
                description="Expert in Python, Django, and Cloud. Salary: $120k", 
                url="https://example.com/job1", source="mock", 
                date_posted=datetime.utcnow()),
            Job(title="Frontend Engineer (React)", company="WebSols", location="New York", 
                description="Looking for React.js rockstar. Experience with Redux.", 
                url="https://example.com/job2", source="mock", 
                date_posted=datetime.utcnow() - timedelta(days=1)),
            Job(title="Data Scientist", company="DataAI", location="San Francisco", 
                description="Machine Learning, Python, PyTorch, and SQL skills required.", 
                url="https://example.com/job3", source="mock", 
                date_posted=datetime.utcnow() - timedelta(hours=5)),
            Job(title="Backend Engineer", company="StartupX", location="Bangalore", 
                description="Node.js or Python backend role. Fast paced environment.", 
                url="https://example.com/job4", source="mock", 
                date_posted=datetime.utcnow() - timedelta(days=2)),
            Job(title="Senior Data Engineer", company="FinTech Global", location="Pune", 
                description="Looking for PySpark, AWS, and Snowflake expert. Migration projects.", 
                url="https://example.com/job5", source="mock", 
                date_posted=datetime.utcnow() - timedelta(hours=2)),
            Job(title="Lead Data Engineer", company="BigData Corp", location="Remote", 
                description="Experience with Airflow, Kafka, and Big Data pipelines required.", 
                url="https://example.com/job6", source="mock", 
                date_posted=datetime.utcnow() - timedelta(days=3)),
        ]
        
        # Simple client-side filter
        filtered = []
        for job in base_jobs:
            # Relaxed matching: verify if ANY word from query matches
            q_tokens = query.lower().split()
            title_lower = job.title.lower()
            desc_lower = job.description.lower()
            
            # Match if ANY token is in title or description (very permissive)
            match_query = False
            if not query:
                match_query = True
            else:
                for token in q_tokens:
                    if token in title_lower or token in desc_lower:
                        match_query = True
                        break
            
            # Relaxed Location: Match if location is empty OR if matches
            match_loc = False
            if not location:
                match_loc = True
            elif job.location and location.lower() in job.location.lower():
                match_loc = True
            elif job.location == "Remote": # Always show remote
                match_loc = True
                
            if match_query and match_loc:
                filtered.append(job)
        
        print(f"MockScraper: Returning {len(filtered)} jobs after filter.")
        return filtered[:limit]

    def parse_job_page(self, url: str) -> Optional[Job]:
        return None
