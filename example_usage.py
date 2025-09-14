#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scrapers.miliGoldScraper import scrape_milli_gold, interpret_price_change
from scrapers.digikalaGoldScraper import digikala_gold_scraper
from scrapers.talappGoldScraper import talapp_gold_scraper
from scrapers.technoGoldScraper import techno_gold_scraper
from scrapers.wallGoldScraper import wall_gold_scraper
from scrapers.melliGoldScraper import melli_gold_scraper
from scrapers.goldikaGoldScraper import goldika_gold_scraper
from scrapers.talaseaScraper import talasea_gold_scraper

def run_gold_scraper(scraper_function, scraper_name):
    """
    General function to run any gold scraper and display results
    
    Args:
        scraper_function: The scraper function to call
        scraper_name: Name of the scraper for display purposes
    """
    print(f"* Using {scraper_name}")
    print("=" * 40)
    
    # Scrape the data
    data = scraper_function()
    
    # Check for errors
    if 'error' in data:
        print(f"❌ Error: {data['error']}")
        return
    
    # Display the results
    print(f"✅ Successfully scraped data from {scraper_name}:")
    print(f"📊 قیمت ۱ گرم طلای ۱۸ عیار: {data['gold_price_18_carat']} {data['currency']}")
    print(f"📈 تغییرات: {data['price_change']}")
    
    # Interpret the price change
    change_interpretation = interpret_price_change(data['price_change'])
    print(f"🔍 تفسیر تغییرات: {change_interpretation}")
    
    # You can also access individual values
    price = data['gold_price_18_carat']
    change = data['price_change']
    
    print(f"\n💰 Current gold price: {price} Rial")
    print(f"📊 Price change: {change}")
    
    # Show trend
    if change and change.startswith('-'):
        print("📉 Trend: Decreasing (Bearish)")
    elif change and (change.startswith('+') or not change.startswith('-')):
        print("📈 Trend: Increasing (Bullish)")
    else:
        print("❓ Trend: Unknown")

def main():
    print("Gold Arbitrage Scraper Examples")
    print()
    
    # Define scrapers to run
    scrapers = [
        (scrape_milli_gold, "Milli Gold Scraper"),
        (digikala_gold_scraper, "Digikala Gold Scraper"),
        (talapp_gold_scraper, "Talapp Gold Scraper"),
        (techno_gold_scraper, "Techno Gold Scraper"),
        (wall_gold_scraper, "Wall Gold Scraper"),
        (melli_gold_scraper, "Melli Gold Scraper"),
        (goldika_gold_scraper, "Goldika Gold Scraper"),
        (talasea_gold_scraper, "Talasea Gold Scraper")
    ]
    
    # Run each scraper
    for scraper_function, scraper_name in scrapers:
        run_gold_scraper(scraper_function, scraper_name)
        print()

if __name__ == "__main__":
    main() 