from abc import ABC, abstractmethod
import requests
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from typing import Dict, Optional, Union
import logging
import re

class GoldPriceData:
    """Data class to hold gold price information"""
    def __init__(self, price: float, change_24h: float, change_percent: float = None, 
                 currency: str = "IRR", source: str = "", timestamp: str = ""):
        self.price = price
        self.change_24h = change_24h
        self.change_percent = change_percent
        self.currency = currency
        self.source = source
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict:
        return {
            'price': self.price,
            'change_24h': self.change_24h,
            'change_percent': self.change_percent,
            'currency': self.currency,
            'source': self.source,
            'timestamp': self.timestamp
        }

class BaseScraper(ABC):
    """Base class for all gold price scrapers"""
    
    def __init__(self, url: str, name: str, use_selenium: bool = False):
        self.url = url
        self.name = name
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.driver = None
        self.ua = UserAgent()
        self.setup_session()
        self.logger = self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for the scraper"""
        logger = logging.getLogger(f"scraper.{self.name}")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def setup_session(self):
        """Setup requests session with headers"""
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(headers)
    
    def setup_selenium_driver(self, headless: bool = True):
        """Setup Selenium Chrome driver"""
        try:
            options = Options()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument(f'--user-agent={self.ua.random}')
            
            # Use undetected-chromedriver for better anti-bot evasion
            self.driver = uc.Chrome(options=options)
            return True
        except Exception as e:
            self.logger.error(f"Failed to setup Selenium driver: {e}")
            return False
    
    def get_page_content(self, url: str = None) -> Optional[str]:
        """Get page content using requests or selenium"""
        target_url = url or self.url
        
        try:
            if self.use_selenium:
                return self._get_content_selenium(target_url)
            else:
                return self._get_content_requests(target_url)
        except Exception as e:
            self.logger.error(f"Failed to get page content from {target_url}: {e}")
            return None
    
    def _get_content_requests(self, url: str) -> Optional[str]:
        """Get content using requests"""
        try:
            # Random delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"Requests failed for {url}: {e}")
            return None
    
    def _get_content_selenium(self, url: str) -> Optional[str]:
        """Get content using Selenium"""
        try:
            if not self.driver:
                if not self.setup_selenium_driver():
                    return None
            
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Random delay
            time.sleep(random.uniform(2, 4))
            
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Selenium failed for {url}: {e}")
            return None
    
    def parse_html(self, html_content: str) -> Optional[BeautifulSoup]:
        """Parse HTML content with BeautifulSoup"""
        try:
            return BeautifulSoup(html_content, 'lxml')
        except Exception as e:
            self.logger.error(f"Failed to parse HTML: {e}")
            return None
    
    def clean_price_text(self, text: str) -> str:
        """Clean price text by removing common separators and keeping only numbers and dots"""
        if not text:
            return "0"
        
        # Remove common Persian/Arabic numbers and convert to English
        persian_to_english = {
            '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
            '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
            '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
            '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
        }
        
        for persian, english in persian_to_english.items():
            text = text.replace(persian, english)
        
        # Remove common separators and keep only numbers and dots
        text = re.sub(r'[^\d.-]', '', text)
        
        return text.strip()
    
    def extract_number(self, text: str) -> float:
        """Extract number from text"""
        try:
            cleaned = self.clean_price_text(text)
            if not cleaned:
                return 0.0
            return float(cleaned)
        except (ValueError, TypeError):
            self.logger.warning(f"Could not extract number from: {text}")
            return 0.0
    
    def close_driver(self):
        """Close Selenium driver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"Error closing driver: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_driver()
    
    @abstractmethod
    def scrape(self) -> Optional[GoldPriceData]:
        """Abstract method to scrape gold price data"""
        pass
    
    @abstractmethod
    def get_selectors(self) -> Dict[str, str]:
        """Abstract method to return CSS selectors for price and change elements"""
        pass 