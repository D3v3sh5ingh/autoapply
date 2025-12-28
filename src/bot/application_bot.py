import time
import os
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from ..database.models import Profile

class ApplicationBot:
    def __init__(self, headless: bool = False):
        self.driver = self._setup_driver(headless)
        
    def _setup_driver(self, headless: bool):
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        # Anti-detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def close(self):
        if self.driver:
            self.driver.quit()

    def fill_application(self, url: str, profile: Profile):
        print(f"Bot navigating to: {url}")
        self.driver.get(url)
        time.sleep(3) 

        self._try_click_apply_button()
        
        filled_count = 0
        filled_count += self._fill_input_by_keywords(["first_name", "firstname", "first name"], profile.name.split()[0] if profile.name else "")
        filled_count += self._fill_input_by_keywords(["last_name", "lastname", "last name"], " ".join(profile.name.split()[1:]) if profile.name else "")
        filled_count += self._fill_input_by_keywords(["full_name", "fullname", "name"], profile.name or "")
        filled_count += self._fill_input_by_keywords(["email", "e-mail"], profile.email or "")
        filled_count += self._fill_input_by_keywords(["phone", "mobile", "contact"], profile.phone or "")
        
        if profile.resume_path and os.path.exists(profile.resume_path):
            self._upload_resume(profile.resume_path)
        
        print(f"Bot finished. Filled ~{filled_count} fields.")

    def _try_click_apply_button(self):
        buttons = self.driver.find_elements(By.TAG_NAME, "button") + self.driver.find_elements(By.TAG_NAME, "a")
        for btn in buttons:
            try:
                text = btn.text.lower()
                if "apply" in text and len(text) < 20:
                    if btn.is_displayed():
                        btn.click()
                        time.sleep(2)
                        break
            except:
                continue

    def _fill_input_by_keywords(self, keywords: list, value: str):
        if not value: return 0
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        for inp in inputs:
            try:
                if not inp.is_displayed(): continue
                meta = (inp.get_attribute("name") or "") + " " + (inp.get_attribute("id") or "") + " " + (inp.get_attribute("placeholder") or "")
                meta = meta.lower()
                if any(k in meta for k in keywords):
                    if inp.get_attribute("value"): continue
                    inp.clear()
                    inp.send_keys(value)
                    return 1
            except: continue
        return 0

    def _upload_resume(self, path: str):
        file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        if file_inputs:
            try:
                file_inputs[0].send_keys(path)
            except Exception as e:
                print(f"Failed to upload resume: {e}")
