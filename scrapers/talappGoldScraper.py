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

def talapp_gold_scraper():
    """
    Scrape gold price and price changes from Talapp Gold website using Selenium
    Returns a dictionary with the scraped data
    """
    url = "https://talapp.ir/"
    
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
        
        # Set page load timeout to 10 seconds
        driver.set_page_load_timeout(10)
        
        # Navigate to the page
        try:
            driver.get(url)
        except Exception as e:
            nothing = True
            # Continue anyway to try to extract whatever content is available
        
        # Get the HTML content immediately without waiting
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Look for Persian digit price patterns and convert to English
        for element in soup.find_all(['div', 'span', 'p']):
            text = element.get_text().strip()
            if re.search(r'[0-9]', text):
                # Look for price patterns with Persian digits
                price_match = re.search(r'[0-9]{1},[0-9]{3},[0-9]{3}', text)
                if price_match:
                    rial_price = price_match.group(0)
                    rial_price = rial_price.replace(',', '') + "0"
                    result['gold_price_18_carat'] = rial_price
                    break
        
        return result
        
    except Exception as e:
        return {'error': f'Selenium scraping error: {str(e)}'}
    finally:
        if driver:
            driver.quit()

data = talapp_gold_scraper()
print(data)