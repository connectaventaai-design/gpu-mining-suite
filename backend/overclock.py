"""
Overclock Management Module
WARNING: Overclocking can damage hardware. Use at your own risk.
This is a placeholder implementation as actual overclocking on Windows
requires MSI Afterburner or similar tools with command line interfaces.
"""

import subprocess
import os
from typing import Dict, Any, Optional

class OverclockManager:
    def __init__(self):
        self.current_profile = {}
        self.afterburner_path = None
        self.enabled = False
        
        # Try to find MSI Afterburner
        self._detect_afterburner()
    
    def _detect_afterburner(self):
        """Detect if MSI Afterburner is installed"""
        possible_paths = [
            r"C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe",
            r"C:\Program Files\MSI Afterburner\MSIAfterburner.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.afterburner_path = path
                print(f"Found MSI Afterburner at: {path}")
                return True
        
        print("MSI Afterburner not found. Overclocking features will be disabled.")
        print("To enable overclocking, install MSI Afterburner from:")
        print("https://www.msi.com/Landing/afterburner")
        return False
    
    def apply_profile(
        self,
        gpu_id: int,
        core_clock: int = 0,
        memory_clock: int = 0,
        power_limit: int = 100,
        fan_speed: int = -1
    ) -> bool:
        """
        Apply overclock profile to GPU
        
        Args:
            gpu_id: GPU index
            core_clock: Core clock offset in MHz (can be negative)
            memory_clock: Memory clock offset in MHz
            power_limit: Power limit percentage (0-100)
            fan_speed: Fan speed percentage (0-100), -1 for auto
        
        Returns:
            True if successful, False otherwise
        """
        
        if not self.enabled and not self.afterburner_path:
            print("⚠️ Overclocking is disabled or MSI Afterburner not found")
            print("This is a simulated overclock application.")
            
            # Store profile for display purposes
            self.current_profile[gpu_id] = {
                'core_clock': core_clock,
                'memory_clock': memory_clock,
                'power_limit': power_limit,
                'fan_speed': fan_speed
            }
            return True
        
        # In a real implementation, this would use MSI Afterburner's CLI
        # or NVAPI to apply settings
        
        print(f"Applying overclock profile to GPU {gpu_id}:")
        print(f"  Core Clock: {core_clock:+d} MHz")
        print(f"  Memory Clock: {memory_clock:+d} MHz")
        print(f"  Power Limit: {power_limit}%")
        print(f"  Fan Speed: {'Auto' if fan_speed == -1 else f'{fan_speed}%'}")
        
        self.current_profile[gpu_id] = {
            'core_clock': core_clock,
            'memory_clock': memory_clock,
            'power_limit': power_limit,
            'fan_speed': fan_speed
        }
        
        return True
    
    def apply_coin_profile(
        self,
        gpu_id: int,
        gpu_model: str,
        coin: str,
        profile_data: Dict[str, Any]
    ) -> bool:
        """Apply overclock profile for a specific coin"""
        
        if not profile_data:
            print(f"No overclock profile found for {coin} on {gpu_model}")
            return False
        
        print(f"Applying {coin} profile: {profile_data.get('name', coin)}")
        
        return self.apply_profile(
            gpu_id,
            core_clock=profile_data.get('core_clock', 0),
            memory_clock=profile_data.get('memory_clock', 0),
            power_limit=profile_data.get('power_limit', 100),
            fan_speed=profile_data.get('fan_speed', -1)
        )
    
    def reset_to_default(self, gpu_id: int) -> bool:
        """Reset GPU to default clocks"""
        print(f"Resetting GPU {gpu_id} to default settings")
        
        return self.apply_profile(
            gpu_id,
            core_clock=0,
            memory_clock=0,
            power_limit=100,
            fan_speed=-1
        )
    
    def get_current_profile(self, gpu_id: int) -> Dict[str, Any]:
        """Get currently applied profile"""
        return self.current_profile.get(gpu_id, {})
    
    def get_all_profiles(self) -> Dict[int, Dict[str, Any]]:
        """Get all currently applied profiles"""
        return self.current_profile.copy()
    
    def enable_overclocking(self):
        """Enable overclocking features"""
        self.enabled = True
        print("⚠️ Overclocking enabled. Use at your own risk!")
    
    def disable_overclocking(self):
        """Disable overclocking features"""
        self.enabled = False
        print("Overclocking disabled")
    
    def validate_profile(
        self,
        core_clock: int,
        memory_clock: int,
        power_limit: int
    ) -> tuple[bool, str]:
        """Validate overclock settings for safety"""
        
        # Conservative limits
        if abs(core_clock) > 300:
            return False, "Core clock offset too high (max ±300 MHz)"
        
        if memory_clock > 1500 or memory_clock < -500:
            return False, "Memory clock offset out of safe range (-500 to +1500 MHz)"
        
        if power_limit < 50 or power_limit > 120:
            return False, "Power limit out of safe range (50-120%)"
        
        return True, "Profile is within safe limits"

# Global overclock manager instance
overclock_manager = OverclockManager()
