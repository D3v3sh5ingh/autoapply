import os
import sys
import logging
from src.scraper.instahyre_scraper import InstahyreScraper
from src.scraper.naukri_scraper import NaukriScraper
from src.scraper.linkedin_scraper import LinkedInScraper
from src.scraper.generic_scraper import GenericScraper
from src.matcher.semantic_matcher import SemanticMatcher
from src.database.models import Profile, Job
from src.application_bot import ApplicationBot

# Setup Logging to Console
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("Verifier")

def verify_ssl():
    logger.info("--- 1. SSL & Environment Check ---")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✅ SSL Certs working. Model loaded.")
    except Exception as e:
        logger.error(f"❌ SSL/Model Error: {e}")

def verify_instahyre():
    logger.info("--- 2. Instahyre Scraper Check ---")
    try:
        scraper = InstahyreScraper()
        jobs = scraper.scrape("Data Engineer", "Pune", 5)
        if jobs:
            logger.info(f"✅ Instahyre found {len(jobs)} jobs. Example: {jobs[0].title} @ {jobs[0].company}")
        else:
            logger.warning("⚠️ Instahyre returned 0 jobs (might be valid if no matches, but suspicious).")
    except Exception as e:
        logger.error(f"❌ Instahyre Failed: {e}")

def verify_naukri():
    logger.info("--- 3. Naukri Scraper Check ---")
    try:
        scraper = NaukriScraper() 
        # Note: Naukri might fail in headless without user-agent tweaks
        jobs = scraper.scrape("Data Engineer", "Pune", 5)
        if jobs:
            logger.info(f"✅ Naukri found {len(jobs)} jobs.")
        else:
            logger.warning("⚠️ Naukri returned 0 jobs.")
    except Exception as e:
        logger.error(f"❌ Naukri Failed: {e}")

def verify_linkedin():
    logger.info("--- 4. LinkedIn Scraper Check ---")
    try:
        scraper = LinkedInScraper()
        jobs = scraper.scrape("Data Engineer", "Pune", 5)
        if jobs:
            logger.info(f"✅ LinkedIn found {len(jobs)} jobs.")
        else:
            logger.warning("⚠️ LinkedIn returned 0 jobs.")
    except Exception as e:
        logger.error(f"❌ LinkedIn Failed: {e}")

def verify_bot():
    logger.info("--- 5. Auto-Apply Bot Check ---")
    try:
        bot = ApplicationBot(headless=True)
        # We won't actually submit, just check if it opens
        bot.close()
        logger.info("✅ Bot initialized and closed successfully.")
    except Exception as e:
        logger.error(f"❌ Bot Failed: {e}")

if __name__ == "__main__":
    print("\n🚀 STARTING SYSTEM VERIFICATION 🚀\n")
    
    # 1. Environment
    # Inject SSL logic if needed
    try:
        import certifi
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        os.environ['SSL_CERT_FILE'] = certifi.where()
    except: pass

    verify_ssl()
    verify_instahyre()
    verify_bot()
    # verify_naukri() # Selenium
    # verify_linkedin() # Selenium
    
    print("\n🏁 VERIFICATION COMPLETE 🏁\n")
