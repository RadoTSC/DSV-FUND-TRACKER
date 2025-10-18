# 🚨 DSV Fund Investment Tracker

Real-time Discord bot that monitors [@dsvfund](https://x.com/dsvfund) Twitter account and posts live portfolio rankings when they invest in Bittensor subnets.

## 🎯 Features

- ⚡ **Real-time alerts** - Detects investments within 60 seconds of DSV tweeting
- 📊 **Portfolio rankings** - Auto-calculates and displays subnet rankings by total invested
- 🏷️ **Category breakdown** - Shows allocation by sector (Agents, Trading, DeSci, etc.)
- 🔒 **Deterministic parsing** - No LLM hallucinations, pure regex validation
- 💾 **Backup system** - Auto-backup before each update

## 📸 Example Output
```
🚨 DSV FUND JUST INVESTED $100,000 in Subnet 75 (HIPPIUS)

📊 DSV FUND PORTFOLIO - LIVE RANKINGS

1. SN62 (RIDGES): $972,000 (40.2%)
2. SN11 (DIPPY STUDIO): $200,000 (8.3%)
...

🎯 TOTAL INVESTED: $2,422,000
📈 Total entries: 15

📂 ALLOCATION BY CATEGORY
  Agents: 45.2%
  Training: 18.3%
  ...
```

## 🏗️ Architecture
```
dsv_monitor.py (Python 3.11)
    ↓ Checks @dsvfund every 55-65s
    ↓ Validates tweets with dsv_system.py
    ↓ Updates dsv_investments.json
    ↓ Creates dsv_signal.txt (doorbell)
    ↓
bot.py (Python 3.13)
    ↓ Watches for signal file every 5s
    ↓ Reads updated ledger
    ↓ Posts to Discord
```

## 📋 Prerequisites

- Python 3.11 (for Twitter scraping)
- Python 3.13 (for Discord bot)
- Discord bot token
- Twitter account + cookies (for twikit)
- [twikit](https://github.com/d60/twikit) library

## 🚀 Quick Start

### 1. Install Dependencies

**Python 3.11 environment (for monitor):**
```bash
pip install twikit
```

**Python 3.13 environment (for Discord bot):**
```bash
pip install discord.py python-dotenv
```

### 2. Setup Files

1. Copy `dsv_system.py`, `dsv_monitor.py` to your project folder
2. Rename `dsv_investments_starter.json` → `dsv_investments.json`
3. Get Twitter cookies with burner acc (inspect element f12)
4. Save cookies to `cookies.json`

### 3. Integrate with Discord Bot

See [`bot_integration.md`](bot_integration.md) for detailed code snippets to add to your `bot.py`.

**Summary:**
- Add DSV channel ID constant
- Add DSV monitor subprocess startup
- Add signal watcher background task
- (Optional) Add `!dsv_now` and `!dsv_undo` commands

### 4. Run
```bash
# Your Discord bot (Python 3.13)
python bot.py

# Monitor starts automatically as subprocess
```

## 📁 Core Files

| File | Purpose |
|------|---------|
| `dsv_system.py` | Investment parser, validator, ledger manager, formatter |
| `dsv_monitor.py` | Twitter monitor (checks @dsvfund every 60s) |
| `dsv_investments.json` | Investment ledger database |
| `dsv_signal.txt` | Temporary signal file (auto-created/deleted) |

## ⚙️ Configuration

Edit these in `dsv_monitor.py`:
```python
DSV_HANDLE = "dsvfund"              # Twitter account to monitor
CHECK_INTERVAL_MIN = 55             # Minimum seconds between checks
CHECK_INTERVAL_MAX = 65             # Maximum seconds between checks
```

Edit in your `bot.py`:
```python
DSV_CHANNEL_ID = 1234567890         # Your Discord channel ID
```

## 🔧 How It Works

### Investment Detection

The system validates tweets using 4 strict filters:
1. ✅ Contains investment keyword (`invest`, `allocated`, `OTC`, etc.)
2. ✅ Contains subnet identifier (`SN75`, `Subnet 75`, etc.)
3. ✅ Contains dollar amount (`$100,000`, `$100k`, etc.)
4. ✅ Is original tweet (not RT/reply/quote)

### Data Extraction

- **First amount only** - Ignores "bringing total to $X" mentions
- **Regex-based** - No LLM, zero hallucination risk
- **Duplicate detection** - Same subnet + amount + date = skip

## 🛠️ Optional Commands

Add these to your Discord bot for manual control:

- `!dsv_now` - Display current portfolio (no wait for new investment)
- `!dsv_undo` - Revert last investment (admin only)

## 📊 Subnet Categories

All 128 Bittensor subnets are mapped to categories:
- Agents
- Training  
- Trading
- DeSci
- Compute
- Data
- Storage
- And more...

See `SUBNET_CATEGORIES` in `dsv_system.py` for full mapping.

## 🐛 Troubleshooting

**Monitor not starting?**
- Check Python 3.11 is installed
- Verify `cookies.json` exists and is valid

**No Discord posts?**
- Check channel ID is correct
- Verify bot has send permissions
- Check terminal for errors

**Duplicate investments?**
- Use `!dsv_undo` to revert
- Check `dsv_investments_backup.json` exists

## 📝 License

MIT License - Free to use and modify

## 🤝 Contributing

Pull requests welcome! Please test thoroughly before submitting.

## ⭐ Support

If this helped you copy-trade DSV Fund faster, consider starring the repo!

---

**Built for the Bittensor community** 🟣
