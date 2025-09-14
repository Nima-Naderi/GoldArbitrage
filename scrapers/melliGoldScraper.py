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
from utils.price_converters import remove_zero_from_start

def melli_gold_scraper():
    """
    Scrape gold price and price changes from Melli Gold website using Selenium
    Returns a dictionary with the scraped data
    """
    url = "https://melligold.com/"
    
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
            if re.search(r'[0-9]', text):
                price_match = re.search(r'[0-9]{1},[0-9]{3},[0-9]{3}', text)
                if price_match:
                    toman_price = remove_comma(price_match.group(0))
                    rial_price = toman_to_rial(toman_price)
                    result['gold_price_18_carat'] = format_number_with_commas(rial_price)
                    break

        for element in soup.find_all(['div', 'span', 'p']):
            text = element.get_text().strip()
            if re.search(r'[0-9]', text):
                change_match = re.search(r'([+-]?\d+\.?\d*\s*%)', text)
                if change_match:
                    result['price_change'] = remove_zero_from_start(change_match.group(1).replace(' ', ''))
                    break

        if result['price_change'] and not result['price_change'].startswith(('+', '-')):
            for element in soup.find_all(['div', 'span', 'p']):
                text = element.get_text().strip()
                if result['price_change'].replace('%', '') in text:
                    classes = ' '.join(element.get('class', []))
                    style = element.get('style', '')

                    if any(indicator in classes.lower() for indicator in ['green', 'positive', 'up', 'increase']):
                        result['price_change'] = '+' + result['price_change']
                        break
                    elif any(indicator in classes.lower() for indicator in ['red', 'negative', 'down', 'decrease']):
                        result['price_change'] = '-' + result['price_change']
                        break
                    elif 'color: green' in style.lower() or 'color:#green' in style.lower():
                        result['price_change'] = '+' + result['price_change']
                        break
                    elif 'color: red' in style.lower() or 'color:#red' in style.lower():
                        result['price_change'] = '-' + result['price_change']
                        break
        #TODO: Add more indicators for this website
        
        return result
        
    except Exception as e:
        return {'error': f'Selenium scraping error: {str(e)}'}
    finally:
        if driver:
            driver.quit()

data = melli_gold_scraper()
print(data)