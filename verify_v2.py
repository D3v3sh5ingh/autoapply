import sys
import os
import logging
from datetime import datetime

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("Verifier")

try:
    print("\n🚀 STARTING EXTENDED SYSTEM VERIFICATION 🚀\n")

    # 1. Test DB Imports and Logic
    logger.info("--- 1. Database Check ---")
    from src.database.db import init_db, save_jobs, get_saved_jobs
    from src.database.models import Job, Profile
    
    init_db()
    
    test_job = Job(
        title="Test Job",
        company="Test Corp",
        url=f"http://test.com/{datetime.now().timestamp()}",
        source="internal_test",
        date_posted=datetime.utcnow()
    )
    
    count = save_jobs([test_job])
    saved = get_saved_jobs()
    
    if count == 1 and len(saved) > 0:
        logger.info(f"✅ Database working. Saved {count} job. Total: {len(saved)}")
        
        # Test Application Tracking
        job_id = saved[0].id
        from src.database.db import mark_job_applied
        success = mark_job_applied(job_id, status="test_applied")
        if success:
             logger.info(f"✅ Application tracking working. Marked Job {job_id} as applied.")
        else:
             logger.error("❌ Application tracking failed.")
             sys.exit(1)
    else:
        logger.error(f"❌ Database save failed. Count: {count}, Total: {len(saved)}")
        sys.exit(1)

    # 2. Test Smart Search Imports
    logger.info("--- 2. Dashboard Logic Check ---")
    from src.ui.dashboard import run_search
    # We can't easily run the UI logic in headless, but successful import means syntax is OK.
    logger.info("✅ Dashboard module imported successfully.")

    # 3. Test Bot Import
    logger.info("--- 3. Bot Check ---")
    from src.application_bot import ApplicationBot
    bot = ApplicationBot(headless=True)
    bot.close()
    logger.info("✅ Bot initialized and closed.")

    print("\n🏁 ALL SYSTEMS GO 🏁")

except Exception as e:
    logger.error(f"CRITICAL FAILURE: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
