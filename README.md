# 🏆 Gold Arbitrage Bot

Automated gold price monitoring and arbitrage opportunity detection with Telegram notifications.

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install Redis
brew install redis && brew services start redis  # macOS
# or: sudo apt install redis-server && sudo systemctl start redis  # Linux

# Configure Telegram bot
cp .env.example .env
# Edit .env with your bot token and channel ID
```

### 2. Run
```bash
# Start the bot
python start_bot.py
```

## 📊 Features

- **9 Gold Sources**: Scrapes prices from major Iranian gold websites
- **Real-time Analysis**: Finds arbitrage opportunities every 5 minutes
- **Telegram Notifications**: Sends formatted reports to your channel
- **Automated Scheduling**: Runs 24/7 with Celery
- **Data Export**: Saves results to JSON files

## 🏪 Supported Websites

1. **Milli Gold** (milli.gold) - Digital gold trading platform
2. **Talasea** (talasea.ir) - Gold investment platform
3. **Goldika** (goldika.ir) - Online gold trading
4. **Melligold** (melligold.com) - Gold investment services
5. **Wallgold** (wallgold.ir) - Digital gold wallet
6. **Technogold** (technogold.gold) - Technology-based gold trading
7. **Daric** (daric.gold) - Gold trading platform
8. **Talapp** (talapp.ir) - Gold trading application
9. **Digikala** (digikala.com/wealth/landing/digital-gold) - E-commerce digital gold

## 🎯 Usage

```bash
# Test connection
python telegram_arbitrage_bot.py test

# Manual run
python telegram_arbitrage_bot.py manual

# Start automated bot
python start_bot.py
```

## 📱 Telegram Setup

1. Create bot with [@BotFather](https://t.me/botfather)
2. Add bot to your channel as admin
3. Get channel ID from [@userinfobot](https://t.me/userinfobot)
4. Set credentials in `.env` file

## 📁 Project Structure

```
GoldArbitrage/
├── scrapers/           # Gold price scrapers
├── utils/              # Price conversion utilities
├── gold_arbitrage_finder.py    # Main analysis engine
├── telegram_arbitrage_bot.py   # Telegram bot & Celery tasks
├── start_bot.py        # Automated startup script
└── arbitrage_results/  # Generated reports
```

## 🔧 Requirements

- Python 3.8+
- Redis
- Telegram Bot Token
- Internet connection

## 📈 Sample Output

```
🏆 GOLD ARBITRAGE REPORT
📅 2024-12-01 14:30:22
📊 Sources: 8

💰 PRICE RANGE:
🔻 Lowest:  12,345,000 (Milli Gold)
🔺 Highest: 12,456,000 (Digikala)
📏 Range:   111,000 (0.90%)

🎯 TOP ARBITRAGE OPPORTUNITIES:
1. Milli Gold → Digikala
   💵 Buy:  12,345,000
   💰 Sell: 12,456,000
   📈 Profit: 111,000 (0.90%)
```

## 🛠️ Troubleshooting

- **Redis not running**: `brew services start redis`
- **No messages**: Check bot token and channel ID
- **Scrapers failing**: Some sites may block requests
- **Process issues**: Restart with `python start_bot.py`

## 📄 License

MIT License - Feel free to use and modify.