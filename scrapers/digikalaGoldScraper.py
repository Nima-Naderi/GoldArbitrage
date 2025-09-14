import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def digikala_gold_scraper():
    """
    Scrape gold price and price changes from Digikala Gold website using Selenium
    Returns a dictionary with the scraped data
    """
    url = "https://digikala.com/wealth/landing/digital-gold"
    
    # Initialize result dictionary
    result = {
        'gold_price_18_carat': None,
        'price_change': None,
        'currency': 'ریال',
        'unit': '۱ گرم'
    }
    
    # Setup Chrome options for fast headless browsing
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = None
    try:
        # Initialize Chrome driver with automatic driver management
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set page load timeout to 5 seconds
        driver.set_page_load_timeout(5)
        
        # Navigate to the page
        try:
            driver.get(url)
        except Exception as e:
            # print(f"Page load timeout after 5 seconds.")
            nothing = True
            # Continue anyway to try to extract whatever content is available
        
        # Get the HTML content immediately without waiting
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Look for Persian digit price patterns and convert to English
        for element in soup.find_all(['div', 'span', 'p']):
            text = element.get_text().strip()
            if re.search(r'[۰-۹]', text):
                # Look for price patterns with Persian digits
                price_match = re.search(r'[۰-۹]{2},[۰-۹]{3}', text)
                if price_match:
                    persian_price = price_match.group(0)
                    # print(f"Found Persian price: {persian_price}")
                    
                    # Convert Persian digits to English digits
                    persian_to_english = {
                        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
                        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
                    }
                    
                    english_price = persian_price
                    for persian, english in persian_to_english.items():
                        english_price = english_price.replace(persian, english)

                    converted_to_geram = english_price + ",000"
                    
                    # print(f"Converted to English: {english_price}")
                    result['gold_price_18_carat'] = converted_to_geram
                    break
        
        return result
        
    except Exception as e:
        return {'error': f'Selenium scraping error: {str(e)}'}
    finally:
        if driver:
            driver.quit()
