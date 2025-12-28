from src.scraper.hn_scraper import HNScraper
from src.scraper.linkedin_scraper import LinkedInScraper
from src.scraper.naukri_scraper import NaukriScraper

def test_hn():
    print("\n=== Testing Hacker News Scraper ===")
    scraper = HNScraper()
    jobs = scraper.scrape(limit=3)
    print(f"Found {len(jobs)} jobs")
    for job in jobs:
        print(f"  - {job.title} | {job.url}")

def test_linkedin():
    print("\n=== Testing LinkedIn Scraper (Selenium) ===")
    try:
        scraper = LinkedInScraper(headless=True)
        jobs = scraper.scrape(query="python developer", location="Bangalore", limit=3)
        print(f"Found {len(jobs)} jobs")
        for job in jobs:
            print(f"  - {job.title} at {job.company} ({job.location})")
            print(f"    URL: {job.url}")
        scraper.close()
    except Exception as e:
        print(f"LinkedIn test failed: {e}")

def test_naukri():
    print("\n=== Testing Naukri Scraper (Selenium) ===")
    try:
        scraper = NaukriScraper(headless=True)
        jobs = scraper.scrape(query="python developer", location="Bangalore", limit=3)
        print(f"Found {len(jobs)} jobs")
        for job in jobs:
            print(f"  - {job.title} at {job.company}")
            print(f"    URL: {job.url}")
        scraper.close()
    except Exception as e:
        print(f"Naukri test failed: {e}")

if __name__ == "__main__":
    test_hn()
    test_linkedin()
    test_naukri()
