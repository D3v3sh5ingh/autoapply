from src.scraper.hn_scraper import HNScraper

def main():
    scraper = HNScraper()
    print("Scraping Hacker News for jobs...")
    jobs = scraper.scrape(limit=5)
    print(f"Found {len(jobs)} jobs:")
    for job in jobs:
        print(f"- {job.title} at {job.company}")
        print(f"  URL: {job.url}")
        print(f"  Location: {job.location}")
        print("-" * 20)

if __name__ == "__main__":
    main()
