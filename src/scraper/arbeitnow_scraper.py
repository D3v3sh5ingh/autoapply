import requests
from typing import List, Optional
from datetime import datetime
from .base import BaseScraper
from ..database.models import Job
from ..utils.logger import setup_logger

class ArbeitnowScraper(BaseScraper):
    """
    Scraper for Arbeitnow API (Remote-focused, structured data).
    API Docs: https://arbeitnow.com/api/job-board-api
    """
    API_URL = "https://arbeitnow.com/api/job-board-api"

    def __init__(self):
        super().__init__(self.API_URL)
        self.logger = setup_logger("ArbeitnowScraper")

    def scrape(self, query: str = "", location: str = "", limit: int = 10) -> List[Job]:
        """
        Fetches jobs from Arbeitnow. 
        Note: The API doesn't support server-side filtering by query/location well, 
        so we fetch the latest batch and filter client-side.
        """
        self.logger.info(f"Fetching from Arbeitnow API...")
        jobs = []
        try:
            response = requests.get(self.API_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                raw_jobs = data.get("data", [])
                self.logger.info(f"Arbeitnow returned {len(raw_jobs)} raw jobs. Filtering for '{query}'...")
                
                for item in raw_jobs:
                    try:
                        title = item.get("title", "")
                        company = item.get("company_name", "")
                        desc = item.get("description", "") # HTML content
                        tags = item.get("tags", [])
                        is_remote = item.get("remote", False)
                        location_api = item.get("location", "Unknown")
                        url = item.get("url", "")
                        
                        # Basic Client-Side Filter
                        # If query is provided, check title/tags
                        text_corpus = (title + " " + " ".join(tags)).lower()
                        if query and query.lower() not in text_corpus:
                            continue
                            
                        # If location is provided (and not just "Remote"), try to filter
                        # Arbeitnow is mostly remote, so we'll be lenient with location
                        if location and location.lower() not in location_api.lower() and not is_remote:
                             # If user asked for specific city and job is NOT remote and NOT in that city
                             pass 

                        job = Job(
                            title=title,
                            company=company,
                            location=f"{location_api} {'(Remote)' if is_remote else ''}",
                            description=f"Tags: {', '.join(tags)}", # Keep description short for card view
                            url=url,
                            source="arbeitnow",
                            date_posted=datetime.utcnow() # API doesn't provide easy date, assume fresh
                        )
                        jobs.append(job)
                        
                        if len(jobs) >= limit:
                            break
                    except Exception as e:
                        continue
                        
                self.logger.info(f"Arbeitnow found {len(jobs)} matches.")
            else:
                self.logger.error(f"Arbeitnow API failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Arbeitnow Connection Error: {e}")
            
        return jobs

    def parse_job_page(self, url: str) -> Optional[Job]:
        pass
