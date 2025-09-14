import requests
from bs4 import BeautifulSoup
import re

def scrape_talasea():
    """
    Scrape gold price and price changes from Talasea website
    Returns a dictionary with the scraped data
    """
    url = "https://talasea.ir/"
    
    try:
        # Send GET request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Initialize result dictionary
        result = {
            'gold_price_18_carat': None,
            'price_change': None,
            'currency': 'ریال',
            'unit': '۱ گرم'
        }
        
        # Look for gold price - try different possible selectors
        # The price is likely in a div or span with specific classes or containing the price text
        
        # Method 1: Look for text containing "قیمت" and "طلا" and "۱۸ عیار"
        price_elements = soup.find_all(string=re.compile(r'قیمت.*طلا.*۱۸.*عیار|طلا.*۱۸.*عیار.*قیمت'))
        if price_elements:
            # Find the parent element and look for price nearby
            for element in price_elements:
                parent = element.parent
                # Look for price patterns in nearby elements
                siblings = parent.find_next_siblings()
                for sibling in siblings:
                    price_match = re.search(r'([\d,]+,\d+)', sibling.get_text())
                    if price_match:
                        result['gold_price_18_carat'] = price_match.group(1)
                        break
        
        # Method 2: Look for large numbers that could be prices (in Rial format)
        if not result['gold_price_18_carat']:
            # Look for patterns like "86,610,000" followed by "ریال" or "تومان"
            price_pattern = re.compile(r'([\d,]+,\d+).*?(?:ریال|تومان)')
            price_matches = soup.find_all(string=price_pattern)
            for match in price_matches:
                price_search = price_pattern.search(match)
                if price_search:
                    result['gold_price_18_carat'] = price_search.group(1)
                    break
        
        # Method 3: Look for price in specific HTML structure (common for trading platforms)
        if not result['gold_price_18_carat']:
            # Look for price in table cells, divs with price classes, or specific data attributes
            price_selectors = [
                'td.price', 'span.price', 'div.price', '.gold-price', 
                '[data-price]', '.price-value', '.current-price'
            ]
            for selector in price_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    # Look for 7-9 digit numbers (typical for gold prices in Rial)
                    price_match = re.search(r'(\d{1,3}(?:,\d{3})+)', text)
                    if price_match:
                        result['gold_price_18_carat'] = price_match.group(1)
                        break
                if result['gold_price_18_carat']:
                    break
        
        # Method 4: Look in divs/spans that might contain price data
        if not result['gold_price_18_carat']:
            for element in soup.find_all(['div', 'span', 'p', 'td']):
                text = element.get_text().strip()
                # Look for 7-9 digit numbers (typical for gold prices in Rial)
                price_match = re.search(r'(\d{2,3},\d{3},\d{3})', text)
                if price_match:
                    # Additional validation - check if this looks like a gold price
                    price_value = int(price_match.group(1).replace(',', ''))
                    if 50000000 <= price_value <= 200000000:  # Reasonable range for gold price in Rial
                        result['gold_price_18_carat'] = price_match.group(1)
                        break
        
        # Look for price changes - likely contains percentage with "%" or "تغییرات"
        change_elements = soup.find_all(string=re.compile(r'تغییرات|تغییر|رشد|کاهش'))
        if change_elements:
            for element in change_elements:
                parent = element.parent
                # Look for percentage in nearby elements
                siblings = parent.find_next_siblings()
                for sibling in siblings:
                    # Updated regex to capture positive/negative signs
                    change_match = re.search(r'([+-]?\d+\.?\d*%)', sibling.get_text())
                    if change_match:
                        result['price_change'] = change_match.group(1)
                        break
        
        # Alternative method for price changes
        if not result['price_change']:
            # Look for percentage patterns with signs
            for element in soup.find_all(['div', 'span', 'p', 'td']):
                text = element.get_text().strip()
                # Look for patterns like "+1.47%", "-2.35%", "1.47%" (positive assumed)
                change_match = re.search(r'([+-]?\d+\.?\d*%)', text)
                if change_match:
                    result['price_change'] = change_match.group(1)
                    break
        
        # Method 3: Look for price change in specific selectors
        if not result['price_change']:
            change_selectors = [
                '.change', '.price-change', '.percentage', '.percent',
                '[data-change]', '.change-value', '.variation'
            ]
            for selector in change_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    change_match = re.search(r'([+-]?\d+\.?\d*%)', text)
                    if change_match:
                        result['price_change'] = change_match.group(1)
                        break
                if result['price_change']:
                    break
        
        # If we found a percentage without explicit sign, check surrounding context for indicators
        if result['price_change'] and not result['price_change'].startswith(('+', '-')):
            # Look for green/red indicators or positive/negative keywords in the HTML
            for element in soup.find_all(['div', 'span', 'p', 'td']):
                text = element.get_text().strip()
                if result['price_change'].replace('%', '') in text:
                    # Check for color classes or text indicators
                    classes = ' '.join(element.get('class', []))
                    style = element.get('style', '')
                    
                    # Common patterns for positive/negative indicators
                    if any(indicator in classes.lower() for indicator in ['green', 'positive', 'up', 'increase', 'rise']):
                        result['price_change'] = '+' + result['price_change']
                        break
                    elif any(indicator in classes.lower() for indicator in ['red', 'negative', 'down', 'decrease', 'fall']):
                        result['price_change'] = '-' + result['price_change']
                        break
                    elif 'color: green' in style.lower() or 'color:#green' in style.lower():
                        result['price_change'] = '+' + result['price_change']
                        break
                    elif 'color: red' in style.lower() or 'color:#red' in style.lower():
                        result['price_change'] = '-' + result['price_change']
                        break
        
        return result
        
    except requests.RequestException as e:
        return {'error': f'Network error: {str(e)}'}
    except Exception as e:
        return {'error': f'Parsing error: {str(e)}'}

def interpret_price_change(change_str):
    """
    Interpret the price change string and return a descriptive message
    """
    if not change_str:
        return "تغییرات نامشخص"
    
    if change_str.startswith('+'):
        return f"📈 افزایش {change_str[1:]} (مثبت)"
    elif change_str.startswith('-'):
        return f"📉 کاهش {change_str[1:]} (منفی)"
    else:
        # If no sign, assume positive (common convention)
        return f"📈 تغییر {change_str} (احتمالاً مثبت)"

def main():
    """Main function to run the scraper"""
    print("Scraping Talasea website...")
    print("=" * 50)
    
    data = scrape_talasea()
    
    if 'error' in data:
        print(f"Error occurred: {data['error']}")
        return
    
    print(f"قیمت ۱ گرم طلای ۱۸ عیار: {data['gold_price_18_carat']} {data['currency']}")
    print(f"تغییرات: {data['price_change']}")
    
    # Show interpreted change
    change_interpretation = interpret_price_change(data['price_change'])
    print(f"تفسیر تغییرات: {change_interpretation}")
    
    return data

if __name__ == "__main__":
    main() 