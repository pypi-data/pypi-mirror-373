import os
import time
from pathlib import Path
import undetected_chromedriver as uc
from markdownify import markdownify as md
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

class DeepSeek:
    APP_URL = "https://chat.deepseek.com/"

    def __init__(self, profile_path=None, session_name=None, headless=False, chrome_path=None):
        self.profile_path = Path(profile_path) if profile_path else Path('deepseek_default_profile')
        self.profile_path.mkdir(exist_ok=True)
        
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={self.profile_path}")
        
        if headless:
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
        
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        if chrome_path and os.path.exists(chrome_path):
            options.binary_location = chrome_path
        
        self.driver = uc.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self._login()
        self.is_first_chat = False
        self._select_chat_session(session_name)

    def _login(self):
        self.driver.get(self.APP_URL)
        try:
            WebDriverWait(self.driver, 5).until(EC.url_to_be(self.APP_URL))
        except TimeoutException:
            WebDriverWait(self.driver, 600).until(EC.url_to_be(self.APP_URL))

    def _select_chat_session(self, session_name):
        if session_name is not None:
            self.driver.find_elements(By.XPATH,
                f"//*[starts-with(text(), '{session_name}')]"
            )[0].click()
        else:
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys('j').key_up(Keys.CONTROL).perform()
            self.is_first_chat = True

    def send_prompt(self, prompt):
        if self.is_first_chat:
            num_history_replies = 0
        else:
            history_replies = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "ds-markdown"))
            )
            num_history_replies = len(history_replies)

        time.sleep(1)
        prompt_escaped = prompt.replace("\n", Keys.SHIFT + Keys.ENTER + Keys.SHIFT)
        
        input_selectors = [
            "#chat-input",
            "textarea",
            "div[contenteditable='true']",
            "input[type='text']"
        ]
        
        prompt_input = None
        for selector in input_selectors:
            try:
                prompt_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                break
            except:
                continue
        
        if not prompt_input:
            raise Exception("Could not find input element")
            
        prompt_input.clear()
        prompt_input.send_keys(prompt_escaped)
        time.sleep(1)
        prompt_input.send_keys(Keys.ENTER)

        return self._get_latest_reply(num_history_replies)

    def _get_latest_reply(self, num_history_replies):
        latest_reply = None
        maximum_trials = 600
        for _ in range(maximum_trials):
            all_replies = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "ds-markdown"))
            )
            if len(all_replies) >= (num_history_replies + 1):
                latest_reply = all_replies[num_history_replies]
                self.is_first_chat = False
                break
            time.sleep(1)

        if latest_reply is None:
            raise TimeoutException("Failed to get the latest reply from DeepSeek.")

        previous_html = ""
        stable_count = 0
        stability_threshold = 4
        for _ in range(maximum_trials):
            latest_html = latest_reply.get_attribute('innerHTML')
            if latest_html == previous_html:
                stable_count += 1
                if stable_count >= stability_threshold:
                    return md(latest_html).strip()
            else:
                stable_count = 0
            previous_html = latest_html
            time.sleep(1)

        raise TimeoutException("WARNING: Failed to get the reply HTML.")

    def close(self):
        self.driver.quit()