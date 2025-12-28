from abc import ABC, abstractmethod
from typing import List, Optional
from ..database.models import Job

class BaseScraper(ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None  # Setup requests session here

    @abstractmethod
    def scrape(self, query: str, location: str, limit: int = 10) -> List[Job]:
        """
        Scrape jobs based on query and location.
        Returns a list of Job objects.
        """
        pass

    @abstractmethod
    def parse_job_page(self, url: str) -> Optional[Job]:
        """
        Parse a single job page for more details if needed.
        """
        pass
