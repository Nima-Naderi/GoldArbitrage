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
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.price_converters import remove_comma, toman_to_rial, format_number_with_commas
from utils.price_converters import convert_persian_to_english_digits

def goldika_gold_scraper():
    """
    Scrape gold price and price changes from Goldika Gold website using Selenium
    Returns a dictionary with the scraped data
    """
    url = "https://goldika.ir/"
    
    result = {
        'gold_price_18_carat': None,
        'price_change': None,
        'currency': 'ریال',
        'unit': '۱ گرم'
    }
    
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
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.set_page_load_timeout(10)
        
        try:
            driver.get(url)
            time.sleep(4)
        except Exception as e:
            nothing = True
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        for element in soup.find_all(['div', 'span', 'p']):
            text = element.get_text().strip()
            if re.search(r'[۰-۹]', text):
                price_match = re.search(r'[۰-۹]{1},[۰-۹]{3},[۰-۹]{3}', text)
                if price_match:
                    toman_price = remove_comma(price_match.group(0))
                    english_price = convert_persian_to_english_digits(toman_price)
                    rial_price = toman_to_rial(english_price)
                    result['gold_price_18_carat'] = format_number_with_commas(rial_price)
                    break
        
        return result
        
    except Exception as e:
        return {'error': f'Selenium scraping error: {str(e)}'}
    finally:
        if driver:
            driver.quit()