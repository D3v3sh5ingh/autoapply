from typing import List, Optional
import time
import random
from datetime import datetime
from .base import BaseScraper
from ..database.models import Job
from ..utils.logger import setup_logger

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

class NaukriScraper(BaseScraper):
    """
    Scraper for Naukri.com Jobs.
    Uses Selenium as Naukri is heavily dynamic.
    """
    BASE_URL = "https://www.naukri.com"

    def __init__(self, headless: bool = True):
        super().__init__(self.BASE_URL)
        self.headless = headless
        self.driver = None
        self.logger = setup_logger("NaukriScraper")

    def _setup_driver(self):
        from src.utils.driver import get_driver
        self.driver = get_driver(self.headless)

    def scrape(self, query: str = "python developer", location: str = "Bangalore", limit: int = 10) -> List[Job]:
        if not self.driver:
            self._setup_driver()

        # Naukri URL format: https://www.naukri.com/python-developer-jobs-in-bangalore or search params
        # Using search parameter style is more reliable across changes
        # https://www.naukri.com/k-python-l-pune
        
        q_clean = query.replace(' ', '-')
        l_clean = location.replace(' ', '-')
        search_url = f"{self.BASE_URL}/{q_clean}-jobs-in-{l_clean}"
        
        self.logger.info(f"Navigating to: {search_url}")
        self.driver.get(search_url)
        
        delay = random.uniform(5, 8)
        self.logger.info(f"Waiting {delay:.2f}s for page load...")
        time.sleep(delay)
        
        jobs = []
        try:
            # Selectors for job tuples
            # Naukri changes classes often. Using partial class or structure is safer.
            # .srp-jobtuple-wrapper is a common container
            job_tuples = self.driver.find_elements(By.CSS_SELECTOR, ".srp-jobtuple-wrapper")
            
            if not job_tuples:
                self.logger.warning("No job tuples found. Checking for 'cust-job-tuple'...")
                job_tuples = self.driver.find_elements(By.CSS_SELECTOR, "div.cust-job-tuple")
            
            if not job_tuples:
                self.logger.warning("Still no jobs. Taking debug screenshot: naukri_debug.png")
                self.driver.save_screenshot("naukri_debug.png")

            self.logger.info(f"Found {len(job_tuples)} potential job cards.")

            for tuple_node in job_tuples[:limit]:
                try:
                    title_elem = tuple_node.find_element(By.CSS_SELECTOR, "a.title")
                    try:
                        company_elem = tuple_node.find_element(By.CSS_SELECTOR, "a.comp-name")
                    except:
                        # Sometimes company name is not a link
                        company_elem = tuple_node.find_element(By.CSS_SELECTOR, "div.comp-name")
                    
                    # Location structure varies
                    try:
                        loc_elem = tuple_node.find_element(By.CSS_SELECTOR, "span.locWdth")
                        location_text = loc_elem.text.strip()
                    except:
                        location_text = "Unknown"

                    # Try to get description snippet
                    desc_text = "No description available."
                    try:
                        # Naukri often has a job-desc or snippet class
                        desc_elem = tuple_node.find_element(By.CSS_SELECTOR, "div.job-desc")
                        desc_text = desc_elem.text.strip()
                    except:
                        try:
                            # Fallback: keyskills match
                            keyskills = tuple_node.find_elements(By.CSS_SELECTOR, "li.dot") # tags
                            if not keyskills: keyskills = tuple_node.find_elements(By.CSS_SELECTOR, ".tags span")
                            if keyskills:
                                desc_text = "Skills: " + ", ".join([k.text for k in keyskills])
                        except: pass
                    
                    # If still empty, use Title + Company to ensure at least some match possibility
                    if desc_text == "No description available.":
                         desc_text = f"{title} role at {company} in {location_text}"

                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    url = title_elem.get_attribute("href")
                    
                    self.logger.info(f"Found Job: {title} at {company}")
                    
                    job = Job(
                        title=title,
                        company=company,
                        location=location_text,
                        url=url,
                        source="naukri",
                        date_posted=datetime.utcnow()
                    )
                    jobs.append(job)
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping Naukri: {e}")
            self.driver.save_screenshot("naukri_error.png")
            
        return jobs

    def parse_job_page(self, url: str) -> Optional[Job]:
        pass
        
    def close(self):
        if self.driver:
            self.driver.quit()
