from typing import Optional, Dict
import re
from datetime import datetime
from ..base_scraper import BaseScraper, GoldPriceData

class MilliScraper(BaseScraper):
    """Scraper for milli.gold"""
    
    def __init__(self):
        super().__init__(
            url="https://milli.gold/",
            name="milli",
            use_selenium=True  # Milli likely uses JavaScript for dynamic content
        )
    
    def get_selectors(self) -> Dict[str, str]:
        """Return CSS selectors for Milli website elements"""
        return {
            'price': '[class*="price"], [class*="قیمت"], .gold-price, #gold-price',
            'change': '[class*="change"], [class*="تغییر"], .price-change, .change-percent',
            'price_container': '.price-container, .gold-price-container, [class*="price-box"]',
            'price_text': 'span:contains("ریال"), span:contains("تومان"), span:contains("price")'
        }
    
    def scrape(self) -> Optional[GoldPriceData]:
        """Scrape gold price data from Milli"""
        try:
            self.logger.info(f"Starting scrape for {self.name}")
            
            # Get page content
            html_content = self.get_page_content()
            if not html_content:
                return None
            
            soup = self.parse_html(html_content)
            if not soup:
                return None
            
            # Extract price and change data
            price = self._extract_price(soup)
            change_data = self._extract_change(soup)
            
            if price == 0:
                self.logger.warning("Could not extract valid price")
                return None
            
            return GoldPriceData(
                price=price,
                change_24h=change_data.get('change_absolute', 0),
                change_percent=change_data.get('change_percent', 0),
                currency="IRR",
                source=self.name,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Error scraping {self.name}: {e}")
            return None
    
    def _extract_price(self, soup) -> float:
        """Extract current gold price"""
        selectors = self.get_selectors()
        
        # Try multiple approaches to find price
        price_candidates = []
        
        # Method 1: Look for specific price elements
        for selector in selectors['price'].split(', '):
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and any(char.isdigit() for char in text):
                    price_candidates.append(text)
        
        # Method 2: Look for text containing "ریال" or price indicators
        price_elements = soup.find_all(text=re.compile(r'\d+.*ریال|\d+.*تومان|قیمت.*\d+'))
        for text in price_elements:
            if text and any(char.isdigit() for char in str(text)):
                price_candidates.append(str(text))
        
        # Method 3: Look for large numbers (likely prices)
        all_text = soup.get_text()
        price_patterns = [
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*ریال',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*تومان',
            r'قیمت[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'(\d{2,3},\d{3},\d{3})',  # Pattern for large numbers like 86,600,000
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, all_text)
            price_candidates.extend(matches)
        
        # Process candidates and find the most likely price
        for candidate in price_candidates:
            try:
                # Clean and extract number
                cleaned = self.clean_price_text(candidate)
                if cleaned:
                    price = float(cleaned)
                    # Gold prices in Iran are typically in millions
                    if 50000000 <= price <= 200000000:  # Reasonable range for 18k gold price
                        return price
            except (ValueError, TypeError):
                continue
        
        self.logger.warning(f"Could not find valid price in candidates: {price_candidates}")
        return 0.0
    
    def _extract_change(self, soup) -> Dict[str, float]:
        """Extract 24h change data"""
        selectors = self.get_selectors()
        result = {'change_absolute': 0, 'change_percent': 0}
        
        # Look for change elements
        change_candidates = []
        
        # Method 1: CSS selectors
        for selector in selectors['change'].split(', '):
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and ('٪' in text or '%' in text or any(char.isdigit() for char in text)):
                    change_candidates.append(text)
        
        # Method 2: Text patterns
        all_text = soup.get_text()
        change_patterns = [
            r'(\+?-?\d+(?:\.\d+)?)\s*٪',
            r'(\+?-?\d+(?:\.\d+)?)\s*%',
            r'تغییرات[^\d]*(\+?-?\d+(?:\.\d+)?)',
            r'(\+?-?\d+(?:\.\d+)?)\s*درصد',
        ]
        
        for pattern in change_patterns:
            matches = re.findall(pattern, all_text)
            change_candidates.extend(matches)
        
        # Process change candidates
        for candidate in change_candidates:
            try:
                cleaned = self.clean_price_text(candidate)
                if cleaned:
                    change_val = float(cleaned)
                    if -50 <= change_val <= 50:  # Reasonable range for daily change %
                        result['change_percent'] = change_val
                        break
            except (ValueError, TypeError):
                continue
        
        return result 