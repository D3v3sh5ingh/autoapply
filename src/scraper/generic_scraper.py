from typing import List, Optional
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
from .base import BaseScraper
from ..database.models import Job
from ..utils.logger import setup_logger

class GenericScraper(BaseScraper):
    """
    A generic scraper that targets common ATS platforms like Greenhouse and Lever.
    User provides a COMPANY url like "https://boards.greenhouse.io/airbnb".
    """
    def __init__(self):
        super().__init__("generic")
        self.logger = setup_logger("GenericScraper")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def scrape(self, query: str = "", location: str = "", limit: int = 10) -> List[Job]:
        # query is treated as the URL in this scraper mode for simplicity
        # User enters "https://boards.greenhouse.io/..." in the query box
        
        target_url = query
        if not target_url.startswith("http"):
            # Not a URL, return empty
            return []

        self.logger.info(f"Generic scraping URL: {target_url}")
        
        try:
            resp = requests.get(target_url, headers=self.headers)
            if resp.status_code != 200:
                self.logger.error(f"Failed to fetch {target_url}: {resp.status_code}")
                return []
                
            soup = BeautifulSoup(resp.text, 'html.parser')
            jobs = []

            # Detect platform
            if "greenhouse.io" in target_url:
                jobs = self._scrape_greenhouse(soup, limit)
            elif "lever.co" in target_url:
                jobs = self._scrape_lever(soup, limit)
            else:
                self.logger.warning("Unknown platform. Trying heuristics.")
                # Heuristic fallback could go here
                pass
                
            return jobs

        except Exception as e:
            self.logger.error(f"Generic scrape error: {e}")
            return []

    def _scrape_greenhouse(self, soup, limit):
        jobs = []
        # Greenhouse usually has <div class="opening"> <a href="...">Title</a> <span class="location">...</span> </div>
        openings = soup.find_all('div', class_='opening')
        
        for op in openings[:limit]:
            try:
                link = op.find('a')
                if not link: continue
                
                title = link.text.strip()
                url = "https://boards.greenhouse.io" + link['href'] if link['href'].startswith('/') else link['href']
                
                loc_span = op.find('span', class_='location')
                location = loc_span.text.strip() if loc_span else "Unknown"
                
                jobs.append(Job(
                    title=title,
                    company="Company (Greenhouse)", # Hard to find company name easily without more parsing
                    location=location,
                    url=url,
                    source="greenhouse",
                    date_posted=datetime.utcnow()
                ))
            except: 
                continue
        return jobs

    def _scrape_lever(self, soup, limit):
        jobs = []
        # Lever usually has <a class="posting-title"> <h5>Title</h5> </a>
        postings = soup.find_all('div', class_='posting')
        
        for post in postings[:limit]:
            try:
                link = post.find('a', class_='posting-title')
                if not link: continue
                
                title = link.find('h5').text.strip()
                url = link['href']
                
                # Location is confusing in Lever sometimes, often in a span
                labels = post.find('div', class_='posting-categories')
                location = labels.text.strip() if labels else "Unknown"
                
                jobs.append(Job(
                    title=title,
                    company="Company (Lever)",
                    location=location,
                    url=url,
                    source="lever",
                    date_posted=datetime.utcnow()
                ))
            except:
                continue
        return jobs

    def parse_job_page(self, url: str) -> Optional[Job]:
        pass
