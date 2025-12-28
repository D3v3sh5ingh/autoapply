import requests
from datetime import datetime
from typing import List, Optional
from .base import BaseScraper
from ..database.models import Job

class HNScraper(BaseScraper):
    """
    Scraper for Hacker News "Who is hiring" or Job stories.
    For this v1, we'll use the official HN API to get job stories.
    """
    BASE_API_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        super().__init__(self.BASE_API_URL)

    def scrape(self, query: str = "", location: str = "", limit: int = 10) -> List[Job]:
        # Get job stories IDs
        try:
            resp = requests.get(f"{self.BASE_API_URL}/jobstories.json")
            resp.raise_for_status()
            job_ids = resp.json()[:limit]  # Respect limit
            
            jobs = []
            for jid in job_ids:
                job_data = self._fetch_item(jid)
                if job_data:
                    job = self.parse_job_page(job_data)
                    if job:
                        # Basic filtering if query/location provided (client-side since API is limited)
                        if query.lower() in job.title.lower() or query.lower() in (job.description or "").lower():
                            if not location or (job.location and location.lower() in job.location.lower()):
                                jobs.append(job)
                            elif not location:
                                jobs.append(job)
            return jobs
        except Exception as e:
            print(f"Error scraping HN: {e}")
            return []

    def _fetch_item(self, item_id: int) -> Optional[dict]:
        try:
            resp = requests.get(f"{self.BASE_API_URL}/item/{item_id}.json")
            if resp.status_code == 200:
                return resp.json()
        except:
            pass
        return None

    def parse_job_page(self, data: dict) -> Optional[Job]:
        """
        Parses the JSON data from HN API into a Job object.
        """
        if notData := data:
            return None
        
        # HN jobs often have title like "Company | Role | Location" or similar
        title_raw = data.get('title', 'Unknown Job')
        url = data.get('url', f"https://news.ycombinator.com/item?id={data.get('id')}")
        description = data.get('text', '')  # specific to HN items, often empty for external links
        
        # Simple heuristic to extract company/location from title if possible
        # This is very basic; a real parser would be more robust
        parts = title_raw.split('|')
        if len(parts) >= 2:
            company = parts[0].strip()
            title = parts[1].strip()
            location = parts[2].strip() if len(parts) > 2 else None
        else:
            company = "Hacker News (Unknown Company)"
            title = title_raw
            location = None

        date_posted = datetime.fromtimestamp(data.get('time', 0))

        return Job(
            title=title,
            company=company,
            location=location,
            description=description,
            url=url,
            date_posted=date_posted,
            source="hacker_news"
        )
