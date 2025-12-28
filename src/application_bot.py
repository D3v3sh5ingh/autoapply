import time
import os
import random
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.utils.logger import setup_logger # Centralized logger
from .database.models import Profile

class ApplicationBot:
    def __init__(self, headless: bool = False):
        self.logger = setup_logger("ApplicationBot")
        self.driver = self._setup_driver(headless)
        self.logger.info(f"Bot initialized (Headless={headless})")

    def _setup_driver(self, headless: bool):
        from src.utils.driver import get_driver
        return get_driver(headless)

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Bot closed.")
            except: pass

    def fill_application(self, url: str, profile: Profile):
        try:
            self.logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for meaningful content
            time.sleep(4) 
            
            # 1. Check if we are on a login page
            current_url = self.driver.current_url.lower()
            page_title = self.driver.title.lower()
            if "login" in current_url or "sign" in current_url or "auth" in current_url or "join" in current_url:
                self.logger.warning(f"Likely a Login/Signup page ({current_url}). Skipping to avoid messing up account.")
                return # Abort

            # 2. Try to click "Apply" or "Easy Apply" if it's not a direct form
            if self._try_click_apply_button():
                self.logger.info("Clicked an 'Apply' button. Waiting for form...")
                time.sleep(3)

            # 2. Fill Fields
            filled_count = 0
            
            # Personal Info
            filled_count += self._fill_input_by_keywords(["first_name", "firstname", "first"], profile.name.split()[0] if profile.name else "")
            filled_count += self._fill_input_by_keywords(["last_name", "lastname", "last"], " ".join(profile.name.split()[1:]) if profile.name else "")
            filled_count += self._fill_input_by_keywords(["full_name", "fullname", "name"], profile.name or "")
            filled_count += self._fill_input_by_keywords(["email", "e-mail", "mail"], profile.email or "")
            filled_count += self._fill_input_by_keywords(["phone", "mobile", "contact", "cell"], profile.phone or "")
            
            # Links/URLs
            if "linkedin" in (url or "").lower():
                # Sometimes asks for LinkedIn profile URL
                pass 
                
            # 3. Resume Upload
            if profile.resume_path and os.path.exists(profile.resume_path):
                self._upload_resume(profile.resume_path)
            
            self.logger.info(f"Bot finished logic. Filled ~{filled_count} fields.")
            
        except Exception as e:
            self.logger.error(f"Bot crashed on {url}: {e}")
            raise e

    def _try_click_apply_button(self):
        """
        Tries to find and click an 'Apply' button to open the form.
        Returns True if clicked, False otherwise.
        """
        # Common selectors for Apply buttons
        selectors = [
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]",
            "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]",
            "//input[@type='submit' and contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]"
        ]
        
        for xpath in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                for btn in elements:
                    if btn.is_displayed() and btn.is_enabled():
                        # Verify it's not "Apply later" or something else
                        text = btn.text.lower()
                        if "apply" in text and len(text) < 30:
                            self.logger.info(f"Found Apply button: '{text}'")
                            btn.click()
                            return True
            except: continue
        return False

    def _fill_input_by_keywords(self, keywords: list, value: str):
        if not value: return 0
        
        # Heuristic: Find inputs -> Check attributes -> Fuzzy Match
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        textarea = self.driver.find_elements(By.TAG_NAME, "textarea")
        
        for inp in inputs + textarea:
            try:
                if not inp.is_displayed() or not inp.is_enabled(): continue
                
                # Check type
                type_attr = inp.get_attribute("type")
                if type_attr in ["hidden", "submit", "button", "checkbox", "radio", "file"]:
                    continue
                
                # Build metadata string to search keywords in
                meta_parts = [
                    inp.get_attribute("name"),
                    inp.get_attribute("id"),
                    inp.get_attribute("placeholder"),
                    inp.get_attribute("aria-label"),
                    # Try to get label text?? Too expensive maybe.
                ]
                meta = " ".join([str(x).lower() for x in meta_parts if x])
                
                # Check if matches ANY keyword
                if any(k in meta for k in keywords):
                    # Check if already filled
                    curr_val = inp.get_attribute("value")
                    if curr_val and len(curr_val) > 0:
                        continue
                        
                    self.logger.info(f"Filling field '{meta[:30]}...' with '{value[:5]}***'")
                    inp.clear()
                    inp.send_keys(value)
                    return 1
            except: continue
        return 0

    def _upload_resume(self, path: str):
        try:
            file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            if file_inputs:
                self.logger.info(f"Found file input. Uploading: {path}")
                file_inputs[0].send_keys(path)
            else:
                self.logger.warning("No file input found for resume.")
        except Exception as e:
            self.logger.error(f"Failed to upload resume: {e}")
