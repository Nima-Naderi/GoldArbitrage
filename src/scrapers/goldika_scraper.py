from typing import Optional, Dict
import re
from datetime import datetime
from ..base_scraper import BaseScraper, GoldPriceData

class GoldikaScraper(BaseScraper):
    """Scraper for goldika.ir"""
    
    def __init__(self):
        super().__init__(
            url="https://goldika.ir/",
            name="goldika",
            use_selenium=True
        )
    
    def get_selectors(self) -> Dict[str, str]:
        """Return CSS selectors for Goldika website elements"""
        return {
            'price': '.price, .gold-price, [class*="price"], [class*="قیمت"], .current-price',
            'change': '.change, .price-change, [class*="change"], [class*="تغییر"], .price-diff',
            'price_container': '.price-container, .gold-info, .price-box, .market-data',
            'currency': 'span:contains("ریال"), span:contains("تومان")'
        }
    
    def scrape(self) -> Optional[GoldPriceData]:
        """Scrape gold price data from Goldika"""
        try:
            self.logger.info(f"Starting scrape for {self.name}")
            
            html_content = self.get_page_content()
            if not html_content:
                return None
            
            soup = self.parse_html(html_content)
            if not soup:
                return None
            
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
        price_candidates = []
        
        for selector in selectors['price'].split(', '):
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and any(char.isdigit() for char in text):
                    price_candidates.append(text)
        
        all_text = soup.get_text()
        price_patterns = [
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*ریال',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*تومان',
            r'قیمت[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'طلا[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'(\d{8,})',  # Large numbers
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, all_text)
            price_candidates.extend(matches)
        
        for candidate in price_candidates:
            try:
                cleaned = self.clean_price_text(candidate)
                if cleaned:
                    price = float(cleaned)
                    if 50000000 <= price <= 200000000:
                        return price
            except (ValueError, TypeError):
                continue
        
        return 0.0
    
    def _extract_change(self, soup) -> Dict[str, float]:
        """Extract 24h change data"""
        selectors = self.get_selectors()
        result = {'change_absolute': 0, 'change_percent': 0}
        
        change_candidates = []
        
        for selector in selectors['change'].split(', '):
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and ('٪' in text or '%' in text or any(char.isdigit() for char in text)):
                    change_candidates.append(text)
        
        all_text = soup.get_text()
        change_patterns = [
            r'(\+?-?\d+(?:\.\d+)?)\s*٪',
            r'(\+?-?\d+(?:\.\d+)?)\s*%',
            r'تغییر[^\d]*(\+?-?\d+(?:\.\d+)?)',
            r'درصد[^\d]*(\+?-?\d+(?:\.\d+)?)',
        ]
        
        for pattern in change_patterns:
            matches = re.findall(pattern, all_text)
            change_candidates.extend(matches)
        
        for candidate in change_candidates:
            try:
                cleaned = self.clean_price_text(candidate)
                if cleaned:
                    change_val = float(cleaned)
                    if -50 <= change_val <= 50:
                        result['change_percent'] = change_val
                        break
            except (ValueError, TypeError):
                continue
        
        return result 