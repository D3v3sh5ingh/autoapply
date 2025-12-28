from typing import List, Optional
from datetime import datetime
import requests
from .base import BaseScraper
from ..database.models import Job
from ..utils.logger import setup_logger

class InstahyreScraper(BaseScraper):
    """
    Scraper for Instahyre using internal API.
    """
    BASE_URL = "https://www.instahyre.com"
    API_URL = "https://www.instahyre.com/api/v1/job_search"

    def __init__(self):
        super().__init__(self.BASE_URL)
        self.logger = setup_logger("InstahyreScraper")

    def scrape(self, query: str = "python", location: str = "Bangalore", limit: int = 10) -> List[Job]:
        params = {
            "skills": query,
            "location": location,
            "count": limit + 5 # Fetch a bit more to filter
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.instahyre.com/jobs/"
        }

        self.logger.info(f"Scraping Instahyre API for query='{query}' in '{location}'...")
        jobs = []
        try:
            response = requests.get(self.API_URL, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # DEBUG: Print raw response summary
                print(f"DEBUG: Instahyre API Response Keys: {list(data.keys())}")
                if 'objects' in data:
                    print(f"DEBUG: Instahyre 'objects' count: {len(data['objects'])}")
                
                if 'objects' in data:
                    for obj in data['objects']:
                        try:
                            # DEBUG: Explicit type check
                            print(f"DEBUG: Processing obj of type {type(obj)}")
                            if not isinstance(obj, dict):
                                print(f"DEBUG: Skipping invalid object type: {type(obj)}")
                                continue
                                
                            title = obj.get('title', 'Unknown Role')
                            # Company Name Logic
                            company = obj.get('company_name')
                            if not company and isinstance(obj.get('company'), dict):
                                company = obj['company'].get('name')
                            
                            # Fallback if still unknown
                            if not company:
                                # Sometimes it's in a different structure
                                company = "Confidential (Instahyre)" 


                            # Location Logic (Fixing H,y,d,e,r,a,b,a,d issue)
                            locs = obj.get('locations', [])
                            parsed_locs = []
                            
                            if isinstance(locs, list):
                                for l in locs:
                                    if isinstance(l, dict):
                                        parsed_locs.append(l.get('city', ''))
                                    elif isinstance(l, str):
                                        parsed_locs.append(l)
                            elif isinstance(locs, str):
                                parsed_locs.append(locs)
                                
                            location_text = ", ".join(filter(None, parsed_locs)) if parsed_locs else location

                            # URL Logic
                            slug = obj.get('job_slug', '')
                            url = f"{self.BASE_URL}/job-{obj.get('id')}-{slug}" if obj.get('id') else self.BASE_URL

                            description = f"Skills: {', '.join(obj.get('skills', []))}"
                            
                            job = Job(
                                title=title,
                                company=company,
                                location=location_text,
                                description=description,
                                url=url,
                                source="instahyre",
                                date_posted=datetime.utcnow()
                            )
                            jobs.append(job)
                            if len(jobs) >= limit:
                                break
                        except Exception as e:
                            self.logger.error(f"Error parsing Instahyre job: {e}")
                            continue
                self.logger.info(f"Instahyre found {len(jobs)} jobs.")
            else:
                self.logger.error(f"Instahyre API failed with {resp.status_code}")
        except Exception as e:
            self.logger.error(f"Instahyre scrape connection error: {e}")
            print(f"CRITICAL INSTAHYRE ERROR: {e}") # This will show in the terminal
            
        return jobs

    def parse_job_page(self, url: str) -> Optional[Job]:
        pass
