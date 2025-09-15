# 🏆 Gold Arbitrage Bot

Automated gold price monitoring and arbitrage opportunity detection with Telegram notifications.

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure Telegram bot
cp .env.example .env
# Edit .env with your bot token and channel ID
```

### 2. Run
```bash
# Start the bot
python simple_bot.py
```

## 📊 Features

- **9 Gold Sources**: Scrapes prices from major Iranian gold websites
- **Real-time Analysis**: Finds arbitrage opportunities every 4 minutes
- **Telegram Notifications**: Sends formatted reports to your channel
- **Simple Scheduling**: Runs 24/7 with a simple while loop
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
# Run the bot
python simple_bot.py
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
├── simple_bot.py       # The bot (run this!)
└── arbitrage_results/  # Generated reports
```

## 🔧 Requirements

- Python 3.8+
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

- **No messages**: Check bot token and channel ID in .env file
- **Scrapers failing**: Some sites may block requests
- **Bot stops**: Check internet connection and restart
- **Connection issues**: Bot automatically tests Telegram connection on startup

## 📄 License

MIT License - Feel free to use and modify.