from typing import List, Optional
import time
from datetime import datetime
from .base import BaseScraper
from ..database.models import Job

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

    def _setup_driver(self):
        if not HAS_SELENIUM:
            raise ImportError("Selenium is required.")
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        # Important for Naukri to not block immediately
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def scrape(self, query: str = "python developer", location: str = "Bangalore", limit: int = 10) -> List[Job]:
        if not self.driver:
            self._setup_driver()

        # Naukri URL format: https://www.naukri.com/python-developer-jobs-in-bangalore
        # We need to format the query and location to match their slug pattern or use search param
        # Using search param is safer: https://www.naukri.com/k-python-developer-l-bangalore
        
        q_slug = f"k-{query.replace(' ', '-')}"
        l_slug = f"l-{location.replace(' ', '-')}"
        search_url = f"{self.BASE_URL}/{q_slug}-{l_slug}"
        
        print(f"Scraping Naukri: {search_url}")
        self.driver.get(search_url)
        time.sleep(5) # Wait for their heavy JS
        
        jobs = []
        try:
            # Selectors for job tuples
            job_tuples = self.driver.find_elements(By.CSS_SELECTOR, ".srp-jobtuple-wrapper")
            
            for tuple_node in job_tuples[:limit]:
                try:
                    title_elem = tuple_node.find_element(By.CSS_SELECTOR, "a.title")
                    company_elem = tuple_node.find_element(By.CSS_SELECTOR, "a.comp-name")
                    
                    # Location structure varies
                    try:
                        loc_elem = tuple_node.find_element(By.CSS_SELECTOR, "span.locWdth")
                        location_text = loc_elem.text.strip()
                    except:
                        location_text = "Unknown"

                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    url = title_elem.get_attribute("href")
                    
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
            print(f"Error scraping Naukri: {e}")
            
        return jobs

    def parse_job_page(self, url: str) -> Optional[Job]:
        pass
        
    def close(self):
        if self.driver:
            self.driver.quit()
