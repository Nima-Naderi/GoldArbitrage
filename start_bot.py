#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Easy startup script for the Gold Arbitrage Telegram Bot
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def check_redis():
    """Check if Redis is running"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        return True
    except:
        return False

def start_redis():
    """Try to start Redis"""
    print("🔄 Attempting to start Redis...")
    try:
        # Try different methods to start Redis
        if sys.platform == "darwin":  # macOS
            subprocess.run(["brew", "services", "start", "redis"], check=True)
        elif sys.platform.startswith("linux"):  # Linux
            subprocess.run(["sudo", "systemctl", "start", "redis"], check=True)
        print("✅ Redis started successfully!")
        return True
    except:
        print("❌ Could not start Redis automatically")
        print("💡 Please start Redis manually:")
        print("   macOS: brew services start redis")
        print("   Linux: sudo systemctl start redis")
        print("   Docker: docker run -d -p 6379:6379 redis:alpine")
        return False

def main():
    """Main startup function"""
    print("🤖 Gold Arbitrage Telegram Bot Startup")
    print("=" * 50)
    
    # Check Redis
    if not check_redis():
        print("❌ Redis is not running")
        if not start_redis():
            return False
    else:
        print("✅ Redis is running")
    
    # Check .env file
    if not Path('.env').exists():
        print("❌ .env file not found")
        print("💡 Please create .env file with your Telegram credentials")
        return False
    else:
        print("✅ .env file found")
    
    print("\n🚀 Starting the bot...")
    print("This will start both the worker and beat scheduler")
    print("Press Ctrl+C to stop\n")
    
    try:
        # Start worker in background
        worker_process = subprocess.Popen([
            sys.executable, "start_worker.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give worker time to start
        time.sleep(2)
        
        # Start beat scheduler
        beat_process = subprocess.Popen([
            sys.executable, "start_beat.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Bot started successfully!")
        print("📱 Check your Telegram channel for messages")
        print("📊 Bot will run every 5 minutes")
        
        # Wait for processes
        try:
            worker_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping bot...")
            worker_process.terminate()
            beat_process.terminate()
            print("✅ Bot stopped")
            
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
