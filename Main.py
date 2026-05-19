
import sys
from httpx import options
import os
import time
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


from Database_Manager import DatabaseManager
from Browser_Manager import BrowserManager
from Gemini_Manager import GeminiManager
from Maps_Manager import MapsManager


import tkinter as tk
from tkinter import messagebox


# 1. CONFIGURATION
from dotenv import load_dotenv
import os

load_dotenv()  # reads .env and sets the variables
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLEMAPS_API_KEY = os.getenv("GOOGLEMAPS_API_KEY")


JOB_LIST = [
    "ingénieur simulation", "ingénieur modélisation", "ingénieur calcul scientifique",
    "ingénieur méthodes numériques", "ingénieur physique numérique", "ingénieur R&D simulation",
    "ingénieur recherche simulation", "ingénieur simulation physique", "ingénieur problèmes inverses",
    "ingénieur mathématiques", "ingénieur traitement du signal", "ingénieur imagerie scientifique",
    "ingénieur électromagnétisme", "ingénieur ondes", "ingénieur acoustique numérique",
    "ingénieur multiphysique", "ingénieur éléments finis", "ingénieur thermique",
    "ingénieur radar", "ingénieur quantique", "ingénieur python", "ingénieur c++"
]

BASE_WEBSITES = {
    "indeed": "https://www.indeed.com",
    "hellowork": "https://www.hellowork.com/fr-fr/candidat/connexion-inscription.html#connexion" #"https://www.hellowork.com"
}

SELECTORS = { 
    "google": {
        "search_bar_for_email": "input[type='email']",
        "search_bar_for_password": "input[type='password']"
    },
    
    "indeed": {
        "search_bar_for_job": "input[id*='text-input-what']", 
        "search_bar_for_city": "input[id*='text-input-where']", 
        "search_all_elements": "div.cardOutline:not(.disliked) div.job_seen_beacon", 
        "search_all_offers": "a", 
        "search_all_discard_buttons": "[data-testid='dislikeicon']", 
        "job_title": "h1[class*='jobsearch-JobInfoHeader-title css-1b1jw74 e1tiznh50'] span",
        "company_name": "[class*='css-1h4l2d7 e19afand0']",
        "location": "[class*='css-89aoy7 eu4oa1w0'] div",
        "description": "[class*='jobsearch-JobComponent-description css-dyse26 eu4oa1w0']",
        "next_page": "a[data-testid*='pagination-page-next']",
        "apply_button": "button[id*='indeedApplyButton']",
        "apply_on_another_website_button": "//button[.//span[text()='Continuer pour postuler']]",
        "apply_continue_button": "button[data-testid='continue-button']",
        "check_quel_est_votre_niveau_de_formation": "span[data-testid='safe-markup']",
        "select_niveau_de_formation": "select[id='single-select-question-:rd:']option[label='06 - BAC +4 / BAC +5']",
        "apply_final_button": "//button[@data-testid='submit-application-button']"
},   

    "hellowork": {
        "search_bar_to_connect": "summary[class*='tw-hidden tw-text-white sm:tw-btn-primary-l tw-relative']",
        "search_bar_for_email": "input[type='email']",
        "search_bar_for_password": "input[type='password']",
        "search_bar_for_job": "input[id='k']", 
        "search_bar_for_city": "input[id='l']", 
        "search_all_elements": "a[class*='tw-no-underline tw-outline-none focus-within:tw-underline tw-forwarder tw-inline']", 
        # "search_all_offers": "a", 
        "search_all_discard_buttons": "button[class*='tw-btn-icon-no-outline-m sm:tw-btn-icon-no-outline-l small-group:sm:tw-btn-icon-no-outline-m']", 
        "job_title": "span[class='tw-block tw-typo-xl sm:tw-typo-2xl tw-mb-1']",
        "company_name": "p[class='w-typo-s sm:tw-typo-m']",
        "location": "li[class='tw-tag-secondary-s tw-border-0 tw-readonly']",
        "description": "div[id='b0f']",
        "next_page": "nav[class='tw-hidden sm:tw-flex tw-gap-2 tw-typo-m tw-flex-wrap'] button:last-child",
        "apply_button": "button[form='offer-detail-main-step-form']",
        "apply_on_another_website_button": "//button[.//span[text()='Postuler sur le site du partenaire']]",
        # "apply_continue_button": "button[data-testid='continue-button']",
        # "check_quel_est_votre_niveau_de_formation": "span[data-testid='safe-markup']",
        # "select_niveau_de_formation": "select[id='single-select-question-:rd:']option[label='06 - BAC +4 / BAC +5']",
        # "apply_final_button": "//button[@data-testid='submit-application-button']"
} 


}




class JobScraper(ABC):
    def __init__(self): ...
    
    def run(self):
        try:
            self.browser.driver.get(self.base_url)
            # time.sleep(5)  # Let the page load and potential popups appear
            self.login()

            for job in JOB_LIST:
                print("job_list", job)
                self.search_job(job)
                has_next_page = True
                number_of_page = 1
                
                while has_next_page and number_of_page <3:
                    time.sleep(2) # Wait for the discard job to go off before extracting offers
                    job_urls__discard_buttons = self.get_offer_urls_on_page()
                    
                    for url, discard_button in job_urls__discard_buttons:
                        self.process_offer(url, discard_button)
                    
                    has_next_page = self.go_to_next_page()
                    print(f"Next page exists: {has_next_page}")
                    number_of_page += 1
                
                time.sleep(5) # Pause between different job searches
        finally:
            self.cleanup()


    # --- Subclasses must implement these ---
    @abstractmethod
    def login(self): ...

    @abstractmethod
    def search_job(self, job_title): ...

    @abstractmethod
    def get_offer_urls_on_page(self) -> list: ...

    @abstractmethod
    def process_offer(self, url, discard_button): ...

    @abstractmethod
    def go_to_next_page(self) -> bool: ...

    # --- Shared utilities (no need to override) ---
    def is_already_seen(self, url_id, title=None, company=None):
        if not url_id:
            return False
        self.db.cursor.execute("SELECT 1 FROM job WHERE url_id = ?", (url_id,))
        result = self.db.cursor.fetchone() is not None
        if title and company:
            self.db.cursor.execute(
                "SELECT 1 FROM job WHERE site_source != ? AND titre = ? AND entreprise = ?",
                (self.website_name, title, company)
            )
            return result and self.db.cursor.fetchone() is not None
        return result
    
    def cleanup(self):
        print("\nCleaning up resources...")
        self.browser.quit()
        self.db.close()

    def save_error_page(self, context: str = "error"):
        """Save the current browser page HTML to a timestamped file for debugging."""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"debug_{context}_{timestamp}.html"
            page_source = self.browser.driver.page_source
            with open(filename, "w", encoding="utf-8") as f:
                f.write(page_source)
            print(f"🔍 Page HTML saved to: {filename}")
        except Exception as dump_err:
            print(f"⚠ Could not save page HTML: {dump_err}")

    def _ask_user_if_problem(self) -> bool:
        """
        Shows a dialog asking if there's still a problem.
        Returns True if user says YES (problem exists → go to error),
        Returns False if user says NO (all good → continue).
        """
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.attributes("-topmost", True)  # Bring to front

        result = messagebox.askyesno(
            title="⚠️ Manual Check Required",
            message=(
                "The automation has PAUSED before the final submission.\n\n"
                "Please check the browser and fix any issue manually.\n\n"
                "Is there still a problem?"
            ),
            icon=messagebox.WARNING
        )
        root.destroy()
        return result  # True = YES (problem), False = NO (continue)
    
    def _ask_user_for_field(self, field_name: str, url: str) -> str:
        """
        Shows a dialog asking the user to manually input a missing field.
        Returns the entered string, or empty string if cancelled.
        """
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        dialog = tk.Toplevel(root)
        dialog.title(f"⚠️ Field Not Found: {field_name}")
        dialog.attributes("-topmost", True)
        dialog.grab_set()

        tk.Label(
            dialog,
            text=(
                f"Could not extract '{field_name}' automatically.\n"
                f"URL: {url}\n\n"
                f"Please enter it manually (or leave blank to skip):"
            ),
            wraplength=400,
            justify="left",
            padx=10,
            pady=10
        ).pack()

        entry_var = tk.StringVar()
        entry = tk.Entry(dialog, textvariable=entry_var, width=50)
        entry.pack(padx=10, pady=5)
        entry.focus_set()

        result = {"value": ""}

        def on_confirm():
            result["value"] = entry_var.get().strip()
            dialog.destroy()

        def on_skip():
            result["value"] = ""
            dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="✅ Confirm", command=on_confirm).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⏭ Skip", command=on_skip).pack(side="left", padx=5)

        dialog.bind("<Return>", lambda e: on_confirm())
        dialog.bind("<Escape>", lambda e: on_skip())

        root.wait_window(dialog)
        root.destroy()
        return result["value"]







class IndeedScraper(JobScraper):
    def __init__(self, browser, db, gemini):
        super().__init__()
        self.website_name = "indeed"
        self.base_url = BASE_WEBSITES[self.website_name]
        self.selectors = SELECTORS[self.website_name]
        self.browser = browser
        self.db = db
        self.gemini = gemini
        self.run()
        
    def login(self):...

    def search_job(self, job_title):
        try:
            self.browser.wait_for_dom_stability(timeout=10, stable_time=2)
            
            # Job Title
            search_job = self.browser.wait_driver.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["search_bar_for_job"]))
            )
            search_job.click()
            search_job.send_keys(Keys.CONTROL + "a")
            search_job.send_keys(Keys.BACKSPACE)
            search_job.send_keys(job_title)
            
            # City
            search_city = self.browser.wait_driver.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["search_bar_for_city"]))
            )
            search_city.click()
            time.sleep(0.5)
            search_city.send_keys(Keys.CONTROL + "a")
            search_city.send_keys(Keys.BACKSPACE)
            search_city.send_keys("Paris" + Keys.ENTER)
            
        except Exception as e:
            print(f"❌ Error during search: {e}")
            self.browser.driver.save_screenshot("search_error.png")

    def get_offer_urls_on_page(self):
        elements = self.browser.driver.find_elements(By.CSS_SELECTOR, self.selectors["search_all_elements"])
        print(f"\n✓ Found {len(elements)} job listings on this page")
        
        urls__discard_buttons = []
        for el in elements:
            links = el.find_elements(By.CSS_SELECTOR, self.selectors["search_all_offers"])
            discard_buttons = el.find_elements(By.CSS_SELECTOR, self.selectors["search_all_discard_buttons"])
            
            # Check if both lists have at least one element to avoid IndexError
            if links and discard_buttons:
                # Grab the first element [0] from both lists
                urls__discard_buttons.append((
                    links[0].get_attribute("href"), 
                    discard_buttons[0] # Extracted from the list!
                ))
        return urls__discard_buttons

    def process_offer(self, url, discard_button):
        print(f"\nProcessing: {url}")
        
        # 1. Create a flag to track if we need to discard
        should_discard = False 
        
        try:
            self.browser.open_new_tab(url)
            time.sleep(3) 
            
            final_url = self.browser.driver.current_url
            url_id = self._normalize_url(final_url)
            
            if not url_id:
                print("✗ Invalid or non-Indeed URL format.")
                return # The finally block will still run and close the tab

            if self.browser.is_button_present("section.error-content"):
                print("⚠️ 404 page detected. Skipping.")
                should_discard = True
                return

            # Extract raw data
            title = self.browser.driver.find_element(By.CSS_SELECTOR, self.selectors["job_title"]).text.strip()

            try:
                company = self.browser.driver.find_element(By.CSS_SELECTOR, self.selectors["company_name"]).text.strip()
                if not company:
                    raise ValueError("Empty company name")
            except (NoSuchElementException, ValueError):
                print("⚠️ Company name not found. Asking user...")
                company = self._ask_user_for_field("company", final_url)

            try:
                location = self.browser.driver.find_element(By.CSS_SELECTOR, self.selectors["location"]).text.strip()
                if not location:
                    raise ValueError("Empty location")
            except (NoSuchElementException, ValueError):
                print("⚠️ Location not found. Asking user...")
                location = self._ask_user_for_field("location", final_url)

            
            if self.is_already_seen(url_id, title, company):
                print("⚠️ Already seen this offer. Discarding without processing.")
                should_discard = True
                return
                        
            desc_element = self.browser.driver.find_element(By.CSS_SELECTOR, self.selectors["description"])
            soup = BeautifulSoup(desc_element.get_attribute('innerHTML'), 'html.parser')
            description = soup.get_text(separator='\n', strip=True)

            print("Asking Gemini to analyze description...")
            print(description)
            gemini_analysis = self.gemini.analyze_description(description)

            if gemini_analysis:
                self.browser.driver.implicitly_wait(1)
                if self.browser.is_button_present(self.selectors["apply_button"]):
                    print("There is an apply button, we can apply directly on Indeed!")
                    self.apply_to_job()
                    self.db.save_job(title, final_url, url_id, company, location, description, id_statut=3, site_source=self.website_name)
                elif self.browser.is_button_present(self.selectors["apply_on_another_website_button"]):
                    url_to_company_website = self.browser.driver.find_element(By.XPATH, self.selectors["apply_on_another_website_button"]).get_attribute("href")
                    self.db.save_job(title, url_to_company_website, url_id, company, location, description, id_statut=2, site_source=self.website_name)
                else: 
                    self.save_error_page("no_apply_button")
                    sys.exit("Unexpected case: Gemini accepted the offer but no apply button found. Exiting to avoid discarding.")
                should_discard = True
            elif gemini_analysis is False:
                self.db.save_job(title, final_url, url_id, company, location, description, id_statut=1, site_source=self.website_name)
                print("✗ Discarded by Gemini's analysis.")
                should_discard = True
            elif gemini_analysis is None:
                self.save_error_page("gemini_failure")
                sys.exit("Gemini analysis failed. Exiting.")

        except Exception as e:
            print(f"✗ Error extracting offer data: {e}")
            self.save_error_page("extract_error")
            sys.exit("Critical error during offer processing. Exiting to avoid unintended discarding.")
        finally:
            # 3. Close the job offer tab. 
            # Your BrowserManager already switches focus back to window_handles[0] here!
            self.browser.close_current_tab()
            
            # 4. Now that we are back on the main tab, we can safely interact with the discard button
            if should_discard:
                self.discard_the_job(discard_button)
                print("Discarded the job offer")
  
    def apply_to_job(self):
        try:
            # 1. Clic sur Apply
            apply_btn = self.browser.wait_driver.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors["apply_button"]))
            )
            apply_btn.click()
            print("✓ Clicked Apply button.")
            time.sleep(3)

            # 2. Si on est déjà sur la page de review finale, sauter toutes les étapes intermédiaires
            try:
                print("Checking if we're already on the final review page...")
                apply_final_btn = WebDriverWait(self.browser.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, self.selectors["apply_final_button"]))
                )
                print("✓ Already on review page. Skipping intermediate steps.")
            except TimeoutException:
                # 3. Flow normal : Continue → questions éventuelles → submit
                self._dismiss_cookie_banner()
                apply_continue_btn = self.browser.wait_driver.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors["apply_continue_button"]))
                )
                self._safe_click(apply_continue_btn)
                print("✓ Clicked Continue button.")

                # 4. Question formation (optionnelle)
                try:
                    ...  # ton code existant pour l'éducation
                except Exception:
                    print("ℹ Education question not asked. Skipping...")

                # 5. Cherche le bouton final
                try:
                    apply_final_btn = self.browser.wait_driver.until(
                        EC.element_to_be_clickable((By.XPATH, self.selectors["apply_final_button"]))
                    )
                except TimeoutException:
                    still_problem = self._ask_user_if_problem()
                    if still_problem:
                        self.save_error_page("apply_failure_user_reported")
                        sys.exit()
                    apply_final_btn = self.browser.wait_driver.until(
                        EC.element_to_be_clickable((By.XPATH, self.selectors["apply_final_button"]))
                    )

            # 6. Soumettre
            self._safe_click(apply_final_btn)
            print("✓ Application submitted!")

        except Exception as e:
            print(f"✗ Failed: {e}")
            self.save_error_page("apply_failure")
            sys.exit()

    def _dismiss_cookie_banner(self):
        """Attempt to close the OneTrust cookie consent banner if present."""
        banner_selectors = [
            "button#onetrust-accept-btn-handler",   # "Accept all" button
            "button.onetrust-close-btn-handler",     # Close/X button
            "#onetrust-accept-btn-handler",
            ".onetrust-accept-btn-handler",
        ]
        for selector in banner_selectors:
            try:
                btn = self.browser.driver.find_element(By.CSS_SELECTOR, selector)
                self.browser.driver.execute_script("arguments[0].click();", btn)
                print(f"✓ Dismissed cookie banner via: {selector}")
                time.sleep(1)
                return
            except NoSuchElementException:
                continue
        print("ℹ No cookie banner found (or already dismissed).")

    def _safe_click(self, element):
        """Click an element, falling back to JS click if intercepted."""
        try:
            element.click()
        except Exception:
            print("⚠ Regular click intercepted, using JS click fallback.")
            self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.3)
            self.browser.driver.execute_script("arguments[0].click();", element)



    def discard_the_job(self, discard_button):
        try:
            discard_button.click()
            print("✓ Discarded the job offer.")
        except NoSuchElementException:
            print("No discard button found. Unable to discard the job offer.")
        except Exception as e:
            print(f"✗ Error during discarding the job: {e}")

    def go_to_next_page(self):
        try:
            next_btn = self.browser.driver.find_element(By.CSS_SELECTOR, self.selectors["next_page"])
            url_next = next_btn.get_attribute("href")
            self.browser.driver.get(url_next)
            return True
        except NoSuchElementException:
            print("No next page found.")
            return False

    def _normalize_url(self, final_url: str) -> str:
        if "jk=" not in final_url or "jobs?q=" in final_url:
            return None
        # Extract just the jk parameter
        for param in final_url.split("&"):
            if param.startswith("jk=") or "?jk=" in param:
                return param.split("jk=")[-1]
        return None






class HelloworkScraper(JobScraper):
    def __init__(self, browser, db, gemini):
        super().__init__()
        self.website_name = "hellowork"
        self.base_url = BASE_WEBSITES[self.website_name]
        self.selectors = SELECTORS[self.website_name]
        self.browser = browser
        self.db = db
        self.gemini = gemini
        self.run()
        
    def login(self):
        # connect_button = self.browser.wait_driver.until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["search_bar_to_connect"]))
        # )
        # connect_button.click()

        search_email = self.browser.wait_driver.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["search_bar_for_email"]))
        )
        search_email.click()
        search_email.send_keys(Keys.CONTROL + "a")
        search_email.send_keys(Keys.BACKSPACE)
        search_email.send_keys(os.getenv("HELLOWORK_EMAIL"))

        search_password = self.browser.wait_driver.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["search_bar_for_password"]))
        )
        search_password.click()
        search_password.send_keys(Keys.CONTROL + "a")
        search_password.send_keys(Keys.BACKSPACE)
        search_password.send_keys(os.getenv("HELLOWORK_PASSWORD"))

    def search_job(self, job_title):
        try:
            self.browser.wait_for_dom_stability(timeout=10, stable_time=2)
            
            # Job Title
            search_job = self.browser.wait_driver.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["search_bar_for_job"]))
            )
            search_job.click()
            search_job.send_keys(Keys.CONTROL + "a")
            search_job.send_keys(Keys.BACKSPACE)
            search_job.send_keys(job_title)
            
            # City
            search_city = self.browser.wait_driver.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["search_bar_for_city"]))
            )
            search_city.click()
            time.sleep(0.5)
            search_city.send_keys(Keys.CONTROL + "a")
            search_city.send_keys(Keys.BACKSPACE)
            search_city.send_keys("Paris" + Keys.ENTER)
            
        except Exception as e:
            print(f"❌ Error during search: {e}")
            self.browser.driver.save_screenshot("search_error.png")

    def get_offer_urls_on_page(self):
        elements = self.browser.driver.find_elements(By.CSS_SELECTOR, self.selectors["search_all_elements"])
        print(f"\n✓ Found {len(elements)} job listings on this page")
        
        urls__discard_buttons = []
        for el in elements:
            discard_buttons = el.find_elements(By.CSS_SELECTOR, self.selectors["search_all_discard_buttons"])
            urls__discard_buttons.append((
                el.get_attribute("href"), 
                discard_buttons[0] # Extracted from the list!
            ))
            # links = el.find_elements(By.CSS_SELECTOR, self.selectors["search_all_offers"])
            # discard_buttons = el.find_elements(By.CSS_SELECTOR, self.selectors["search_all_discard_buttons"])
            
            # # Check if both lists have at least one element to avoid IndexError
            # if links and discard_buttons:
            #     # Grab the first element [0] from both lists
            #     urls__discard_buttons.append((
            #         links[0].get_attribute("href"), 
            #         discard_buttons[0] # Extracted from the list!
            #     ))
        return urls__discard_buttons

    def process_offer(self, url, discard_button):
        print(f"\nProcessing: {url}")
        
        # 1. Create a flag to track if we need to discard
        should_discard = False 
        
        try:
            self.browser.open_new_tab(url)
            time.sleep(3) 
            
            final_url = self.browser.driver.current_url
            url_id = self._normalize_url(final_url)
            
            if not url_id:
                print("✗ Invalid or non-Indeed URL format.")
                return # The finally block will still run and close the tab

            # if self.browser.is_button_present("section.error-content"):
            #     print("⚠️ 404 page detected. Skipping.")
            #     should_discard = True
            #     return

            # Extract raw data
            title = self.browser.driver.find_element(By.CSS_SELECTOR, self.selectors["job_title"]).text.strip()

            try:
                company = self.browser.driver.find_element(By.CSS_SELECTOR, self.selectors["company_name"]).text.strip()
                if not company:
                    raise ValueError("Empty company name")
            except (NoSuchElementException, ValueError):
                print("⚠️ Company name not found. Asking user...")
                company = self._ask_user_for_field("company", final_url)

            try:
                location = self.browser.driver.find_element(By.CSS_SELECTOR, self.selectors["location"]).text.strip()
                if not location:
                    raise ValueError("Empty location")
            except (NoSuchElementException, ValueError):
                print("⚠️ Location not found. Asking user...")
                location = self._ask_user_for_field("location", final_url)

            
            if self.is_already_seen(url_id, title, company):
                print("⚠️ Already seen this offer. Discarding without processing.")
                should_discard = True
                return
                        
            desc_element = self.browser.driver.find_element(By.CSS_SELECTOR, self.selectors["description"])
            soup = BeautifulSoup(desc_element.get_attribute('innerHTML'), 'html.parser')
            description = soup.get_text(separator='\n', strip=True)

            print("Asking Gemini to analyze description...")
            print(description)
            gemini_analysis = self.gemini.analyze_description(description)

            if gemini_analysis:
                self.browser.driver.implicitly_wait(1)
                if self.browser.is_button_present(self.selectors["apply_button"]):
                    print("There is an apply button, we can apply directly on Indeed!")
                    self.apply_to_job()
                    self.db.save_job(title, final_url, url_id, company, location, description, id_statut=3, site_source=self.website_name)
                elif self.browser.is_button_present(self.selectors["apply_on_another_website_button"]):
                    url_to_company_website = self.browser.driver.find_element(By.XPATH, self.selectors["apply_on_another_website_button"]).get_attribute("href")
                    self.db.save_job(title, url_to_company_website, url_id, company, location, description, id_statut=2, site_source=self.website_name)
                else: 
                    self.save_error_page("no_apply_button")
                    sys.exit("Unexpected case: Gemini accepted the offer but no apply button found. Exiting to avoid discarding.")
                should_discard = True
            elif gemini_analysis is False:
                self.db.save_job(title, final_url, url_id, company, location, description, id_statut=1, site_source=self.website_name)
                print("✗ Discarded by Gemini's analysis.")
                should_discard = True
            elif gemini_analysis is None:
                self.save_error_page("gemini_failure")
                sys.exit("Gemini analysis failed. Exiting.")

        except Exception as e:
            print(f"✗ Error extracting offer data: {e}")
            self.save_error_page("extract_error")
            sys.exit("Critical error during offer processing. Exiting to avoid unintended discarding.")
        finally:
            # 3. Close the job offer tab. 
            # Your BrowserManager already switches focus back to window_handles[0] here!
            self.browser.close_current_tab()
            
            # 4. Now that we are back on the main tab, we can safely interact with the discard button
            if should_discard:
                self.discard_the_job(discard_button)
                print("Discarded the job offer")
  
    def apply_to_job(self):
        try:
            # 1. Clic sur Apply
            apply_btn = self.browser.wait_driver.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors["apply_button"]))
            )
            apply_btn.click()
            print("✓ Clicked Apply button.")
            time.sleep(3)

            # 2. Si on est déjà sur la page de review finale, sauter toutes les étapes intermédiaires
            try:
                print("Checking if we're already on the final review page...")
                apply_final_btn = WebDriverWait(self.browser.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, self.selectors["apply_final_button"]))
                )
                print("✓ Already on review page. Skipping intermediate steps.")
            except TimeoutException:
                # 3. Flow normal : Continue → questions éventuelles → submit
                self._dismiss_cookie_banner()
                apply_continue_btn = self.browser.wait_driver.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors["apply_continue_button"]))
                )
                self._safe_click(apply_continue_btn)
                print("✓ Clicked Continue button.")

                # 4. Question formation (optionnelle)
                try:
                    ...  # ton code existant pour l'éducation
                except Exception:
                    print("ℹ Education question not asked. Skipping...")

                # 5. Cherche le bouton final
                try:
                    apply_final_btn = self.browser.wait_driver.until(
                        EC.element_to_be_clickable((By.XPATH, self.selectors["apply_final_button"]))
                    )
                except TimeoutException:
                    still_problem = self._ask_user_if_problem()
                    if still_problem:
                        self.save_error_page("apply_failure_user_reported")
                        sys.exit()
                    apply_final_btn = self.browser.wait_driver.until(
                        EC.element_to_be_clickable((By.XPATH, self.selectors["apply_final_button"]))
                    )

            # 6. Soumettre
            self._safe_click(apply_final_btn)
            print("✓ Application submitted!")

        except Exception as e:
            print(f"✗ Failed: {e}")
            self.save_error_page("apply_failure")
            sys.exit()

    def _dismiss_cookie_banner(self):
        """Attempt to close the OneTrust cookie consent banner if present."""
        banner_selectors = [
            "button#onetrust-accept-btn-handler",   # "Accept all" button
            "button.onetrust-close-btn-handler",     # Close/X button
            "#onetrust-accept-btn-handler",
            ".onetrust-accept-btn-handler",
        ]
        for selector in banner_selectors:
            try:
                btn = self.browser.driver.find_element(By.CSS_SELECTOR, selector)
                self.browser.driver.execute_script("arguments[0].click();", btn)
                print(f"✓ Dismissed cookie banner via: {selector}")
                time.sleep(1)
                return
            except NoSuchElementException:
                continue
        print("ℹ No cookie banner found (or already dismissed).")

    def _safe_click(self, element):
        """Click an element, falling back to JS click if intercepted."""
        try:
            element.click()
        except Exception:
            print("⚠ Regular click intercepted, using JS click fallback.")
            self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.3)
            self.browser.driver.execute_script("arguments[0].click();", element)



    def discard_the_job(self, discard_button):
        try:
            discard_button.click()
            print("✓ Discarded the job offer.")
        except NoSuchElementException:
            print("No discard button found. Unable to discard the job offer.")
        except Exception as e:
            print(f"✗ Error during discarding the job: {e}")

    def go_to_next_page(self):
        try:
            next_btn = self.browser.driver.find_element(By.CSS_SELECTOR, self.selectors["next_page"])
            next_btn.click()
            return True
        except NoSuchElementException:
            print("No next page found.")
            return False

    def _normalize_url(self, final_url: str) -> str:
        if "/fr-fr/emplois/" in final_url:
            return final_url.split("/fr-fr/emplois/")[-1].replace(".html", "")
        return None








def login_google(browser):
    print("\nAttempting login...")
    try:
        button = browser.driver.find_element(By.LINK_TEXT, "Connexion")
        button.click()
        
        main_window = browser.driver.current_window_handle
        wait_short = WebDriverWait(browser.driver, 5)
        
        google_btn = wait_short.until(EC.element_to_be_clickable((By.ID, "login-google-button")))
        google_btn.click()
        print("✓ Google button clicked.")
        
        wait_short.until(EC.number_of_windows_to_be(2))
        
        for window_handle in browser.driver.window_handles:
            if window_handle != main_window:
                browser.driver.switch_to.window(window_handle)
                break
        
        print("✓ Switched to Google login window.")
        
        # Email input
        search_email = browser.wait_driver.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["google"]["search_bar_for_email"]))
        )
        search_email.send_keys(EMAIL + Keys.ENTER)
        print("✓ Email entered.")
        
        # Password input
        time.sleep(5)
        search_password = browser.wait_driver.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["google"]["search_bar_for_password"]))
        )
        search_password.send_keys(PASSWORD + Keys.ENTER)
        print("✓ Password entered.")
        
        time.sleep(10) # Wait for manual 2FA if needed
        browser.driver.switch_to.window(main_window)
        print("✓ Returned to main window.")
        
    except (TimeoutException, NoSuchElementException) as e:
        print("ℹ️ Login flow interrupted or skipped. Continuing...")
        browser.close_all_except_main()

def run_scraper():
    browser = BrowserManager()
    db = DatabaseManager()
    gemini = GeminiManager(api_key=GEMINI_API_KEY)
    print(GEMINI_API_KEY)
    browser.driver.maximize_window()
    login_google(browser)
    IndeedScraper(browser, db, gemini)


if __name__ == "__main__":
    run_scraper()


    # import google.generativeai as genai

    # genai.configure(api_key=GEMINI_API_KEY)
    # for m in genai.list_models():
    #     if "generateContent" in m.supported_generation_methods:
    #         print(m.name)