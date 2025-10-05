from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
 
 
 
 
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.price_converters import convert_persian_to_english_digits, convert_milligram_price_to_gram_price, remove_comma, format_number_with_commas

def digikala_gold_scraper():
    """
    Scrape gold price and price changes from Digikala Gold website using Selenium
    Returns a dictionary with the scraped data
    """
    url = "https://digikala.com/wealth/landing/digital-gold"
    
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
        driver = webdriver.Chrome(options=chrome_options)
        
        driver.set_page_load_timeout(30)
        
        try:
            driver.get(url)
            time.sleep(8)
        except Exception:
            pass
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        for element in soup.find_all(['div', 'span', 'p']):
            text = element.get_text().strip()
            if re.search(r'[۰-۹]', text):
                price_match = re.search(r'[۰-۹]{2,3},[۰-۹]{3}', text)
                if price_match:
                    persian_price = remove_comma(price_match.group(0))
                    english_price = convert_persian_to_english_digits(persian_price)
                    converted_to_gram = convert_milligram_price_to_gram_price(english_price)
                    formatted_price = format_number_with_commas(converted_to_gram)
                    
                    result['gold_price_18_carat'] = formatted_price
                    break
            # Fallback: match Latin digits if Persian digits not found
            if re.search(r'[0-9]', text) and result['gold_price_18_carat'] is None:
                price_match_latin = re.search(r'\d{2,3},\d{3}', text)
                if price_match_latin:
                    latin_price = remove_comma(price_match_latin.group(0))
                    converted_to_gram = convert_milligram_price_to_gram_price(latin_price)
                    formatted_price = format_number_with_commas(converted_to_gram)
                    result['gold_price_18_carat'] = formatted_price
                    break
        
        return result
        
    except Exception as e:
        return {'error': f'Selenium scraping error: {str(e)}'}
    finally:
        if driver:
            driver.quit()
 