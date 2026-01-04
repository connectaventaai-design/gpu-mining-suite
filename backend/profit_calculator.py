"""
Profit Calculator Module
Calculates mining profitability based on live coin prices
"""

import requests
import time
from typing import Dict, Any, Optional
from threading import Lock

class ProfitCalculator:
    def __init__(self):
        self.coin_prices = {}
        self.last_update = 0
        self.cache_duration = 300  # 5 minutes
        self.lock = Lock()
        
        # Expected hashrates for GTX 1660 SUPER (approximate)
        self.expected_hashrates = {
            'RVN': 15.5,      # MH/s for KawPow
            'ETC': 28.0,      # MH/s for Etchash
            'ERG': 90.0,      # MH/s for Autolykos
            'FLUX': 30.0,     # Sol/s for ZelHash
            'KAS': 420.0,     # MH/s for kHeavyHash
            'ALPH': 130.0     # MH/s for Blake3
        }
        
        # Power consumption per algorithm (watts)
        self.power_consumption = {
            'RVN': 90,
            'ETC': 85,
            'ERG': 95,
            'FLUX': 92,
            'KAS': 100,
            'ALPH': 95
        }
    
    def get_coin_price(self, coin_symbol: str, coin_config: Dict[str, Any]) -> Optional[float]:
        """Fetch current coin price from API"""
        api_url = coin_config.get('api_url')
        if not api_url:
            return None
        
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract price from CoinGecko response
            if coin_symbol == 'RVN':
                return data.get('ravencoin', {}).get('usd')
            elif coin_symbol == 'ETC':
                return data.get('ethereum-classic', {}).get('usd')
            elif coin_symbol == 'ERG':
                return data.get('ergo', {}).get('usd')
            elif coin_symbol == 'FLUX':
                return data.get('flux', {}).get('usd')
            elif coin_symbol == 'KAS':
                return data.get('kaspa', {}).get('usd')
            elif coin_symbol == 'ALPH':
                return data.get('alephium', {}).get('usd')
            
            return None
        except Exception as e:
            print(f"Error fetching price for {coin_symbol}: {e}")
            return None
    
    def update_prices(self, coins_config: Dict[str, Any]) -> Dict[str, float]:
        """Update prices for all coins"""
        with self.lock:
            current_time = time.time()
            
            # Use cache if still valid
            if current_time - self.last_update < self.cache_duration and self.coin_prices:
                return self.coin_prices
            
            prices = {}
            coins = coins_config.get('coins', {})
            
            for symbol, config in coins.items():
                price = self.get_coin_price(symbol, config)
                if price:
                    prices[symbol] = price
            
            self.coin_prices = prices
            self.last_update = current_time
            
            return prices
    
    def calculate_daily_revenue(self, coin: str, hashrate: float, price: float) -> float:
        """Calculate daily revenue for a coin"""
        # This is a simplified calculation
        # In reality, you'd need network difficulty, block reward, etc.
        
        # Rough estimates based on typical network stats
        revenue_multipliers = {
            'RVN': 0.5,    # coins per MH/s per day
            'ETC': 0.003,  # ETC per MH/s per day
            'ERG': 0.15,   # ERG per MH/s per day
            'FLUX': 0.08,  # FLUX per Sol/s per day
            'KAS': 25,     # KAS per MH/s per day
            'ALPH': 0.4    # ALPH per MH/s per day
        }
        
        multiplier = revenue_multipliers.get(coin, 0)
        daily_coins = hashrate * multiplier
        daily_revenue = daily_coins * price
        
        return daily_revenue
    
    def calculate_profit(
        self,
        coin: str,
        hashrate: float,
        price: float,
        power_watts: float,
        electricity_cost: float = 0.12
    ) -> Dict[str, Any]:
        """Calculate mining profit including electricity costs"""
        
        # Daily revenue
        daily_revenue = self.calculate_daily_revenue(coin, hashrate, price)
        
        # Daily electricity cost
        daily_kwh = (power_watts * 24) / 1000
        daily_electricity_cost = daily_kwh * electricity_cost
        
        # Net profit
        daily_profit = daily_revenue - daily_electricity_cost
        
        return {
            'coin': coin,
            'hashrate': hashrate,
            'price': price,
            'daily_revenue': daily_revenue,
            'daily_electricity_cost': daily_electricity_cost,
            'daily_profit': daily_profit,
            'monthly_profit': daily_profit * 30,
            'yearly_profit': daily_profit * 365,
            'power_watts': power_watts,
            'electricity_cost_kwh': electricity_cost
        }
    
    def calculate_all_coins_profitability(
        self,
        coins_config: Dict[str, Any],
        electricity_cost: float = 0.12
    ) -> Dict[str, Dict[str, Any]]:
        """Calculate profitability for all supported coins"""
        
        # Update prices
        prices = self.update_prices(coins_config)
        
        results = {}
        
        for coin_symbol in self.expected_hashrates.keys():
            price = prices.get(coin_symbol)
            if not price:
                continue
            
            hashrate = self.expected_hashrates[coin_symbol]
            power = self.power_consumption.get(coin_symbol, 90)
            
            profit_data = self.calculate_profit(
                coin_symbol,
                hashrate,
                price,
                power,
                electricity_cost
            )
            
            results[coin_symbol] = profit_data
        
        return results
    
    def get_most_profitable_coin(
        self,
        coins_config: Dict[str, Any],
        electricity_cost: float = 0.12
    ) -> Optional[str]:
        """Get the most profitable coin to mine"""
        
        profitability = self.calculate_all_coins_profitability(coins_config, electricity_cost)
        
        if not profitability:
            return None
        
        # Find coin with highest daily profit
        best_coin = max(
            profitability.items(),
            key=lambda x: x[1]['daily_profit']
        )
        
        return best_coin[0]
    
    def get_cached_prices(self) -> Dict[str, float]:
        """Get cached coin prices"""
        with self.lock:
            return self.coin_prices.copy()

# Global profit calculator instance
profit_calculator = ProfitCalculator()
