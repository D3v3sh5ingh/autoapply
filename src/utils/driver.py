import logging
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger("WebDriverManager")

def get_driver(headless: bool = True):
    """
    Returns a configured Chrome WebDriver instance.
    Handles installation and cleanup of corrupted drivers automatically.
    """
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    # Anti-detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # 1. Try standard install
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        logger.warning(f"Standard driver install failed: {e}")
        error_str = str(e)
        if "WinError 193" in error_str or "executable" in error_str:
            logger.info("Detected corrupted driver. Cleaning cache and retrying...")
            _clean_wdm_cache()
            
            # 2. Retry after clean
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                return driver
            except Exception as e2:
                 logger.error(f"Retry failed: {e2}")
                 raise e2
        raise e

def _clean_wdm_cache():
    """
    Aggressively cleans the webdriver_manager cache.
    """
    user_home = os.path.expanduser("~")
    wdm_path = os.path.join(user_home, ".wdm")
    if os.path.exists(wdm_path):
        try:
            shutil.rmtree(wdm_path)
            logger.info(f"Deleted {wdm_path}")
        except Exception as e:
            logger.error(f"Failed to delete .wdm: {e}")
