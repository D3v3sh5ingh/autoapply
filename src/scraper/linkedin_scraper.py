import time
from typing import List, Optional
from bs4 import BeautifulSoup
from .base import BaseScraper
from ..database.models import Job
from datetime import datetime

# Try importing selenium, handle if not installed yet (though we are installing it)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

class LinkedInScraper(BaseScraper):
    """
    Scraper for LinkedIn Jobs. 
    Uses Selenium to handle dynamic rendering and potential auth walls.
    """
    BASE_URL = "https://www.linkedin.com/jobs/search"

    def __init__(self, headless: bool = True):
        super().__init__(self.BASE_URL)
        self.headless = headless
        self.driver = None

    def _setup_driver(self):
        if not HAS_SELENIUM:
            raise ImportError("Selenium is required for LinkedIn scraping. Please install it with `pip install selenium webdriver_manager`.")
        
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def scrape(self, query: str = "software engineer", location: str = "India", limit: int = 10) -> List[Job]:
        if not self.driver:
            self._setup_driver()

        # Construct URL
        # LinkedIn public search URL structure
        search_url = f"{self.BASE_URL}?keywords={query}&location={location}"
        
        print(f"Scraping LinkedIn: {search_url}")
        self.driver.get(search_url)
        
        # Scroll to load more jobs if needed (basic version just takes initial load)
        time.sleep(3) # Wait for page structure
        
        jobs = []
        try:
            # This selector is subject to change by LinkedIn
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.base-card")
            
            for card in job_cards[:limit]:
                try:
                    # Extract basic info from card
                    title_elem = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title")
                    company_elem = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle")
                    loc_elem = card.find_element(By.CSS_SELECTOR, "span.job-search-card__location")
                    link_elem = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
                    
                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    location_text = loc_elem.text.strip()
                    url = link_elem.get_attribute("href")
                    
                    # Create job object
                    job = Job(
                        title=title,
                        company=company,
                        location=location_text,
                        url=url,
                        source="linkedin",
                        date_posted=datetime.utcnow() # Approximate, real date parsing is complex
                    )
                    jobs.append(job)
                except Exception as e:
                    # Skip incomplete cards
                    continue
                    
        except Exception as e:
            print(f"Error scraping LinkedIn list: {e}")
            
        return jobs

    def parse_job_page(self, url: str) -> Optional[Job]:
        # Detailed parsing can be added later
        pass

    def close(self):
        if self.driver:
            self.driver.quit()
