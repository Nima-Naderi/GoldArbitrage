#!/usr/bin/env python3
"""
Example Usage Script for Gold Arbitrage Scraper
Simple demonstration of how to use the scraper
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.gold_scraper import GoldArbitrageScraper

def simple_demo():
    """Simple demonstration of the scraper"""
    print("🏅 Gold Arbitrage Scraper Demo")
    print("=" * 40)
    
    # Initialize the scraper
    scraper = GoldArbitrageScraper(max_workers=3)
    
    # Show available scrapers
    print(f"📊 Available scrapers: {len(scraper.get_available_scrapers())}")
    for name in scraper.get_available_scrapers():
        print(f"   • {name}")
    
    print("\n💡 To run the scraper:")
    print("   python3 main.py                    # Scrape all sites")
    print("   python3 main.py --sites milli      # Scrape specific site")
    print("   python3 main.py --save             # Save results to files")
    print("   python3 main.py --json             # JSON output")
    
    print("\n📝 Example data structure:")
    example_data = {
        "price": 86600000,
        "change_24h": 500000,
        "change_percent": 0.77,
        "currency": "IRR",
        "source": "milli",
        "timestamp": "2024-01-01T12:00:00"
    }
    
    for key, value in example_data.items():
        print(f"   {key}: {value}")
    
    print("\n🚀 Ready to scrape Iranian gold prices!")
    print("   Note: Web scraping may take 30-60 seconds")

if __name__ == "__main__":
    simple_demo() 