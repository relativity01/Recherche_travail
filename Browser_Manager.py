import time
import undetected_chromedriver as uc   
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class BrowserManager:
    def __init__(self):
        options = uc.ChromeOptions()
        options.add_argument(r"--user-data-dir=C:\Users\remot\AppData\Local\UC_Bot_Profile")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument("--start-maximized")
        print("ok")
        self.driver = uc.Chrome(options=options, version_main=148)
        print("ok")
        self.wait_driver = WebDriverWait(self.driver, 3)
        print("ok")

    def open_new_tab(self, url):
            # Opens a new tab natively and automatically switches to it
            self.driver.switch_to.new_window('tab')
            # Navigate to the target URL
            self.driver.get(url)

    def close_current_tab(self):
        if len(self.driver.window_handles) > 1:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def close_all_except_main(self):
        main_handle = self.driver.window_handles[0]
        
        for handle in self.driver.window_handles[1:]:
            try:
                self.driver.switch_to.window(handle)
                self.driver.close()
            except Exception as e:
                print(f"Could not close window {handle}: {e}")
        
        # Switch back to main only if the session is still alive
        try:
            self.driver.switch_to.window(main_handle)
        except Exception as e:
            print(f"Could not switch to main window: {e}")

    def wait_for_dom_stability(self, timeout=10, stable_time=1.0):
        end_time = time.time() + timeout
        last_change = time.time()
        initial_dom = self.driver.execute_script("return document.body.innerHTML.length")

        while time.time() < end_time:
            current_dom = self.driver.execute_script("return document.body.innerHTML.length")
            if current_dom != initial_dom:
                last_change = time.time()
                initial_dom = current_dom
            else:
                if time.time() - last_change >= stable_time:
                    return True
            time.sleep(0.2)
        raise TimeoutError("DOM did not stabilize")

    def quit(self):
        self.driver.quit()

    def is_button_present(self, selector):
        try:
            if selector.startswith("//") or selector.startswith("(//"):
                elements = self.driver.find_elements(By.XPATH, selector)
            else:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return len(elements) > 0
        except Exception:
            return False

