#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple Gold Arbitrage Bot - No Celery, just a while loop
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import our arbitrage finder
from gold_arbitrage_finder import GoldArbitrageFinder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', 'YOUR_CHANNEL_ID_HERE')

# Maximum message length for Telegram (4096 characters)
MAX_MESSAGE_LENGTH = 4000


class TelegramSender:
    """Class to handle Telegram message sending"""
    
    def __init__(self, bot_token: str, channel_id: str):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message to Telegram channel
        
        Args:
            text: Message text to send
            parse_mode: Parse mode (HTML or Markdown)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.channel_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            logger.info("Message sent to Telegram successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send message to Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False
    
    def send_long_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """
        Send a long message by splitting it into chunks
        
        Args:
            text: Long message text
            parse_mode: Parse mode (HTML or Markdown)
            
        Returns:
            bool: True if all chunks sent successfully
        """
        if len(text) <= MAX_MESSAGE_LENGTH:
            return self.send_message(text, parse_mode)
        
        # Split message into chunks
        chunks = []
        current_chunk = ""
        
        lines = text.split('\n')
        for line in lines:
            if len(current_chunk + line + '\n') <= MAX_MESSAGE_LENGTH:
                current_chunk += line + '\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Send each chunk
        success = True
        for i, chunk in enumerate(chunks):
            if i > 0:
                chunk = f"📄 Part {i+1}/{len(chunks)}\n\n{chunk}"
            
            if not self.send_message(chunk, parse_mode):
                success = False
        
        return success


class ArbitrageReporter:
    """Class to format arbitrage results for Telegram"""
    
    def __init__(self, telegram_sender: TelegramSender):
        self.telegram_sender = telegram_sender
    
    def format_arbitrage_report(self, finder: GoldArbitrageFinder) -> str:
        """
        Format arbitrage results into a detailed Telegram message
        
        Args:
            finder: GoldArbitrageFinder instance with results
            
        Returns:
            str: Formatted message for Telegram
        """
        if not finder.prices:
            return "❌ No gold prices could be scraped at this time."
        
        # Header
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"🏆 <b>GOLD ARBITRAGE REPORT</b>\n"
        message += f"📅 {timestamp}\n"
        message += f"📊 Sources: {len(finder.prices)}\n\n"
        
        # All prices by source
        if finder.prices:
            sorted_prices = sorted(finder.prices, key=lambda x: x.price)
            
            message += f"💰 <b>ALL GOLD PRICES (18K per gram):</b>\n"
            for i, price in enumerate(sorted_prices, 1):
                message += f"{i:2d}. {price.source:<12}: {self.format_price(price.price):>12} Rial"
                if price.price_change:
                    message += f" ({price.price_change})"
                message += "\n"
            
            # Price range analysis
            lowest = sorted_prices[0]
            highest = sorted_prices[-1]
            price_range = highest.price - lowest.price
            range_percentage = (price_range / lowest.price) * 100
            
            message += f"\n📊 <b>PRICE ANALYSIS:</b>\n"
            message += f"🔻 Lowest:  {self.format_price(lowest.price)} Rial ({lowest.source})\n"
            message += f"🔺 Highest: {self.format_price(highest.price)} Rial ({highest.source})\n"
            message += f"📏 Range:   {self.format_price(price_range)} Rial ({range_percentage:.2f}%)\n\n"
        
        # All arbitrage opportunities
        if finder.arbitrage_opportunities:
            message += f"🎯 <b>ALL ARBITRAGE OPPORTUNITIES:</b>\n"
            message += f"Found {len(finder.arbitrage_opportunities)} opportunities\n\n"
            
            # Show ALL opportunities (not just top 3)
            for i, opp in enumerate(finder.arbitrage_opportunities, 1):
                message += f"{i:2d}. <b>{opp.buy_source}</b> → <b>{opp.sell_source}</b>\n"
                message += f"    💵 Buy:  {self.format_price(opp.buy_price)} Rial\n"
                message += f"    💰 Sell: {self.format_price(opp.sell_price)} Rial\n"
                message += f"    📈 Profit: {self.format_price(opp.profit_per_gram)} Rial\n"
                message += f"    🎯 Profit %: {opp.profit_percentage:.2f}%\n\n"
            
            # Summary statistics
            max_profit_percentage = max(opp.profit_percentage for opp in finder.arbitrage_opportunities)
            min_profit_percentage = min(opp.profit_percentage for opp in finder.arbitrage_opportunities)
            avg_profit_percentage = sum(opp.profit_percentage for opp in finder.arbitrage_opportunities) / len(finder.arbitrage_opportunities)
            
            # Find best opportunity by profit amount (Rial)
            best_opp = max(finder.arbitrage_opportunities, key=lambda x: x.profit_per_gram)
            max_profit_rial = best_opp.profit_per_gram
            
            message += f"📊 <b>OPPORTUNITY STATISTICS:</b>\n"
            message += f"🎯 Best Profit: {self.format_price(max_profit_rial)} Rial ({best_opp.buy_source} → {best_opp.sell_source})\n"
            message += f"📈 Best Profit %: {max_profit_percentage:.2f}%\n"
            message += f"📉 Lowest Profit %: {min_profit_percentage:.2f}%\n"
            message += f"📊 Average Profit %: {avg_profit_percentage:.2f}%\n"
            message += f"🔢 Total Opportunities: {len(finder.arbitrage_opportunities)}\n"
            
            # Profit analysis
            total_profit_potential = sum(opp.profit_per_gram for opp in finder.arbitrage_opportunities)
            message += f"💰 Total Profit Potential: {self.format_price(total_profit_potential)} Rial\n"
        else:
            message += "❌ No arbitrage opportunities found with current criteria.\n"
            message += "💡 This means all prices are very similar across sources.\n"
        
        # Market insights
        if finder.prices and len(finder.prices) > 1:
            message += f"\n🔍 <b>MARKET INSIGHTS:</b>\n"
            
            # Price volatility
            prices = [p.price for p in finder.prices]
            avg_price = sum(prices) / len(prices)
            price_std = (sum((p - avg_price) ** 2 for p in prices) / len(prices)) ** 0.5
            volatility = (price_std / avg_price) * 100
            
            message += f"📊 Average Price: {self.format_price(avg_price)} Rial\n"
            message += f"📈 Price Volatility: {volatility:.2f}%\n"
            
            # Market efficiency
            if volatility < 0.5:
                message += f"✅ Market is highly efficient (low volatility)\n"
            elif volatility < 1.0:
                message += f"⚖️ Market shows moderate efficiency\n"
            else:
                message += f"⚠️ Market shows high volatility (good for arbitrage)\n"
        
        # Footer
        message += f"\n🤖 <i>Automated Gold Arbitrage Bot</i>"
        
        return message
    
    def format_price(self, price: float) -> str:
        """Format price with commas"""
        return f"{int(price):,}"
    
    def send_arbitrage_report(self, finder: GoldArbitrageFinder) -> bool:
        """
        Send arbitrage report to Telegram
        
        Args:
            finder: GoldArbitrageFinder instance with results
            
        Returns:
            bool: True if sent successfully
        """
        try:
            message = self.format_arbitrage_report(finder)
            return self.telegram_sender.send_long_message(message)
        except Exception as e:
            logger.error(f"Error formatting/sending report: {e}")
            return False


def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check .env file
    if not Path('.env').exists():
        print("❌ .env file not found")
        print("💡 Create .env file with your Telegram credentials")
        return False
    
    # Check environment variables
    if TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE' or not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env file")
        return False
    
    if TELEGRAM_CHANNEL_ID == 'YOUR_CHANNEL_ID_HERE' or not TELEGRAM_CHANNEL_ID:
        print("❌ TELEGRAM_CHANNEL_ID not set in .env file")
        return False
    
    print("✅ Environment variables configured")
    return True


def test_telegram_connection():
    """Test Telegram bot connection (no message sent)"""
    try:
        # Perform a lightweight getMe API call instead of sending a message
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return True
    except Exception:
        return False


def run_arbitrage_analysis():
    """Run one arbitrage analysis and send to Telegram"""
    try:
        logger.info("Starting arbitrage analysis...")
        
        # Initialize components
        telegram_sender = TelegramSender(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID)
        reporter = ArbitrageReporter(telegram_sender)
        
        # Run arbitrage analysis
        finder = GoldArbitrageFinder()
        finder.scrape_all_sources()
        
        if not finder.prices:
            error_message = "❌ <b>ARBITRAGE ANALYSIS FAILED</b>\n\nNo gold prices could be scraped at this time. Please check the scrapers."
            telegram_sender.send_message(error_message)
            return False
        
        # Find arbitrage opportunities
        finder.find_arbitrage_opportunities(min_profit_percentage=0.5)
        
        # Send report to Telegram
        success = reporter.send_arbitrage_report(finder)
        
        if success:
            logger.info("Arbitrage report sent to Telegram successfully")
            return True
        else:
            logger.error("Failed to send report to Telegram")
            return False
            
    except Exception as e:
        logger.error(f"Error in arbitrage analysis: {e}")
        # Send error message to Telegram
        try:
            telegram_sender = TelegramSender(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID)
            error_message = f"❌ <b>ARBITRAGE BOT ERROR</b>\n\nError: {str(e)}"
            telegram_sender.send_message(error_message)
        except:
            pass
        
        return False


def main():
    """Main function"""
    print("🤖 Simple Gold Arbitrage Bot")
    print("=" * 50)
    print("No Celery, just a simple while loop!")
    print()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements not met. Please fix the issues above.")
        return False
    
    # Test Telegram connection
    if not test_telegram_connection():
        print("\n❌ Telegram test failed. Please check your bot token and channel ID.")
        return False
    
    print("\n🚀 Starting the bot...")
    print("Bot will run every 4 minutes")
    print("Press Ctrl+C to stop")
    print()
    
    # Main loop
    try:
        while True:
            print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Running analysis...")
            
            # Run analysis
            success = run_arbitrage_analysis()
            
            if success:
                print("✅ Analysis completed successfully")
            else:
                print("❌ Analysis failed")
            
            # Wait 4 minutes (240 seconds)
            print("⏳ Waiting 4 minutes until next analysis...")
            time.sleep(240)  # 4 minutes
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping bot...")
        print("✅ Bot stopped")
        return True
    
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}")
        return False


if __name__ == "__main__":
    main()
