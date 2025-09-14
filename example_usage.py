#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scrapers.miliGoldScraper import scrape_milli_gold, interpret_price_change

def SampleMiliGold():
    """Example usage of the Milli Gold scraper"""
    print("Example: Using Milli Gold Scraper")
    print("=" * 40)
    
    # Scrape the data
    data = scrape_milli_gold()
    
    # Check for errors
    if 'error' in data:
        print(f"❌ Error: {data['error']}")
        return
    
    # Display the results
    print("✅ Successfully scraped data from Milli Gold:")
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
    SampleMiliGold()

if __name__ == "__main__":
    main() 