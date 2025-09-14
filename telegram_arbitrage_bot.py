#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from io import StringIO
import sys

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Celery imports
from celery import Celery
from celery.schedules import crontab

# Telegram imports
import aiohttp
import requests

# Import our arbitrage finder
from gold_arbitrage_finder import GoldArbitrageFinder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Celery configuration
app = Celery('gold_arbitrage_bot')
app.conf.update(
    broker_url='redis://localhost:6379/0',  # Redis as message broker
    result_backend='redis://localhost:6379/0',
    timezone='Asia/Tehran',
    enable_utc=True,
)

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
        Format arbitrage results into a Telegram-friendly message
        
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
        
        # Price summary
        if finder.prices:
            sorted_prices = sorted(finder.prices, key=lambda x: x.price)
            lowest = sorted_prices[0]
            highest = sorted_prices[-1]
            
            message += f"💰 <b>PRICE RANGE:</b>\n"
            message += f"🔻 Lowest:  {self.format_price(lowest.price)} ({lowest.source})\n"
            message += f"🔺 Highest: {self.format_price(highest.price)} ({highest.source})\n"
            
            price_range = highest.price - lowest.price
            range_percentage = (price_range / lowest.price) * 100
            message += f"📏 Range:   {self.format_price(price_range)} ({range_percentage:.2f}%)\n\n"
        
        # Arbitrage opportunities
        if finder.arbitrage_opportunities:
            message += f"🎯 <b>TOP ARBITRAGE OPPORTUNITIES:</b>\n"
            message += f"Found {len(finder.arbitrage_opportunities)} opportunities\n\n"
            
            # Show top 3 opportunities
            for i, opp in enumerate(finder.arbitrage_opportunities[:3], 1):
                message += f"{i}. <b>{opp.buy_source}</b> → <b>{opp.sell_source}</b>\n"
                message += f"   💵 Buy:  {self.format_price(opp.buy_price)}\n"
                message += f"   💰 Sell: {self.format_price(opp.sell_price)}\n"
                message += f"   📈 Profit: {self.format_price(opp.profit_per_gram)} ({opp.profit_percentage:.2f}%)\n\n"
            
            # Summary stats
            if len(finder.arbitrage_opportunities) > 3:
                max_profit = max(opp.profit_percentage for opp in finder.arbitrage_opportunities)
                avg_profit = sum(opp.profit_percentage for opp in finder.arbitrage_opportunities) / len(finder.arbitrage_opportunities)
                
                message += f"📊 <b>SUMMARY:</b>\n"
                message += f"🎯 Max Profit: {max_profit:.2f}%\n"
                message += f"📊 Avg Profit: {avg_profit:.2f}%\n"
        else:
            message += "❌ No arbitrage opportunities found with current criteria.\n"
        
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


@app.task
def run_arbitrage_and_send():
    """
    Celery task to run arbitrage analysis and send results to Telegram
    """
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
            return {"status": "error", "message": "No prices scraped"}
        
        # Find arbitrage opportunities
        finder.find_arbitrage_opportunities(min_profit_percentage=0.5)
        
        # Send report to Telegram
        success = reporter.send_arbitrage_report(finder)
        
        if success:
            logger.info("Arbitrage report sent to Telegram successfully")
            return {
                "status": "success", 
                "prices_count": len(finder.prices),
                "opportunities_count": len(finder.arbitrage_opportunities)
            }
        else:
            logger.error("Failed to send report to Telegram")
            return {"status": "error", "message": "Failed to send to Telegram"}
            
    except Exception as e:
        logger.error(f"Error in arbitrage task: {e}")
        # Send error message to Telegram
        try:
            telegram_sender = TelegramSender(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID)
            error_message = f"❌ <b>ARBITRAGE BOT ERROR</b>\n\nError: {str(e)}"
            telegram_sender.send_message(error_message)
        except:
            pass
        
        return {"status": "error", "message": str(e)}


# Configure Celery beat schedule
app.conf.beat_schedule = {
    'run-arbitrage-every-5-minutes': {
        'task': 'telegram_arbitrage_bot.run_arbitrage_and_send',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}

# Make sure the task is properly registered
app.conf.task_routes = {
    'telegram_arbitrage_bot.run_arbitrage_and_send': {'queue': 'default'},
}

app.conf.timezone = 'Asia/Tehran'


def test_telegram_connection():
    """Test function to verify Telegram bot setup"""
    print(f"🔍 Debug - TELEGRAM_BOT_TOKEN: {'Set' if TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE' else 'Not set'}")
    print(f"🔍 Debug - TELEGRAM_CHANNEL_ID: {'Set' if TELEGRAM_CHANNEL_ID and TELEGRAM_CHANNEL_ID != 'YOUR_CHANNEL_ID_HERE' else 'Not set'}")
    
    if TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE' or TELEGRAM_CHANNEL_ID == 'YOUR_CHANNEL_ID_HERE' or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("❌ Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID environment variables")
        print("💡 Make sure your .env file contains:")
        print("   TELEGRAM_BOT_TOKEN=your_actual_bot_token")
        print("   TELEGRAM_CHANNEL_ID=your_actual_channel_id")
        return False
    
    telegram_sender = TelegramSender(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID)
    test_message = "🤖 <b>Gold Arbitrage Bot Test</b>\n\nBot is working correctly!"
    
    success = telegram_sender.send_message(test_message)
    if success:
        print("✅ Telegram connection test successful!")
    else:
        print("❌ Telegram connection test failed!")
    
    return success


def run_manual_analysis():
    """Run a manual arbitrage analysis and send to Telegram"""
    print("🚀 Running manual arbitrage analysis...")
    
    # Initialize components
    telegram_sender = TelegramSender(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID)
    reporter = ArbitrageReporter(telegram_sender)
    
    # Run analysis
    finder = GoldArbitrageFinder()
    finder.run_full_analysis(min_profit_percentage=0.5, save_results=True)
    
    # Send to Telegram
    success = reporter.send_arbitrage_report(finder)
    
    if success:
        print("✅ Report sent to Telegram successfully!")
    else:
        print("❌ Failed to send report to Telegram")
    
    return success


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            test_telegram_connection()
        elif command == "manual":
            run_manual_analysis()
        elif command == "worker":
            # Start Celery worker
            print("🚀 Starting Celery worker...")
            print("💡 For better control, use: python start_worker.py")
            app.worker_main(['worker', '--loglevel=info', '--concurrency=1'])
        elif command == "beat":
            # Start Celery beat scheduler
            print("🚀 Starting Celery beat scheduler...")
            print("💡 For better control, use: python start_beat.py")
            app.start(['beat', '--loglevel=info'])
        else:
            print("Usage: python telegram_arbitrage_bot.py [test|manual|worker|beat]")
    else:
        print("🤖 Gold Arbitrage Telegram Bot")
        print("=" * 40)
        print("Commands:")
        print("  test   - Test Telegram connection")
        print("  manual - Run manual analysis and send to Telegram")
        print("  worker - Start Celery worker")
        print("  beat   - Start Celery beat scheduler")
        print()
        print("Environment variables needed:")
        print("  TELEGRAM_BOT_TOKEN - Your Telegram bot token")
        print("  TELEGRAM_CHANNEL_ID - Your Telegram channel ID")
