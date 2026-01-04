"""
Automation Module
Handles auto-switching, scheduling, and watchdog functionality
"""

import time
import threading
from datetime import datetime, time as dt_time
from typing import Optional, Callable
from apscheduler.schedulers.background import BackgroundScheduler

class AutomationManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.watchdog_thread = None
        self.watchdog_running = False
        
        self.auto_switch_enabled = False
        self.watchdog_enabled = False
        self.scheduler_enabled = False
        
        self.mining_hours_start = None
        self.mining_hours_end = None
        
        self.callbacks = {
            'on_miner_crash': None,
            'on_low_hashrate': None,
            'on_high_temp': None,
            'get_miner_status': None,
            'get_gpu_stats': None,
            'restart_miner': None,
            'switch_coin': None
        }
        
        self.last_hashrate = 0
        self.hashrate_threshold = 20  # MH/s
        self.low_hashrate_count = 0
        self.restart_attempts = 0
        self.last_restart_time = 0
        
        self.scheduler.start()
    
    def configure(
        self,
        auto_switch: bool = False,
        watchdog: bool = True,
        scheduler: bool = False,
        hashrate_threshold: float = 20,
        mining_hours: str = "00:00-23:59"
    ):
        """Configure automation settings"""
        self.auto_switch_enabled = auto_switch
        self.watchdog_enabled = watchdog
        self.scheduler_enabled = scheduler
        self.hashrate_threshold = hashrate_threshold
        
        # Parse mining hours
        if '-' in mining_hours:
            start, end = mining_hours.split('-')
            try:
                start_h, start_m = map(int, start.split(':'))
                end_h, end_m = map(int, end.split(':'))
                self.mining_hours_start = dt_time(start_h, start_m)
                self.mining_hours_end = dt_time(end_h, end_m)
            except:
                print("Invalid mining hours format")
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback function for automation events"""
        if event in self.callbacks:
            self.callbacks[event] = callback
    
    def start_watchdog(self, check_interval: int = 30):
        """Start watchdog monitoring"""
        if not self.watchdog_enabled:
            return
        
        if self.watchdog_running:
            return
        
        self.watchdog_running = True
        
        def watchdog_loop():
            while self.watchdog_running:
                try:
                    self._check_miner_health()
                    self._check_temperature()
                    time.sleep(check_interval)
                except Exception as e:
                    print(f"Watchdog error: {e}")
                    time.sleep(check_interval)
        
        self.watchdog_thread = threading.Thread(target=watchdog_loop, daemon=True)
        self.watchdog_thread.start()
        print("Watchdog started")
    
    def stop_watchdog(self):
        """Stop watchdog monitoring"""
        self.watchdog_running = False
        if self.watchdog_thread:
            self.watchdog_thread.join(timeout=5)
        print("Watchdog stopped")
    
    def _check_miner_health(self):
        """Check if miner is healthy"""
        if not self.callbacks['get_miner_status']:
            return
        
        status = self.callbacks['get_miner_status']()
        
        if not status:
            return
        
        # Check if miner crashed
        if status.get('status') == 'crashed' and status.get('coin'):
            print("⚠️ Miner crashed detected!")
            
            # Notify
            if self.callbacks['on_miner_crash']:
                self.callbacks['on_miner_crash'](status.get('coin'))
            
            # Attempt restart with exponential backoff
            current_time = time.time()
            time_since_last_restart = current_time - self.last_restart_time
            
            if time_since_last_restart > 300:  # Reset counter after 5 minutes
                self.restart_attempts = 0
            
            if self.restart_attempts < 5:
                wait_time = min(60 * (2 ** self.restart_attempts), 600)  # Max 10 min
                print(f"Waiting {wait_time}s before restart attempt {self.restart_attempts + 1}")
                time.sleep(wait_time)
                
                if self.callbacks['restart_miner']:
                    self.callbacks['restart_miner']()
                    self.restart_attempts += 1
                    self.last_restart_time = current_time
            else:
                print("❌ Maximum restart attempts reached. Manual intervention required.")
        
        # Check for low hashrate
        if status.get('mining'):
            hashrate = status.get('hashrate', 0)
            
            if hashrate < self.hashrate_threshold:
                self.low_hashrate_count += 1
                
                if self.low_hashrate_count >= 2:  # 2 consecutive low readings
                    print(f"⚠️ Low hashrate detected: {hashrate:.2f} MH/s")
                    
                    if self.callbacks['on_low_hashrate']:
                        self.callbacks['on_low_hashrate'](
                            status.get('coin'),
                            hashrate,
                            self.hashrate_threshold
                        )
                    
                    # Restart if enabled
                    if self.callbacks['restart_miner']:
                        print("Restarting miner due to low hashrate...")
                        self.callbacks['restart_miner']()
                        self.low_hashrate_count = 0
            else:
                self.low_hashrate_count = 0
            
            self.last_hashrate = hashrate
    
    def _check_temperature(self):
        """Check GPU temperatures"""
        if not self.callbacks['get_gpu_stats']:
            return
        
        stats = self.callbacks['get_gpu_stats']()
        
        if not stats:
            return
        
        for gpu_stat in stats.get('gpus', []):
            temp = gpu_stat.get('temperature', 0)
            gpu_id = gpu_stat.get('gpu_id', 0)
            
            # Critical temperature
            if temp >= 85:
                print(f"🔥 CRITICAL: GPU {gpu_id} temperature: {temp}°C - Emergency stop!")
                if self.callbacks['on_high_temp']:
                    self.callbacks['on_high_temp'](gpu_id, temp)
                # Could trigger emergency miner stop here
            
            # High temperature warning
            elif temp >= 80:
                print(f"⚠️ WARNING: GPU {gpu_id} temperature: {temp}°C")
                if self.callbacks['on_high_temp']:
                    self.callbacks['on_high_temp'](gpu_id, temp)
    
    def should_be_mining(self) -> bool:
        """Check if mining should be active based on schedule"""
        if not self.scheduler_enabled:
            return True
        
        if not self.mining_hours_start or not self.mining_hours_end:
            return True
        
        current_time = datetime.now().time()
        
        # Handle overnight schedules (e.g., 22:00-06:00)
        if self.mining_hours_start > self.mining_hours_end:
            return current_time >= self.mining_hours_start or current_time <= self.mining_hours_end
        else:
            return self.mining_hours_start <= current_time <= self.mining_hours_end
    
    def schedule_profit_check(self, interval_minutes: int = 60):
        """Schedule periodic profitability checks for auto-switching"""
        if not self.auto_switch_enabled:
            return
        
        def check_and_switch():
            if not self.callbacks['switch_coin']:
                return
            
            # This would call the profit calculator to find best coin
            # and switch if different from current
            print("Checking coin profitability...")
            # Implementation would go here
        
        self.scheduler.add_job(
            check_and_switch,
            'interval',
            minutes=interval_minutes,
            id='profit_check'
        )
    
    def schedule_mining_hours(self):
        """Schedule mining start/stop based on configured hours"""
        if not self.scheduler_enabled:
            return
        
        # This would schedule jobs based on mining_hours_start and mining_hours_end
        print("Mining schedule configured")
    
    def shutdown(self):
        """Shutdown automation systems"""
        self.stop_watchdog()
        self.scheduler.shutdown()

# Global automation manager instance
automation_manager = AutomationManager()
