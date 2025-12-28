import time
import random
from typing import List, Optional
from bs4 import BeautifulSoup
from .base import BaseScraper
from ..database.models import Job
from datetime import datetime
from ..utils.logger import setup_logger

# Try importing selenium
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
        self.logger = setup_logger("LinkedInScraper")

    def _setup_driver(self):
        from src.utils.driver import get_driver
        self.driver = get_driver(self.headless)

    def scrape(self, query: str = "software engineer", location: str = "India", limit: int = 10) -> List[Job]:
        if not self.driver:
            self._setup_driver()

        # Construct URL
        search_url = f"{self.BASE_URL}?keywords={query}&location={location}&f_TPR=r604800" # Last week filter helps relevance
        
        self.logger.info(f"Navigating to: {search_url}")
        self.driver.get(search_url)
        
        # Human-like delay
        delay = random.uniform(3, 6)
        self.logger.info(f"Waiting for {delay:.2f}s...")
        time.sleep(delay)
        
        jobs = []
        try:
            # Scroll a bit to trigger lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            time.sleep(2)
            
            # This selector is subject to change by LinkedIn
            # Try multiple selector strategies
            selectors = ["div.base-card", "li.jobs-search-results__list-item", "div.job-search-card"]
            job_cards = []
            for sel in selectors:
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if job_cards:
                    self.logger.info(f"Found {len(job_cards)} job cards using selector: {sel}")
                    break
            
            if not job_cards:
                self.logger.warning("No job cards found using standard selectors. Taking debug screenshot.")
                self.driver.save_screenshot("linkedin_debug.png")
            
            for card in job_cards[:limit]:
                try:
                    # Extract basic info from card
                    # Note: Selectors might need adjustment based on the card type found
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title")
                        company_elem = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle")
                        loc_elem = card.find_element(By.CSS_SELECTOR, "span.job-search-card__location")
                        link_elem = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
                    except:
                        # Fallback for different card layout
                        title_elem = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__title") 
                        company_elem = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle")
                        loc_elem = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__caption")
                        link_elem = card.find_element(By.CSS_SELECTOR, "a")

                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    location_text = loc_elem.text.strip()
                    url = link_elem.get_attribute("href")
                    
                    self.logger.info(f"Found Job: {title} at {company}")

                    # Create job object
                    title_text = title_elem.text.strip()
                    company_text = company_elem.text.strip()
                    
                    # Filter out empty or obfuscated data
                    if not title_text or not company_text:
                        continue
                    
                    # Skip obfuscated results (common in scraping without login)
                    if "*" in company_text or "*" in title_text or "LinkedIn Member" in company_text:
                        self.logger.warning(f"Skipping obfuscated job: {title_text} @ {company_text}")
                        continue
                        
                    job = Job(
                        title=title_text,
                        company=company_text,
                        location=location_text,
                        url=url,
                        source="linkedin",
                        date_posted=datetime.utcnow() 
                    )
                    jobs.append(job)
                except Exception as e:
                    # Skip incomplete cards
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping LinkedIn list: {e}")
            self.driver.save_screenshot("linkedin_error.png")
            
        return jobs

    def parse_job_page(self, url: str) -> Optional[Job]:
        # Detailed parsing can be added later
        pass

    def close(self):
        if self.driver:
            self.driver.quit()
