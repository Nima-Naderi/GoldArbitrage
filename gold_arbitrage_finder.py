#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Import all scrapers
from scrapers.miliGoldScraper import scrape_milli_gold, interpret_price_change
from scrapers.digikalaGoldScraper import digikala_gold_scraper
from scrapers.talappGoldScraper import talapp_gold_scraper
from scrapers.technoGoldScraper import techno_gold_scraper
from scrapers.wallGoldScraper import wall_gold_scraper
from scrapers.melliGoldScraper import melli_gold_scraper
from scrapers.goldikaGoldScraper import goldika_gold_scraper
from scrapers.talaseaScraper import talasea_gold_scraper

# Import utility functions
from utils.price_converters import convert_persian_to_english_digits, remove_comma, format_number_with_commas


@dataclass
class GoldPrice:
    """Data class to represent gold price information"""
    source: str
    price: float
    currency: str
    price_change: str
    timestamp: datetime
    raw_data: Dict


@dataclass
class ArbitrageOpportunity:
    """Data class to represent an arbitrage opportunity"""
    buy_source: str
    sell_source: str
    buy_price: float
    sell_price: float
    profit_per_gram: float
    profit_percentage: float
    timestamp: datetime


class GoldArbitrageFinder:
    """Main class for finding gold arbitrage opportunities"""
    
    def __init__(self):
        self.scrapers = {
            "Milli Gold": scrape_milli_gold,
            "Digikala": digikala_gold_scraper,
            "Talapp": talapp_gold_scraper,
            "Techno": techno_gold_scraper,
            "Wall": wall_gold_scraper,
            "Melli": melli_gold_scraper,
            "Goldika": goldika_gold_scraper,
            "Talasea": talasea_gold_scraper
        }
        self.prices: List[GoldPrice] = []
        self.arbitrage_opportunities: List[ArbitrageOpportunity] = []
    
    def normalize_price(self, price_str: str) -> float:
        """
        Normalize price string to float value
        
        Args:
            price_str: Price as string (may contain Persian digits, commas, etc.)
            
        Returns:
            float: Normalized price value
        """
        try:
            # Convert Persian digits to English
            normalized = convert_persian_to_english_digits(price_str)
            
            # Remove commas and other formatting
            normalized = remove_comma(normalized)
            
            # Remove any non-numeric characters except decimal point
            import re
            normalized = re.sub(r'[^\d.]', '', normalized)
            
            # Convert to float
            return float(normalized)
        except (ValueError, TypeError):
            return 0.0
    
    def scrape_all_sources(self) -> List[GoldPrice]:
        """
        Scrape gold prices from all available sources
        
        Returns:
            List[GoldPrice]: List of gold prices from all sources
        """
        print("🔍 Starting to scrape gold prices from all sources...")
        print("=" * 60)
        
        prices = []
        current_time = datetime.now()
        
        for source_name, scraper_func in self.scrapers.items():
            try:
                print(f"📊 Scraping {source_name}...")
                
                # Scrape the data
                data = scraper_func()
                
                # Check for errors
                if 'error' in data:
                    print(f"❌ {source_name}: {data['error']}")
                    continue
                
                # Normalize the price
                normalized_price = self.normalize_price(data['gold_price_18_carat'])
                
                if normalized_price > 0:
                    gold_price = GoldPrice(
                        source=source_name,
                        price=normalized_price,
                        currency=data.get('currency', 'Rial'),
                        price_change=data.get('price_change', ''),
                        timestamp=current_time,
                        raw_data=data
                    )
                    prices.append(gold_price)
                    print(f"✅ {source_name}: {format_number_with_commas(str(int(normalized_price)))} {data.get('currency', 'Rial')}")
                else:
                    print(f"⚠️  {source_name}: Could not parse price")
                
                # Small delay to be respectful to websites
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ {source_name}: Error - {str(e)}")
                continue
        
        self.prices = prices
        print(f"\n📈 Successfully scraped {len(prices)} sources")
        return prices
    
    def find_arbitrage_opportunities(self, min_profit_percentage: float = 0.5) -> List[ArbitrageOpportunity]:
        """
        Find arbitrage opportunities between different sources
        
        Args:
            min_profit_percentage: Minimum profit percentage to consider an opportunity
            
        Returns:
            List[ArbitrageOpportunity]: List of arbitrage opportunities
        """
        if len(self.prices) < 2:
            print("⚠️  Need at least 2 price sources to find arbitrage opportunities")
            return []
        
        print(f"\n🔍 Analyzing arbitrage opportunities (min profit: {min_profit_percentage}%)...")
        print("=" * 60)
        
        opportunities = []
        
        # Compare all pairs of sources
        for i, buy_price in enumerate(self.prices):
            for j, sell_price in enumerate(self.prices):
                if i != j:  # Don't compare source with itself
                    
                    # Calculate profit (sell high, buy low)
                    profit_per_gram = sell_price.price - buy_price.price
                    profit_percentage = (profit_per_gram / buy_price.price) * 100
                    
                    # Only consider opportunities with minimum profit
                    if profit_percentage >= min_profit_percentage:
                        opportunity = ArbitrageOpportunity(
                            buy_source=buy_price.source,
                            sell_source=sell_price.source,
                            buy_price=buy_price.price,
                            sell_price=sell_price.price,
                            profit_per_gram=profit_per_gram,
                            profit_percentage=profit_percentage,
                            timestamp=datetime.now()
                        )
                        opportunities.append(opportunity)
        
        # Sort by profit percentage (highest first)
        opportunities.sort(key=lambda x: x.profit_percentage, reverse=True)
        
        self.arbitrage_opportunities = opportunities
        return opportunities
    
    def print_arbitrage_report(self):
        """Print a comprehensive arbitrage report"""
        if not self.arbitrage_opportunities:
            print("\n❌ No arbitrage opportunities found with the current criteria")
            return
        
        print(f"\n💰 ARBITRAGE OPPORTUNITIES REPORT")
        print("=" * 60)
        print(f"📅 Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Total opportunities found: {len(self.arbitrage_opportunities)}")
        print()
        
        # Top 5 opportunities
        print("🏆 TOP 5 ARBITRAGE OPPORTUNITIES:")
        print("-" * 60)
        
        for i, opp in enumerate(self.arbitrage_opportunities[:5], 1):
            print(f"{i}. BUY from {opp.buy_source} → SELL to {opp.sell_source}")
            print(f"   💵 Buy Price:  {format_number_with_commas(str(int(opp.buy_price)))} Rial")
            print(f"   💰 Sell Price: {format_number_with_commas(str(int(opp.sell_price)))} Rial")
            print(f"   📈 Profit:     {format_number_with_commas(str(int(opp.profit_per_gram)))} Rial per gram")
            print(f"   📊 ROI:        {opp.profit_percentage:.2f}%")
            print()
        
        # Summary statistics
        if self.arbitrage_opportunities:
            max_profit = max(opp.profit_percentage for opp in self.arbitrage_opportunities)
            avg_profit = sum(opp.profit_percentage for opp in self.arbitrage_opportunities) / len(self.arbitrage_opportunities)
            
            print("📊 SUMMARY STATISTICS:")
            print("-" * 60)
            print(f"🎯 Maximum profit opportunity: {max_profit:.2f}%")
            print(f"📊 Average profit opportunity: {avg_profit:.2f}%")
            print(f"🔢 Total opportunities: {len(self.arbitrage_opportunities)}")
    
    def print_price_summary(self):
        """Print a summary of all scraped prices"""
        if not self.prices:
            print("❌ No prices available")
            return
        
        print(f"\n📊 GOLD PRICE SUMMARY")
        print("=" * 60)
        print(f"📅 Scraped at: {self.prices[0].timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Sort prices by value
        sorted_prices = sorted(self.prices, key=lambda x: x.price)
        
        print("💰 PRICES BY SOURCE (Lowest to Highest):")
        print("-" * 60)
        
        for price in sorted_prices:
            print(f"🏪 {price.source:<12}: {format_number_with_commas(str(int(price.price))):>12} Rial")
            if price.price_change:
                print(f"   📈 Change: {price.price_change}")
        
        # Price range analysis
        if len(sorted_prices) > 1:
            lowest = sorted_prices[0]
            highest = sorted_prices[-1]
            price_range = highest.price - lowest.price
            range_percentage = (price_range / lowest.price) * 100
            
            print(f"\n📊 PRICE RANGE ANALYSIS:")
            print("-" * 60)
            print(f"🔻 Lowest:  {format_number_with_commas(str(int(lowest.price)))} Rial ({lowest.source})")
            print(f"🔺 Highest: {format_number_with_commas(str(int(highest.price)))} Rial ({highest.source})")
            print(f"📏 Range:   {format_number_with_commas(str(int(price_range)))} Rial ({range_percentage:.2f}%)")
    
    def save_results_to_file(self, filename: str = None, results_folder: str = "arbitrage_results"):
        """Save results to a JSON file in a specific folder"""
        import os
        
        # Create results folder if it doesn't exist
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
            print(f"📁 Created results folder: {results_folder}")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"arbitrage_results_{timestamp}.json"
        
        # Create full file path
        file_path = os.path.join(results_folder, filename)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "prices": [
                {
                    "source": price.source,
                    "price": price.price,
                    "currency": price.currency,
                    "price_change": price.price_change,
                    "timestamp": price.timestamp.isoformat()
                }
                for price in self.prices
            ],
            "arbitrage_opportunities": [
                {
                    "buy_source": opp.buy_source,
                    "sell_source": opp.sell_source,
                    "buy_price": opp.buy_price,
                    "sell_price": opp.sell_price,
                    "profit_per_gram": opp.profit_per_gram,
                    "profit_percentage": opp.profit_percentage,
                    "timestamp": opp.timestamp.isoformat()
                }
                for opp in self.arbitrage_opportunities
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {file_path}")
    
    def run_full_analysis(self, min_profit_percentage: float = 0.5, save_results: bool = True, results_folder: str = "arbitrage_results"):
        """
        Run the complete arbitrage analysis
        
        Args:
            min_profit_percentage: Minimum profit percentage to consider
            save_results: Whether to save results to file
            results_folder: Folder to save results in
        """
        print("🚀 GOLD ARBITRAGE FINDER")
        print("=" * 60)
        print("Starting comprehensive gold price analysis...")
        print()
        
        # Step 1: Scrape all sources
        self.scrape_all_sources()
        
        if not self.prices:
            print("❌ No prices could be scraped. Exiting.")
            return
        
        # Step 2: Print price summary
        self.print_price_summary()
        
        # Step 3: Find arbitrage opportunities
        self.find_arbitrage_opportunities(min_profit_percentage)
        
        # Step 4: Print arbitrage report
        self.print_arbitrage_report()
        
        # Step 5: Save results if requested
        if save_results:
            self.save_results_to_file(results_folder=results_folder)
        
        print(f"\n✅ Analysis complete! Found {len(self.arbitrage_opportunities)} arbitrage opportunities.")


def main():
    """Main function to run the arbitrage finder"""
    finder = GoldArbitrageFinder()
    
    # You can adjust the minimum profit percentage here
    # 0.5% means we only show opportunities with at least 0.5% profit
    min_profit = 0.5
    
    # Customize the results folder name
    results_folder = "arbitrage_results"
    
    finder.run_full_analysis(
        min_profit_percentage=min_profit, 
        save_results=True, 
        results_folder=results_folder
    )


if __name__ == "__main__":
    main()
