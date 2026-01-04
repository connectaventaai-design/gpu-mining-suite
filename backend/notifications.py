"""
Notifications Module
Handles Discord and Telegram notifications
"""

import requests
from typing import Optional, Dict, Any
from datetime import datetime

class NotificationManager:
    def __init__(self):
        self.discord_webhook = None
        self.telegram_token = None
        self.telegram_chat_id = None
        self.enabled = False
    
    def configure(
        self,
        discord_webhook: str = "",
        telegram_token: str = "",
        telegram_chat_id: str = "",
        enabled: bool = True
    ):
        """Configure notification settings"""
        self.discord_webhook = discord_webhook if discord_webhook else None
        self.telegram_token = telegram_token if telegram_token else None
        self.telegram_chat_id = telegram_chat_id if telegram_chat_id else None
        self.enabled = enabled
    
    def send_discord(self, message: str, embed: Optional[Dict[str, Any]] = None) -> bool:
        """Send notification to Discord"""
        if not self.enabled or not self.discord_webhook:
            return False
        
        try:
            data = {"content": message}
            
            if embed:
                data["embeds"] = [embed]
            
            response = requests.post(
                self.discord_webhook,
                json=data,
                timeout=10
            )
            
            return response.status_code == 204
        except Exception as e:
            print(f"Error sending Discord notification: {e}")
            return False
    
    def send_telegram(self, message: str) -> bool:
        """Send notification to Telegram"""
        if not self.enabled or not self.telegram_token or not self.telegram_chat_id:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending Telegram notification: {e}")
            return False
    
    def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "info",
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send alert to all configured channels"""
        
        if not self.enabled:
            return False
        
        # Format message with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {title}\n{message}"
        
        # Determine color based on severity
        color_map = {
            "info": 0x3498db,      # Blue
            "warning": 0xf39c12,   # Orange
            "error": 0xe74c3c,     # Red
            "success": 0x2ecc71    # Green
        }
        color = color_map.get(severity, 0x95a5a6)
        
        # Send to Discord with embed
        discord_sent = False
        if self.discord_webhook:
            embed = {
                "title": title,
                "description": message,
                "color": color,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "GPU Mining Suite"
                }
            }
            
            if details:
                embed["fields"] = [
                    {"name": key, "value": str(value), "inline": True}
                    for key, value in details.items()
                ]
            
            discord_sent = self.send_discord("", embed)
        
        # Send to Telegram
        telegram_sent = False
        if self.telegram_token and self.telegram_chat_id:
            telegram_message = f"<b>{title}</b>\n{message}"
            
            if details:
                telegram_message += "\n\n"
                for key, value in details.items():
                    telegram_message += f"<b>{key}:</b> {value}\n"
            
            telegram_sent = self.send_telegram(telegram_message)
        
        return discord_sent or telegram_sent
    
    def alert_high_temperature(self, gpu_id: int, temperature: float):
        """Send high temperature alert"""
        self.send_alert(
            "⚠️ High GPU Temperature",
            f"GPU {gpu_id} temperature is high!",
            "warning",
            {
                "GPU": gpu_id,
                "Temperature": f"{temperature}°C",
                "Action": "Check cooling system"
            }
        )
    
    def alert_miner_crashed(self, coin: str):
        """Send miner crashed alert"""
        self.send_alert(
            "❌ Miner Crashed",
            f"Mining process for {coin} has stopped unexpectedly.",
            "error",
            {
                "Coin": coin,
                "Action": "Attempting auto-restart"
            }
        )
    
    def alert_low_hashrate(self, coin: str, hashrate: float, expected: float):
        """Send low hashrate alert"""
        self.send_alert(
            "⚠️ Low Hashrate Detected",
            f"Hashrate for {coin} is below expected.",
            "warning",
            {
                "Coin": coin,
                "Current Hashrate": f"{hashrate:.2f} MH/s",
                "Expected": f"{expected:.2f} MH/s",
                "Difference": f"{((hashrate/expected - 1) * 100):.1f}%"
            }
        )
    
    def alert_mining_started(self, coin: str, pool: str):
        """Send mining started notification"""
        self.send_alert(
            "✅ Mining Started",
            f"Started mining {coin}",
            "success",
            {
                "Coin": coin,
                "Pool": pool
            }
        )
    
    def alert_mining_stopped(self, coin: str, duration: float):
        """Send mining stopped notification"""
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        
        self.send_alert(
            "🛑 Mining Stopped",
            f"Stopped mining {coin}",
            "info",
            {
                "Coin": coin,
                "Duration": f"{hours}h {minutes}m"
            }
        )
    
    def test_notifications(self) -> Dict[str, bool]:
        """Test notification channels"""
        results = {}
        
        if self.discord_webhook:
            results['discord'] = self.send_discord("Test notification from GPU Mining Suite ✅")
        else:
            results['discord'] = False
        
        if self.telegram_token and self.telegram_chat_id:
            results['telegram'] = self.send_telegram("<b>Test notification</b> from GPU Mining Suite ✅")
        else:
            results['telegram'] = False
        
        return results

# Global notification manager instance
notification_manager = NotificationManager()
