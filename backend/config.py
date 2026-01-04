"""
Configuration Management Module
Handles loading and saving configuration files
"""

import json
import os
from typing import Dict, Any

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configs')

class Config:
    def __init__(self):
        self.settings = self.load_json('settings.json')
        self.coins = self.load_json('coins.json')
        self.overclock_profiles = self.load_json('overclock_profiles.json')
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        """Load a JSON configuration file"""
        filepath = os.path.join(CONFIG_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {filename} not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing {filename}: {e}")
            return {}
    
    def save_json(self, filename: str, data: Dict[str, Any]) -> bool:
        """Save data to a JSON configuration file"""
        filepath = os.path.join(CONFIG_DIR, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            return False
    
    def get_setting(self, *keys):
        """Get a setting value using dot notation"""
        value = self.settings
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    def set_setting(self, value, *keys):
        """Set a setting value using dot notation"""
        data = self.settings
        for key in keys[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]
        data[keys[-1]] = value
        return self.save_json('settings.json', self.settings)
    
    def get_coin_config(self, coin_symbol: str) -> Dict[str, Any]:
        """Get configuration for a specific coin"""
        return self.coins.get('coins', {}).get(coin_symbol, {})
    
    def get_overclock_profile(self, gpu_model: str, coin_symbol: str) -> Dict[str, Any]:
        """Get overclock profile for a specific GPU and coin"""
        return self.overclock_profiles.get(gpu_model, {}).get(coin_symbol, {})
    
    def reload(self):
        """Reload all configuration files"""
        self.settings = self.load_json('settings.json')
        self.coins = self.load_json('coins.json')
        self.overclock_profiles = self.load_json('overclock_profiles.json')

# Global config instance
config = Config()
