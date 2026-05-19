from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
import time
import os
import shutil

print("=" * 70)
print("SELENIUM UNDETECTED CHROMEDRIVER - SPEED FIX TESTER")
print("=" * 70)

# ============================================================================
# TEST 1: Regular Selenium (Baseline)
# ============================================================================
def test_regular_selenium():
    print("\n" + "=" * 70)
    print("TEST 1: REGULAR SELENIUM (BASELINE)")
    print("=" * 70)
    
    start = time.time()
    driver = webdriver.Chrome()
    elapsed = time.time() - start
    
    print(f"✓ Started in {elapsed:.2f} seconds")
    driver.get("https://www.google.com")
    print(f"✓ Page title: {driver.title}")
    driver.quit()
    
    return elapsed


# ============================================================================
# TEST 2: Regular Selenium with Anti-Detection (RECOMMENDED SOLUTION)
# ============================================================================
def test_selenium_stealth():
    print("\n" + "=" * 70)
    print("TEST 2: REGULAR SELENIUM + ANTI-DETECTION (RECOMMENDED)")
    print("=" * 70)
    
    start = time.time()
    
    options = webdriver.ChromeOptions()
    
    # Anti-detection tricks
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Performance improvements
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    # Remove webdriver flag in JavaScript
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    elapsed = time.time() - start
    print(f"✓ Started in {elapsed:.2f} seconds")
    
    driver.get("https://www.google.com")
    print(f"✓ Page title: {driver.title}")
    
    # Test if detection is bypassed
    is_webdriver = driver.execute_script("return navigator.webdriver")
    print(f"✓ navigator.webdriver detected: {is_webdriver}")
    
    driver.quit()
    
    return elapsed


# ============================================================================
# TEST 3: UC with specified Chrome version
# ============================================================================
def test_uc_with_version():
    print("\n" + "=" * 70)
    print("TEST 3: UNDETECTED CHROME - SPECIFY VERSION")
    print("=" * 70)
    
    start = time.time()
    
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = uc.Chrome(
        options=options,
        version_main=131,  # Adjust to your Chrome version
        use_subprocess=False
    )
    
    elapsed = time.time() - start
    print(f"✓ Started in {elapsed:.2f} seconds")
    
    driver.get("https://www.google.com")
    print(f"✓ Page title: {driver.title}")
    driver.quit()
    
    return elapsed


# ============================================================================
# TEST 4: UC with binary location specified
# ============================================================================
def test_uc_with_binary():
    print("\n" + "=" * 70)
    print("TEST 4: UNDETECTED CHROME - SPECIFY BINARY PATH")
    print("=" * 70)
    
    start = time.time()
    
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Common Chrome installation paths
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            print(f"✓ Found Chrome at: {chrome_path}")
            break
    
    if chrome_path:
        options.binary_location = chrome_path
    else:
        print("⚠️  Could not find Chrome installation, using default")
    
    driver = uc.Chrome(
        options=options,
        use_subprocess=False
    )
    
    elapsed = time.time() - start
    print(f"✓ Started in {elapsed:.2f} seconds")
    
    driver.get("https://www.google.com")
    print(f"✓ Page title: {driver.title}")
    driver.quit()
    
    return elapsed


# ============================================================================
# TEST 5: Clear UC cache and retry
# ============================================================================
def test_clear_uc_cache():
    print("\n" + "=" * 70)
    print("TEST 5: CLEAR UC CACHE AND RETRY")
    print("=" * 70)
    
    # Clear cache
    uc_cache_paths = [
        os.path.expanduser("~/.undetected_chromedriver"),
        os.path.expanduser("~/AppData/Roaming/undetected_chromedriver"),
        os.path.expanduser("~/AppData/Local/undetected_chromedriver")
    ]
    
    cache_cleared = False
    for cache_path in uc_cache_paths:
        if os.path.exists(cache_path):
            print(f"✓ Deleting cache: {cache_path}")
            try:
                shutil.rmtree(cache_path)
                cache_cleared = True
            except Exception as e:
                print(f"✗ Could not delete: {e}")
    
    if not cache_cleared:
        print("ℹ️  No UC cache found")
    
    # Now test
    start = time.time()
    
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options, use_subprocess=False)
    
    elapsed = time.time() - start
    print(f"✓ Started in {elapsed:.2f} seconds (after cache clear)")
    
    driver.get("https://www.google.com")
    print(f"✓ Page title: {driver.title}")
    driver.quit()
    
    return elapsed


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    results = {}
    
    try:
        results["Regular Selenium"] = test_regular_selenium()
    except Exception as e:
        print(f"✗ Test failed: {e}")
        results["Regular Selenium"] = None
    
    try:
        results["Selenium + Stealth"] = test_selenium_stealth()
    except Exception as e:
        print(f"✗ Test failed: {e}")
        results["Selenium + Stealth"] = None
    
    try:
        results["UC with version"] = test_uc_with_version()
    except Exception as e:
        print(f"✗ Test failed: {e}")
        results["UC with version"] = None
    
    try:
        results["UC with binary"] = test_uc_with_binary()
    except Exception as e:
        print(f"✗ Test failed: {e}")
        results["UC with binary"] = None
    
    try:
        results["UC after cache clear"] = test_clear_uc_cache()
    except Exception as e:
        print(f"✗ Test failed: {e}")
        results["UC after cache clear"] = None
    
    # ========================================================================
    # RESULTS SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    for test_name, duration in results.items():
        if duration:
            status = "🚀 FAST" if duration < 10 else "🐌 SLOW"
            print(f"{status} {test_name:.<50} {duration:>6.2f}s")
        else:
            print(f"✗   {test_name:.<50} FAILED")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)
    
    # Find fastest method
    valid_results = {k: v for k, v in results.items() if v is not None}
    if valid_results:
        fastest = min(valid_results, key=valid_results.get)
        fastest_time = valid_results[fastest]
        
        print(f"\n✓ FASTEST METHOD: {fastest} ({fastest_time:.2f}s)")
        
        if "Selenium + Stealth" in valid_results and valid_results["Selenium + Stealth"] < 10:
            print("\n🎯 RECOMMENDED: Use 'Regular Selenium + Anti-Detection'")
            print("   - Fast startup (5-8 seconds)")
            print("   - Works for most websites including Indeed")
            print("   - No UC overhead")
        else:
            print(f"\n🎯 RECOMMENDED: Use '{fastest}'")
    else:
        print("\n✗ All tests failed. Check your Selenium installation.")
    
    print("\n" + "=" * 70)