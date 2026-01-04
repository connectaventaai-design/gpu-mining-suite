# 🎮 GPU Mining Management Suite

A comprehensive, production-ready GPU mining management system for Windows, designed specifically for NVIDIA GPUs like the GTX 1660 SUPER. Features a beautiful web dashboard, real-time monitoring, profit calculations, automated switching, and remote management capabilities.

![Mining Suite Banner](https://img.shields.io/badge/GPU-Mining-blue?style=for-the-badge&logo=nvidia)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## ✨ Features

### 🖥️ Real-time GPU Monitoring
- **Temperature, hashrate, power consumption** tracking
- **Fan speed and GPU utilization** monitoring
- **Memory usage** (current/total)
- **Clock speeds** (core and memory)
- **Historical data charts** with 24-hour history
- **Multi-GPU support** (ready for expansion)

### 💰 Profitability & Earnings
- **Live coin prices** from CoinGecko API
- **Real-time profitability** calculations
- **Electricity cost** tracking
- **Daily/weekly/monthly** earnings reports
- **Automatic coin switching** based on profitability
- Support for **6 major GPU-minable coins**

### 🤖 Smart Automation
- **Watchdog system** - auto-restart on crash
- **Temperature protection** - emergency shutdown at 85°C
- **Hashrate monitoring** - alert on performance drops
- **Scheduler** - mine during specific hours
- **Idle detection** support (future)
- **Algorithm auto-switching**

### 📊 Web Dashboard
- **Beautiful, responsive UI** - works on desktop and mobile
- **Dark/Light theme** toggle
- **Real-time charts** (temperature, hashrate)
- **One-click mining** start/stop
- **Profit comparison** across all supported coins
- **Settings management** via web interface

### 🔔 Notifications
- **Discord webhook** integration
- **Telegram bot** support
- **Email alerts** (planned)
- Customizable alert triggers:
  - High temperature (>80°C)
  - Low hashrate
  - Miner crash
  - High rejected shares

### ⚡ Overclocking (Safety First)
- **Per-coin profiles** optimized for GTX 1660 SUPER
- **Conservative defaults** for safety
- **Gradual adjustments** to prevent instability
- **Emergency rollback** on crash
- **Optional feature** - disabled by default

### 🌐 Remote Management
- **REST API** with comprehensive endpoints
- **Web-based control** accessible from any device
- **Secure authentication** (planned)
- **Mobile-friendly** dashboard

## 📋 Table of Contents

- [System Requirements](#-system-requirements)
- [Supported Coins](#-supported-coins)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Safety & Disclaimers](#-safety--disclaimers)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Contributing](#-contributing)
- [License](#-license)

## 💻 System Requirements

### Hardware
- **GPU**: NVIDIA GeForce GTX 1660 SUPER (or compatible NVIDIA GPU)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space
- **Internet**: Stable connection required

### Software
- **OS**: Windows 10/11 (64-bit)
- **NVIDIA Driver**: Version 470.0 or newer
- **Python**: Version 3.8+ (3.10 recommended)
- **Mining Software**: T-Rex Miner, lolMiner (see [miners/README.md](miners/README.md))

### Recommended
- **Cooling**: Adequate GPU cooling (case fans, GPU cooler)
- **Power Supply**: 500W+ with sufficient 12V rail
- **Monitor**: For initial setup (can use remotely after)

## 🪙 Supported Coins

The suite supports 6 major GPU-minable cryptocurrencies:

| Coin | Algorithm | Expected Hashrate* | Power | Best Miner |
|------|-----------|-------------------|-------|------------|
| **RVN** (Ravencoin) | KawPow | ~15.5 MH/s | 90W | T-Rex |
| **ETC** (Ethereum Classic) | Etchash | ~28.0 MH/s | 85W | T-Rex |
| **ERG** (Ergo) | Autolykos2 | ~90.0 MH/s | 95W | T-Rex |
| **FLUX** (Flux) | ZelHash | ~30.0 Sol/s | 92W | lolMiner |
| **KAS** (Kaspa) | kHeavyHash | ~420 MH/s | 100W | lolMiner |
| **ALPH** (Alephium) | Blake3 | ~130 MH/s | 95W | lolMiner |

*Hashrates for GTX 1660 SUPER with optimized overclocking

## 📦 Installation

### Step 1: Install Python

1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   ```

### Step 2: Clone Repository

```cmd
git clone https://github.com/connectaventaai-design/gpu-mining-suite.git
cd gpu-mining-suite
```

Or download as ZIP and extract.

### Step 3: Run Installation Script

```cmd
cd scripts
install.bat
```

This will:
- Check Python installation
- Upgrade pip
- Install all Python dependencies
- Create necessary directories

### Step 4: Download Mining Software

Follow instructions in [miners/README.md](miners/README.md) to download:
- **T-Rex Miner** (for RVN, ETC, ERG)
- **lolMiner** (for FLUX, KAS, ALPH)

Place executables in the `miners/` directory.

### Step 5: Configure Settings

1. Edit `configs/settings.json`
2. Add your wallet address:
   ```json
   {
     "mining": {
       "wallet_address": "YOUR_WALLET_ADDRESS_HERE"
     }
   }
   ```

### Step 6: Start the Dashboard

```cmd
cd scripts
start_mining.bat
```

Or manually:
```cmd
python backend/app.py
```

Open your browser to: **http://localhost:5000**

## ⚙️ Configuration

### Basic Configuration (`configs/settings.json`)

```json
{
  "mining": {
    "default_coin": "RVN",
    "mining_pool": "ravencoin.2miners.com:6060",
    "wallet_address": "YOUR_WALLET_ADDRESS",
    "auto_start": false,
    "auto_switch": true,
    "worker_name": "GTX1660S"
  },
  "gpu": {
    "target_temp": 70,
    "max_temp": 80,
    "fan_min": 60,
    "fan_max": 100
  },
  "dashboard": {
    "port": 5000,
    "host": "0.0.0.0",
    "refresh_interval": 5
  }
}
```

### Wallet Addresses

Get wallet addresses from:
- **Ravencoin**: Official Ravencoin wallet or exchanges
- **ETC**: MyEtherWallet, Ledger, exchanges
- **Ergo**: Yoroi wallet, Nautilus wallet
- **Flux**: Zelcore wallet
- **Kaspa**: Kaspa wallet
- **Alephium**: Alephium wallet

### Mining Pools

Default pools are configured in `configs/coins.json`. Popular alternatives:

- **2Miners**: Reliable, low fees
- **MinePool**: Good for beginners
- **WoolyPooly**: Multi-algo support
- **Herominers**: Stable payouts

### Discord Notifications

1. Create a Discord webhook:
   - Server Settings → Integrations → Webhooks → New Webhook
2. Copy webhook URL
3. Add to settings:
   ```json
   {
     "notifications": {
       "discord_webhook": "https://discord.com/api/webhooks/..."
     }
   }
   ```

### Telegram Notifications

1. Create bot with [@BotFather](https://t.me/botfather)
2. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
3. Add to settings:
   ```json
   {
     "notifications": {
       "telegram_token": "123456:ABC-DEF...",
       "telegram_chat_id": "123456789"
     }
   }
   ```

## 🚀 Usage

### Starting Mining

1. Open dashboard: `http://localhost:5000`
2. Select coin from dropdown
3. Click "▶️ Start Mining"

### Stopping Mining

Click "⏹️ Stop Mining" button in the dashboard.

### Switching Coins

1. Stop current mining
2. Select new coin
3. Start mining again

Or use the auto-switch feature for automatic profitability switching.

### Monitoring

The dashboard updates every 5 seconds with:
- Current GPU stats
- Mining hashrate
- Temperature trends
- Profitability data

### Remote Access

To access from other devices on your network:

1. Find your PC's IP address:
   ```cmd
   ipconfig
   ```
2. Access from other device: `http://YOUR_IP:5000`

**Security Note**: Only expose to trusted networks. Authentication is recommended for internet access.

### Overclocking

⚠️ **USE AT YOUR OWN RISK**

Overclocking profiles are in `configs/overclock_profiles.json`.

To apply:
1. Open Settings in dashboard
2. Enable overclocking
3. Profiles auto-apply when switching coins

**Safety limits**:
- Core clock: ±300 MHz max
- Memory clock: +1500 MHz max
- Power limit: 50-120%

## 📡 API Documentation

### GPU Monitoring Endpoints

#### Get All GPU Stats
```http
GET /api/gpu/stats
```

Response:
```json
{
  "gpus": [
    {
      "gpu_id": 0,
      "temperature": 65,
      "fan_speed": 70,
      "power_draw": 95.5,
      "gpu_utilization": 100,
      "memory_used": 4500,
      "memory_total": 6144,
      "core_clock": 1800,
      "memory_clock": 7500
    }
  ],
  "timestamp": 1609459200.0
}
```

#### Get GPU History
```http
GET /api/gpu/history?hours=24
```

### Miner Control Endpoints

#### Start Mining
```http
POST /api/miner/start
Content-Type: application/json

{
  "coin": "RVN",
  "pool": "ravencoin.2miners.com:6060",
  "wallet": "YOUR_WALLET"
}
```

#### Stop Mining
```http
POST /api/miner/stop
```

#### Get Miner Status
```http
GET /api/miner/status
```

Response:
```json
{
  "status": "running",
  "mining": true,
  "coin": "RVN",
  "hashrate": 15.5,
  "shares_accepted": 1234,
  "shares_rejected": 5,
  "uptime": 3600
}
```

### Profitability Endpoints

#### Get Profitability for All Coins
```http
GET /api/profit?electricity_cost=0.12
```

Response:
```json
{
  "RVN": {
    "coin": "RVN",
    "daily_revenue": 1.50,
    "daily_electricity_cost": 0.26,
    "daily_profit": 1.24,
    "monthly_profit": 37.20
  },
  "ETC": { ... }
}
```

#### Get Best Coin to Mine
```http
GET /api/profit/best
```

### Settings Endpoints

#### Get Settings
```http
GET /api/settings
```

#### Update Settings
```http
POST /api/settings
Content-Type: application/json

{
  "mining": {
    "wallet_address": "new_address"
  }
}
```

For complete API documentation, see the interactive API docs at `/api/docs` (coming soon).

## ⚠️ Safety & Disclaimers

### Overclocking Risks

Overclocking can:
- **Reduce GPU lifespan**
- **Cause system instability**
- **Increase power consumption**
- **Void warranties**

**Recommendations**:
- Start with conservative settings
- Monitor temperatures constantly
- Increase gradually and test stability
- Never exceed 85°C
- Use at your own risk

### Temperature Management

The suite includes safety features:

| Temp | Action |
|------|--------|
| >75°C | ⚠️ Warning alert |
| >80°C | 🔥 Increase fan, reduce power |
| >85°C | 🛑 Emergency shutdown |

Always ensure adequate cooling!

### Electricity Costs

Mining profitability depends heavily on electricity costs:

- **Break-even**: ~$0.15-0.20/kWh
- **Profitable**: <$0.12/kWh
- **Not recommended**: >$0.20/kWh

Calculate your costs before starting!

### Legal Considerations

**You are responsible for**:
- Complying with local laws
- Reporting income/taxes
- Respecting residential power limits
- Landlord/HOA regulations

Mining may be illegal in some jurisdictions. Check your local laws!

### Security

- **Never commit wallet addresses** to Git
- **Use .env files** for sensitive data
- **Don't expose dashboard** to internet without authentication
- **Keep miners updated** for security patches
- **Download miners from official sources only**

## 🔧 Troubleshooting

### GPU Not Detected

**Problem**: "No GPU data available"

**Solutions**:
1. Install/update NVIDIA drivers (470+)
2. Install `py3nvml`: `pip install py3nvml`
3. Run as Administrator
4. Restart after driver installation

### Miner Not Starting

**Problem**: "Miner executable not found"

**Solutions**:
1. Download mining software (see `miners/README.md`)
2. Place in `miners/` directory
3. Check filename matches exactly
4. Add antivirus exceptions
5. Install Visual C++ Redistributable

### Dashboard Not Loading

**Problem**: "Cannot access http://localhost:5000"

**Solutions**:
1. Check if Python process is running
2. Verify port 5000 is not in use
3. Check firewall settings
4. Try different port in settings
5. Check console for errors

### Low Hashrate

**Problem**: Hashrate below expected

**Solutions**:
1. Update GPU drivers
2. Check GPU temperature (thermal throttling?)
3. Close other GPU applications
4. Try different overclock profile
5. Check pool connection
6. Verify correct algorithm

### High Temperature

**Problem**: GPU running too hot

**Solutions**:
1. Increase fan speed manually
2. Improve case airflow
3. Clean GPU heatsink/fans
4. Reduce power limit
5. Lower overclocks
6. Check thermal paste

### Notifications Not Working

**Problem**: No Discord/Telegram alerts

**Solutions**:
1. Verify webhook/token is correct
2. Test with "Test Notifications" button
3. Check internet connection
4. Verify bot permissions (Telegram)
5. Enable alerts in settings

### Pool Connection Failed

**Problem**: "Cannot connect to pool"

**Solutions**:
1. Check internet connection
2. Verify pool address in `coins.json`
3. Try alternative pool
4. Check firewall settings
5. Verify wallet address format

### Python Module Errors

**Problem**: "ModuleNotFoundError"

**Solutions**:
```cmd
pip install -r requirements.txt --upgrade
```

If still failing:
```cmd
pip uninstall [module]
pip install [module]
```

## ❓ FAQ

### How much can I earn with a GTX 1660 SUPER?

**It depends** on:
- Electricity cost
- Coin prices
- Network difficulty
- Overclock settings

**Rough estimate** (at $0.10/kWh):
- $0.50 - $2.00 per day after electricity
- $15 - $60 per month

Use the profitability calculator in the dashboard for current estimates.

### Is mining safe for my GPU?

Mining itself won't damage your GPU if:
- Temperatures stay under 80°C
- Adequate cooling is maintained
- Power supply is sufficient
- You don't overclock excessively

Many GPUs have been mining 24/7 for years without issues.

### Can I mine multiple coins simultaneously?

No, you can only mine one coin at a time per GPU. However:
- Auto-switching changes coins based on profitability
- You can manually switch anytime
- Multi-GPU setups can mine different coins (future feature)

### How often should I monitor my mining rig?

**Daily**: Check temperatures and hashrates
**Weekly**: Review earnings and profitability
**Monthly**: Clean dust from GPU/case

The dashboard makes monitoring easy from anywhere!

### What about Ethereum (ETH)?

Ethereum switched to Proof-of-Stake (The Merge) and is no longer minable with GPUs. This suite focuses on currently minable coins like RVN, ETC, ERG, etc.

### Can I use AMD GPUs?

This suite is designed for NVIDIA GPUs using NVML. AMD support would require:
- Different monitoring library (ADL/ROCm)
- Different miners
- Modified overclock module

Not currently supported, but PRs welcome!

### Is this software free?

Yes! MIT License. Free to use, modify, and distribute.

However, mining software (T-Rex, lolMiner) have dev fees (1-2%).

### Can I run this on a laptop?

**Not recommended!** Laptops:
- Have limited cooling
- May throttle heavily
- Could overheat
- Void warranty

Desktop mining rigs only!

### How do I stop mining automatically?

Two options:
1. Use the scheduler feature (specific hours)
2. Set `auto_start: false` in settings
3. Don't use `setup_autostart.bat`

### What about pool fees?

Most pools charge 0.5-1% fees. This is separate from miner dev fees. Total fees typically 1.5-3%.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Setup

```cmd
git clone https://github.com/connectaventaai-design/gpu-mining-suite.git
cd gpu-mining-suite
pip install -r requirements.txt
python backend/app.py
```

### Areas for Contribution

- AMD GPU support
- Additional miners (NBMiner, etc.)
- More coins/algorithms
- Authentication system
- Mobile app
- Docker support
- Linux support
- Translations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Software

- **T-Rex Miner**: Proprietary (1% dev fee)
- **lolMiner**: Proprietary (0.7-1% dev fee)
- **Flask**: BSD-3-Clause
- **Chart.js**: MIT
- **py3nvml**: BSD-3-Clause

## 🙏 Acknowledgments

- NVIDIA for NVML API
- Mining software developers (T-Rex, lolMiner teams)
- CoinGecko for price API
- The cryptocurrency community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/connectaventaai-design/gpu-mining-suite/issues)
- **Discussions**: [GitHub Discussions](https://github.com/connectaventaai-design/gpu-mining-suite/discussions)

## ⚡ Quick Links

- [Installation Guide](#-installation)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [Miner Downloads](miners/README.md)

---

**⚠️ Final Disclaimer**: Cryptocurrency mining involves financial risk. This software is provided "as is" without warranty. The developers are not responsible for any hardware damage, financial losses, or legal issues. Mine responsibly and at your own risk.

**Happy Mining! ⛏️💎**
