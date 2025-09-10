#!/usr/bin/env python3
"""
Test script for Gold Arbitrage Scraper
Demonstrates basic functionality and tests individual scrapers
"""

import sys
from pathlib import Path
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.gold_scraper import GoldArbitrageScraper
from src.scrapers.milli_scraper import MilliScraper

def test_individual_scraper():
    """Test a single scraper"""
    print("🧪 Testing individual scraper (Milli)...")
    
    try:
        with MilliScraper() as scraper:
            print(f"Scraper URL: {scraper.url}")
            print(f"Scraper name: {scraper.name}")
            print(f"Uses Selenium: {scraper.use_selenium}")
            
            # Test selectors
            selectors = scraper.get_selectors()
            print(f"Available selectors: {list(selectors.keys())}")
            
            # Test scraping
            print("Attempting to scrape...")
            data = scraper.scrape()
            
            if data:
                print("✅ Scraping successful!")
                print(f"Price: {data.price:,.0f} {data.currency}")
                print(f"24h Change: {data.change_percent}%")
                print(f"Source: {data.source}")
                print(f"Timestamp: {data.timestamp}")
            else:
                print("❌ No data returned")
                
    except Exception as e:
        print(f"❌ Error testing individual scraper: {e}")

def test_main_scraper():
    """Test the main orchestrator"""
    print("\n🧪 Testing main scraper orchestrator...")
    
    try:
        scraper = GoldArbitrageScraper(max_workers=3)
        
        # List available scrapers
        available = scraper.get_available_scrapers()
        print(f"Available scrapers: {len(available)}")
        for name in available:
            print(f"  - {name}")
        
        # Test scraping a few sites
        print("\nTesting scraping of 2-3 sites...")
        test_sites = ['milli', 'talasea']  # Start with just a couple
        
        results = scraper.scrape_specific_sites(test_sites)
        
        if results:
            print(f"✅ Successfully scraped {len(results)} sites")
            for source, data in results.items():
                print(f"  {source}: {data.get('price', 0):,.0f} IRR ({data.get('change_percent', 0):+.2f}%)")
            
            # Test arbitrage analysis
            if len(results) >= 2:
                print("\nTesting arbitrage analysis...")
                analysis = scraper.analyze_arbitrage_opportunities(results)
                
                if 'error' not in analysis:
                    print(f"Price difference: {analysis['percentage_difference']:.2f}%")
                    print(f"Arbitrage opportunity: {analysis['arbitrage_opportunity']}")
                else:
                    print(f"Analysis error: {analysis['error']}")
        else:
            print("❌ No sites could be scraped")
            
    except Exception as e:
        print(f"❌ Error testing main scraper: {e}")

def test_data_structure():
    """Test data structure and validation"""
    print("\n🧪 Testing data structure...")
    
    from src.base_scraper import GoldPriceData
    
    # Test valid data
    valid_data = GoldPriceData(
        price=86600000,
        change_24h=500000,
        change_percent=0.77,
        currency="IRR",
        source="test",
        timestamp="2024-01-01T12:00:00"
    )
    
    data_dict = valid_data.to_dict()
    print("✅ Valid data structure created:")
    for key, value in data_dict.items():
        print(f"  {key}: {value}")

def main():
    """Run all tests"""
    print("🚀 Starting Gold Arbitrage Scraper Tests")
    print("=" * 50)
    
    # Enable logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Test 1: Data structure
    test_data_structure()
    
    # Test 2: Individual scraper
    test_individual_scraper()
    
    # Test 3: Main orchestrator
    test_main_scraper()
    
    print("\n" + "=" * 50)
    print("🎯 Test complete!")
    print("\nTo run the full scraper:")
    print("  python main.py")
    print("\nTo see all options:")
    print("  python main.py --help")

if __name__ == "__main__":
    main() 