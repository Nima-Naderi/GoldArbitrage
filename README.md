# GoldArbitrage

A comprehensive gold price scraping and arbitrage analysis tool for Iranian gold trading websites. This project scrapes real-time gold prices from multiple sources and identifies potential arbitrage opportunities.

## Features

- **Multi-source scraping**: Scrapes 9 major Iranian gold trading websites
- **Concurrent processing**: Uses multi-threading for fast, parallel scraping
- **Arbitrage analysis**: Automatically identifies price differences and arbitrage opportunities
- **Flexible architecture**: Common base class with individual scrapers for each website
- **Multiple output formats**: JSON, CSV, and formatted console output
- **Error handling**: Robust error handling with detailed logging
- **Anti-bot measures**: Uses rotating user agents and undetected Chrome driver

## Supported Websites

1. **Milli Gold** (milli.gold) - Digital gold trading platform
2. **Talasea** (talasea.ir) - Gold investment platform
3. **Goldika** (goldika.ir) - Online gold trading
4. **Melligold** (melligold.com) - Gold investment services
5. **Wallgold** (wallgold.ir) - Digital gold wallet
6. **Technogold** (technogold.gold) - Technology-based gold trading
7. **Daric** (daric.gold) - Gold trading platform
8. **Talapp** (talapp.ir) - Gold trading application
9. **Digikala** (digikala.com/wealth/landing/digital-gold) - E-commerce digital gold

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd GoldArbitrage
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. For Selenium-based scrapers, ensure you have Chrome browser installed.

## Usage

### Command Line Interface

#### Basic usage - scrape all websites:
```bash
python main.py
```

#### List available scrapers:
```bash
python main.py --list
```

#### Scrape specific websites:
```bash
python main.py --sites milli talasea goldika
```

#### Save results to files:
```bash
python main.py --save
```

#### Custom output filename:
```bash
python main.py --save --output my_gold_prices
```

#### JSON output:
```bash
python main.py --json
```

#### Adjust concurrent workers:
```bash
python main.py --workers 10
```

### Python API

```python
from src.gold_scraper import GoldArbitrageScraper

# Initialize scraper
scraper = GoldArbitrageScraper(max_workers=5)

# Scrape all sites with complete analysis
results = scraper.run_complete_analysis()

# Scrape specific sites
results = scraper.scrape_specific_sites(['milli', 'talasea'])

# Get arbitrage analysis
analysis = scraper.analyze_arbitrage_opportunities(results)

# Save results
scraper.save_results(results, 'my_results')
```

### Individual Scraper Usage

```python
from src.scrapers.milli_scraper import MilliScraper

# Use a single scraper
with MilliScraper() as scraper:
    data = scraper.scrape()
    if data:
        print(f"Price: {data.price} IRR")
        print(f"24h Change: {data.change_percent}%")
```

## Data Structure

Each scraper returns a `GoldPriceData` object with the following fields:

```python
{
    "price": 86600000,           # Current price in IRR
    "change_24h": 0,             # 24-hour absolute change
    "change_percent": 0.77,      # 24-hour percentage change
    "currency": "IRR",           # Currency (Iranian Rial)
    "source": "milli",           # Source website identifier
    "timestamp": "2024-01-01T12:00:00"  # Scraping timestamp
}
```

## Project Structure

```
GoldArbitrage/
├── src/
│   ├── __init__.py
│   ├── base_scraper.py          # Common base class for all scrapers
│   ├── gold_scraper.py          # Main orchestrator class
│   └── scrapers/
│       ├── __init__.py
│       ├── milli_scraper.py     # Milli Gold scraper
│       ├── talasea_scraper.py   # Talasea scraper
│       ├── goldika_scraper.py   # Goldika scraper
│       ├── melligold_scraper.py # Melligold scraper
│       ├── wallgold_scraper.py  # Wallgold scraper
│       ├── technogold_scraper.py # Technogold scraper
│       ├── daric_scraper.py     # Daric scraper
│       ├── talapp_scraper.py    # Talapp scraper
│       └── digikala_scraper.py  # Digikala scraper
├── main.py                      # Command-line interface
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Architecture

### Base Scraper Class

The `BaseScraper` class provides common functionality:

- **HTTP/Selenium support**: Configurable requests or Selenium-based scraping
- **Error handling**: Comprehensive exception handling and logging
- **Text processing**: Persian/Arabic number conversion and price extraction
- **Anti-bot measures**: User agent rotation and undetected Chrome driver

### Individual Scrapers

Each website has its own scraper class that inherits from `BaseScraper`:

- **Custom selectors**: Website-specific CSS selectors and extraction logic
- **Pattern matching**: Regex patterns for price and change detection
- **Validation**: Price range validation and data sanitization

### Main Orchestrator

The `GoldArbitrageScraper` class coordinates all scrapers:

- **Concurrent execution**: Multi-threaded scraping for performance
- **Arbitrage analysis**: Automatic price comparison and opportunity detection
- **Data export**: JSON and CSV output with timestamp tracking

## Arbitrage Analysis

The system automatically analyzes scraped prices to identify arbitrage opportunities:

- **Price comparison**: Finds highest and lowest prices across sources
- **Percentage calculation**: Calculates price differences as percentages
- **Opportunity detection**: Flags differences > 1% as potential arbitrage
- **Detailed reporting**: Provides source attribution and profit potential

## Error Handling

The scraper includes robust error handling:

- **Network errors**: Automatic retries and timeout handling
- **Parsing errors**: Graceful failure with detailed logging
- **Anti-bot detection**: Fallback strategies and user agent rotation
- **Data validation**: Range checking and format validation

## Logging

Comprehensive logging is available at multiple levels:

- **INFO**: Successful operations and progress updates
- **WARNING**: Recoverable errors and missing data
- **ERROR**: Critical failures and exceptions

## Configuration

### Scraper Settings

Each scraper can be configured for:

- **Selenium vs Requests**: Choose scraping method based on website complexity
- **Timeout values**: Adjust for network conditions
- **User agents**: Customize for better anti-bot evasion

### Price Validation

Price validation uses reasonable ranges:

- **Minimum price**: 50,000,000 IRR (reasonable floor for 18k gold)
- **Maximum price**: 200,000,000 IRR (reasonable ceiling)
- **Change validation**: ±50% daily change limit

## Contributing

To add a new gold trading website:

1. Create a new scraper in `src/scrapers/`
2. Inherit from `BaseScraper`
3. Implement `scrape()` and `get_selectors()` methods
4. Add to the scraper list in `GoldArbitrageScraper`
5. Test thoroughly with the website's structure

## Dependencies

- **requests**: HTTP requests and session management
- **beautifulsoup4**: HTML parsing and extraction
- **selenium**: Browser automation for JavaScript-heavy sites
- **undetected-chromedriver**: Anti-bot detection evasion
- **pandas**: Data manipulation and CSV export
- **fake-useragent**: User agent rotation
- **lxml**: Fast XML/HTML processing

## Legal and Ethical Considerations

- **Rate limiting**: Built-in delays to avoid overwhelming servers
- **Respectful scraping**: Follows robots.txt and website terms where applicable
- **Educational purpose**: Designed for price comparison and market analysis
- **No warranty**: Use at your own risk for trading decisions

## Performance

- **Concurrent scraping**: 5-10 websites scraped simultaneously
- **Average time**: 30-60 seconds for complete analysis
- **Memory usage**: Minimal footprint with proper resource cleanup
- **Success rate**: 70-90% depending on website availability and anti-bot measures

## Troubleshooting

### Common Issues

1. **Chrome driver errors**: Ensure Chrome browser is installed
2. **Network timeouts**: Check internet connection and increase timeout values
3. **Anti-bot detection**: Try reducing concurrent workers or adding delays
4. **Missing prices**: Websites may have changed their structure

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Gold prices are volatile and this information should not be used as the sole basis for trading decisions. Always verify prices with official sources before making any transactions.
