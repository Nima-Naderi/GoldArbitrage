#!/usr/bin/env python3
"""
Gold Arbitrage Scraper - Main Interface
Scrapes gold prices from multiple Iranian gold trading websites
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.gold_scraper import GoldArbitrageScraper

def print_results(results):
    """Pretty print the scraping results"""
    print("\n" + "="*60)
    print("GOLD PRICE SCRAPING RESULTS")
    print("="*60)
    
    if "scraping_results" in results:
        scraping_results = results["scraping_results"]
        
        if not scraping_results:
            print("❌ No data could be scraped from any source")
            return
        
        print(f"\n📊 Successfully scraped {len(scraping_results)} sources:")
        print("-" * 60)
        
        for source, data in scraping_results.items():
            price = data.get('price', 0)
            change_percent = data.get('change_percent', 0)
            change_symbol = "📈" if change_percent > 0 else "📉" if change_percent < 0 else "➡️"
            
            print(f"🏪 {source.upper():<12}: {price:>12,.0f} IRR  {change_symbol} {change_percent:>5.2f}%")
        
        # Arbitrage analysis
        if "arbitrage_analysis" in results and "error" not in results["arbitrage_analysis"]:
            analysis = results["arbitrage_analysis"]
            print("\n" + "="*60)
            print("ARBITRAGE ANALYSIS")
            print("="*60)
            
            lowest = analysis['lowest_price']
            highest = analysis['highest_price']
            
            print(f"🏆 Lowest Price:  {lowest['source']:<12} - {lowest['price']:>12,.0f} IRR")
            print(f"💰 Highest Price: {highest['source']:<12} - {highest['price']:>12,.0f} IRR")
            print(f"📈 Price Difference: {analysis['price_difference']:>12,.0f} IRR")
            print(f"📊 Percentage Diff:  {analysis['percentage_difference']:>11.2f}%")
            
            if analysis['arbitrage_opportunity']:
                print(f"\n🚀 ARBITRAGE OPPORTUNITY DETECTED! ({analysis['percentage_difference']:.2f}% difference)")
                print(f"💡 Buy from {lowest['source']} and sell to {highest['source']}")
            else:
                print(f"\n😐 No significant arbitrage opportunity (difference < 1%)")
        
        # Summary
        if "summary" in results:
            summary = results["summary"]
            print("\n" + "="*60)
            print("SCRAPING SUMMARY")
            print("="*60)
            print(f"🎯 Total Attempted:    {summary['total_attempted']}")
            print(f"✅ Successful Scrapes: {summary['successful_scrapes']}")
            print(f"❌ Failed Scrapes:     {summary['failed_scrapes']}")
            print(f"🕐 Analysis Time:      {summary['analysis_timestamp']}")
    
    else:
        # Simple results format
        if not results:
            print("❌ No data could be scraped from any source")
            return
        
        for source, data in results.items():
            price = data.get('price', 0)
            change_percent = data.get('change_percent', 0)
            change_symbol = "📈" if change_percent > 0 else "📉" if change_percent < 0 else "➡️"
            
            print(f"🏪 {source.upper():<12}: {price:>12,.0f} IRR  {change_symbol} {change_percent:>5.2f}%")

def main():
    parser = argparse.ArgumentParser(description='Gold Arbitrage Scraper')
    parser.add_argument('--sites', nargs='+', help='Specific sites to scrape')
    parser.add_argument('--list', action='store_true', help='List available scrapers')
    parser.add_argument('--save', action='store_true', help='Save results to files')
    parser.add_argument('--output', help='Output filename prefix')
    parser.add_argument('--workers', type=int, default=5, help='Number of concurrent workers')
    parser.add_argument('--timeout', type=int, default=60, help='Timeout for scraping operations')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = GoldArbitrageScraper(max_workers=args.workers)
    
    # List available scrapers
    if args.list:
        available = scraper.get_available_scrapers()
        print("Available scrapers:")
        for name in available:
            print(f"  - {name}")
        return
    
    try:
        # Scrape specific sites or all sites
        if args.sites:
            print(f"Scraping specific sites: {', '.join(args.sites)}")
            results = scraper.scrape_specific_sites(args.sites)
            
            if args.save and results:
                filename = args.output or f"gold_prices_selected"
                scraper.save_results(results, filename)
        else:
            print("Scraping all available gold price websites...")
            results = scraper.run_complete_analysis(save_results=args.save)
        
        # Output results
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print_results(results)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 