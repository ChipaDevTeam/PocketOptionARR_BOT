<div align="center">

# PocketOption Gap Arbitrage Bot

**An automated trading bot that exploits price gaps between EURUSD and EURUSD OTC on [Pocket Option](https://u3.shortink.io/main?utm_campaign=821315&utm_source=affiliate&utm_medium=sr&a=SDIaxbeamcYYqB&al=1746142&ac=chipa&cid=949965&code=50START)**

Built with [BinaryOptionsTools V2](https://github.com/ChipaDevTeam/BinaryOptionsTools-v2) by [ChipaDevTeam](https://github.com/ChipaDevTeam)

[![Discord](https://img.shields.io/badge/Discord-Join%20Community-5865F2?logo=discord&logoColor=white)](https://discord.gg/PHHfh6UyCb)
[![GitHub](https://img.shields.io/badge/GitHub-ChipaDevTeam-181717?logo=github)](https://github.com/ChipaDevTeam)
[![ChipaEditor](https://img.shields.io/badge/ChipaEditor-Try%20Now-blue)](https://chipaeditor.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## How It Works

The bot monitors **two price feeds simultaneously** — the real `EURUSD` market and the `EURUSD_otc` (OTC) market on Pocket Option. OTC prices tend to follow the real market but with a small delay, which occasionally creates temporary **price gaps**.

When a gap is detected that exceeds a configurable threshold, the bot places a trade on the OTC asset expecting a **price correction**:

| Scenario | Gap Direction | Expected Correction | Action |
|---|---|---|---|
| Real price **above** OTC | `gap > +threshold` | OTC will correct **upward** | Place a **CALL** option |
| Real price **below** OTC | `gap < -threshold` | OTC will correct **downward** | Place a **PUT** option |

The larger the gap, the higher the probability of a correction — making these signals high-confidence when they occur.

### Strategy Diagram

```
EURUSD (Real)    ──────────╲
                            ╲  Gap detected!
                            ╱  → Place trade on OTC
EURUSD_otc       ──────────╱
                                 ↓
                           OTC corrects toward
                           the real price
```

## Features

- Real-time dual price stream monitoring via WebSocket
- Configurable gap threshold, trade amount, duration, and cooldown
- Automatic trade placement (CALL / PUT) based on gap direction
- Background trade result tracking with win/loss reporting
- Built-in logging support
- Cooldown system to prevent overtrading

## Quick Start

### Prerequisites

- Python 3.9+
- A [Pocket Option](https://u3.shortink.io/main?utm_campaign=821315&utm_source=affiliate&utm_medium=sr&a=SDIaxbeamcYYqB&al=1746142&ac=chipa&cid=949965&code=50START) account

### Installation

```bash
# Clone the repository
git clone https://github.com/ChipaDevTeam/PocketOptionARR_BOT.git
cd PocketOptionARR_BOT

# Create a virtual environment (recommended)
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install the BinaryOptionsTools V2 library
pip install "https://github.com/ChipaDevTeam/BinaryOptionsTools-v2/releases/download/v0.2.9/binaryoptionstoolsv2-0.2.9-cp39-abi3-win_amd64.whl"
```

### Running the Bot

```bash
python gap_bot.py
```

You will be prompted to enter your **SSID**. The SSID is your session token from Pocket Option — the bot auto-detects whether it's a demo or real account.

### Configuration

All settings are at the top of `gap_bot.py`:

```python
REAL_ASSET = "EURUSD"        # Real market asset
OTC_ASSET  = "EURUSD_otc"    # OTC market asset
GAP_THRESHOLD = 0.00130      # Minimum gap to trigger a trade
TRADE_AMOUNT = 1.0           # Trade amount in USD
TRADE_DURATION = 60          # Option expiry in seconds
COOLDOWN_SECONDS = 60        # Minimum seconds between trades
```

> **Tip:** A gap of `0.001` on EUR/USD is uncommon but when it happens the correction is highly probable. Lower the threshold for more frequent (but lower confidence) signals.

## Example Output

```
[*] Connected — Balance: 99.9

============================================================
  Gap Arbitrage Bot
  Pair: EURUSD vs EURUSD_otc
  Threshold: ±0.0013
  Trade: $1.0 / 60s
============================================================

[*] Prices received for both symbols. Monitoring gap...

  EURUSD: 1.08432  |  OTC: 1.08301  |  Gap: +0.00131 <<< SIGNAL
[TRADE] GAP +0.00131 >= +0.0013 → CALL on EURUSD_otc  ($1.0, 60s)
[OK]    Trade placed — ID: abc123
[RESULT] CALL (gap +0.00131) → WIN  | data: {...}
```

## Powered By

### BinaryOptionsTools V2

This bot is built on top of **[BinaryOptionsTools V2](https://github.com/ChipaDevTeam/BinaryOptionsTools-v2)** — a fast, async Python library for connecting to Pocket Option via WebSocket. It handles authentication, real-time price streams, trade execution, and more.

Check out the full library to build your own custom strategies.

### ChipaEditor

Need a browser-based coding environment? Try **[ChipaEditor](https://chipaeditor.com)** — our new online code editor built for developers.

## Get Help & Community

- **Discord** — Join our community for live help, strategy discussions, and updates: [discord.gg/PHHfh6UyCb](https://discord.gg/PHHfh6UyCb)
- **GitHub Issues** — Found a bug or have a feature request? Open an issue on the [repository](https://github.com/ChipaDevTeam/PocketOptionARR_BOT/issues)
- **BinaryOptionsTools V2 Issues** — For library-specific problems: [BinaryOptionsTools-v2 Issues](https://github.com/ChipaDevTeam/BinaryOptionsTools-v2/issues)

## Disclaimer

This bot is provided for **educational and research purposes only**. Trading binary options involves significant risk. Past performance does not guarantee future results. Use at your own risk and always trade responsibly. Start with a **demo account** to test the strategy before using real funds.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by [ChipaDevTeam](https://github.com/ChipaDevTeam)**

[Create a Pocket Option Account](https://u3.shortink.io/main?utm_campaign=821315&utm_source=affiliate&utm_medium=sr&a=SDIaxbeamcYYqB&al=1746142&ac=chipa&cid=949965&code=50START) · [Discord](https://discord.gg/PHHfh6UyCb) · [GitHub](https://github.com/ChipaDevTeam) · [ChipaEditor](https://chipaeditor.com)

</div>