import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from datetime import datetime
import json

from .scrapers.milli_scraper import MilliScraper
from .scrapers.talasea_scraper import TalaseaScraper
from .scrapers.goldika_scraper import GoldikaScraper
from .scrapers.melligold_scraper import MelligoldScraper
from .scrapers.wallgold_scraper import WallgoldScraper
from .scrapers.technogold_scraper import TechnogoldScraper
from .scrapers.daric_scraper import DaricScraper
from .scrapers.talapp_scraper import TalappScraper
from .scrapers.digikala_scraper import DigikalaScraper
from .base_scraper import GoldPriceData

class GoldArbitrageScraper:
    """Main orchestrator for gold price scraping across multiple websites"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.scrapers = self._initialize_scrapers()
        self.logger = self._setup_logging()
    
    def _setup_logging(self):
        """Setup main logging"""
        logger = logging.getLogger("gold_arbitrage")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _initialize_scrapers(self) -> List:
        """Initialize all scraper instances"""
        scrapers = [
            MilliScraper(),
            TalaseaScraper(),
            GoldikaScraper(),
            MelligoldScraper(),
            WallgoldScraper(),
            TechnogoldScraper(),
            DaricScraper(),
            TalappScraper(),
            DigikalaScraper()
        ]
        return scrapers
    
    def scrape_single_site(self, scraper) -> Optional[Dict]:
        """Scrape a single website and return the result"""
        try:
            self.logger.info(f"Starting scrape for {scraper.name}")
            with scraper:
                data = scraper.scrape()
                if data:
                    return data.to_dict()
                else:
                    self.logger.warning(f"No data returned from {scraper.name}")
                    return None
        except Exception as e:
            self.logger.error(f"Error scraping {scraper.name}: {e}")
            return None
    
    def scrape_all_sites(self, timeout: int = 60) -> Dict[str, Dict]:
        """Scrape all websites concurrently"""
        self.logger.info("Starting concurrent scraping of all gold price websites")
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scraping tasks
            future_to_scraper = {
                executor.submit(self.scrape_single_site, scraper): scraper 
                for scraper in self.scrapers
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_scraper, timeout=timeout):
                scraper = future_to_scraper[future]
                try:
                    result = future.result()
                    if result:
                        results[scraper.name] = result
                        self.logger.info(f"Successfully scraped {scraper.name}")
                    else:
                        self.logger.warning(f"Failed to scrape {scraper.name}")
                except Exception as e:
                    self.logger.error(f"Exception occurred while scraping {scraper.name}: {e}")
        
        return results
    
    def scrape_specific_sites(self, site_names: List[str]) -> Dict[str, Dict]:
        """Scrape specific websites by name"""
        selected_scrapers = [s for s in self.scrapers if s.name in site_names]
        
        if not selected_scrapers:
            self.logger.warning(f"No scrapers found for sites: {site_names}")
            return {}
        
        self.logger.info(f"Scraping specific sites: {[s.name for s in selected_scrapers]}")
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(selected_scrapers)) as executor:
            future_to_scraper = {
                executor.submit(self.scrape_single_site, scraper): scraper 
                for scraper in selected_scrapers
            }
            
            for future in as_completed(future_to_scraper):
                scraper = future_to_scraper[future]
                try:
                    result = future.result()
                    if result:
                        results[scraper.name] = result
                except Exception as e:
                    self.logger.error(f"Exception occurred while scraping {scraper.name}: {e}")
        
        return results
    
    def analyze_arbitrage_opportunities(self, results: Dict[str, Dict]) -> Dict:
        """Analyze price differences to find arbitrage opportunities"""
        if len(results) < 2:
            return {"error": "Need at least 2 sources for arbitrage analysis"}
        
        prices = {}
        for source, data in results.items():
            if 'price' in data and data['price'] > 0:
                prices[source] = data['price']
        
        if len(prices) < 2:
            return {"error": "Need at least 2 valid prices for arbitrage analysis"}
        
        # Find min and max prices
        min_price_source = min(prices.keys(), key=lambda k: prices[k])
        max_price_source = max(prices.keys(), key=lambda k: prices[k])
        
        min_price = prices[min_price_source]
        max_price = prices[max_price_source]
        
        price_diff = max_price - min_price
        percentage_diff = (price_diff / min_price) * 100
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_sources": len(results),
            "valid_prices": len(prices),
            "lowest_price": {
                "source": min_price_source,
                "price": min_price
            },
            "highest_price": {
                "source": max_price_source,
                "price": max_price
            },
            "price_difference": price_diff,
            "percentage_difference": round(percentage_diff, 2),
            "arbitrage_opportunity": percentage_diff > 1.0,  # Consider >1% as opportunity
            "all_prices": prices
        }
        
        return analysis
    
    def save_results(self, results: Dict[str, Dict], filename: str = None):
        """Save results to JSON and CSV files"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gold_prices_{timestamp}"
        
        # Save as JSON
        json_filename = f"{filename}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Save as CSV
        csv_filename = f"{filename}.csv"
        df_data = []
        for source, data in results.items():
            row = {
                'source': source,
                'price': data.get('price', 0),
                'change_24h': data.get('change_24h', 0),
                'change_percent': data.get('change_percent', 0),
                'currency': data.get('currency', 'IRR'),
                'timestamp': data.get('timestamp', '')
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        self.logger.info(f"Results saved to {json_filename} and {csv_filename}")
        return json_filename, csv_filename
    
    def get_available_scrapers(self) -> List[str]:
        """Get list of available scraper names"""
        return [scraper.name for scraper in self.scrapers]
    
    def run_complete_analysis(self, save_results: bool = True) -> Dict:
        """Run complete scraping and analysis pipeline"""
        self.logger.info("Starting complete gold arbitrage analysis")
        
        # Scrape all sites
        scraping_results = self.scrape_all_sites()
        
        if not scraping_results:
            return {"error": "No data could be scraped from any source"}
        
        # Analyze arbitrage opportunities
        arbitrage_analysis = self.analyze_arbitrage_opportunities(scraping_results)
        
        # Prepare complete results
        complete_results = {
            "scraping_results": scraping_results,
            "arbitrage_analysis": arbitrage_analysis,
            "summary": {
                "total_attempted": len(self.scrapers),
                "successful_scrapes": len(scraping_results),
                "failed_scrapes": len(self.scrapers) - len(scraping_results),
                "analysis_timestamp": datetime.now().isoformat()
            }
        }
        
        # Save results if requested
        if save_results:
            self.save_results(scraping_results)
        
        return complete_results 