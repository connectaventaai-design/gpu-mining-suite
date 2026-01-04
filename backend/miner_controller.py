"""
Miner Controller Module
Controls mining software (start, stop, restart, monitor)
"""

import subprocess
import os
import time
import psutil
import json
from typing import Dict, Any, Optional
from datetime import datetime

class MinerController:
    def __init__(self):
        self.process = None
        self.current_coin = None
        self.current_pool = None
        self.current_wallet = None
        self.start_time = None
        self.miner_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'miners')
        self.status = 'stopped'
        self.hashrate = 0
        self.shares_accepted = 0
        self.shares_rejected = 0
        self.session_id = None
    
    def start_mining(
        self,
        coin: str,
        algorithm: str,
        pool: str,
        wallet: str,
        worker_name: str = 'worker',
        miner: str = 't-rex'
    ) -> bool:
        """Start mining process"""
        
        if self.is_mining():
            print("Miner is already running")
            return False
        
        # Build miner command
        cmd = self._build_miner_command(coin, algorithm, pool, wallet, worker_name, miner)
        
        if not cmd:
            print(f"Could not build command for miner: {miner}")
            return False
        
        try:
            # Start miner process
            self.process = subprocess.Popen(
                cmd,
                cwd=self.miner_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            self.current_coin = coin
            self.current_pool = pool
            self.current_wallet = wallet
            self.start_time = datetime.now()
            self.status = 'running'
            self.session_id = f"{coin}_{int(time.time())}"
            
            print(f"Started mining {coin} with {miner}")
            return True
        except FileNotFoundError:
            print(f"Miner executable not found. Please download {miner} to the miners/ directory")
            self.status = 'error'
            return False
        except Exception as e:
            print(f"Error starting miner: {e}")
            self.status = 'error'
            return False
    
    def stop_mining(self) -> bool:
        """Stop mining process"""
        if not self.process:
            return True
        
        try:
            # Terminate process gracefully
            self.process.terminate()
            
            # Wait up to 10 seconds for process to end
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if still running
                self.process.kill()
                self.process.wait()
            
            self.process = None
            self.status = 'stopped'
            self.current_coin = None
            self.start_time = None
            
            print("Mining stopped")
            return True
        except Exception as e:
            print(f"Error stopping miner: {e}")
            return False
    
    def restart_mining(self) -> bool:
        """Restart mining with current settings"""
        if not self.current_coin:
            return False
        
        coin = self.current_coin
        pool = self.current_pool
        wallet = self.current_wallet
        
        self.stop_mining()
        time.sleep(2)
        
        # Would need to re-fetch coin config here
        # For now, just return False
        print("Restart requires coin configuration")
        return False
    
    def is_mining(self) -> bool:
        """Check if miner is currently running"""
        if not self.process:
            return False
        
        # Check if process is still alive
        if self.process.poll() is not None:
            # Process has ended
            self.status = 'crashed'
            self.process = None
            return False
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current miner status"""
        is_running = self.is_mining()
        
        uptime = 0
        if self.start_time and is_running:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'status': self.status if is_running else 'stopped',
            'mining': is_running,
            'coin': self.current_coin,
            'pool': self.current_pool,
            'uptime': uptime,
            'hashrate': self.hashrate,
            'shares_accepted': self.shares_accepted,
            'shares_rejected': self.shares_rejected,
            'session_id': self.session_id
        }
    
    def update_stats(self, hashrate: float = 0, accepted: int = 0, rejected: int = 0):
        """Update mining statistics"""
        self.hashrate = hashrate
        self.shares_accepted = accepted
        self.shares_rejected = rejected
    
    def _build_miner_command(
        self,
        coin: str,
        algorithm: str,
        pool: str,
        wallet: str,
        worker_name: str,
        miner: str
    ) -> Optional[list]:
        """Build miner command based on miner type"""
        
        if miner == 't-rex':
            # T-Rex Miner command
            exe = 't-rex.exe' if os.name == 'nt' else 't-rex'
            return [
                os.path.join(self.miner_path, exe),
                '-a', algorithm,
                '-o', f"stratum+tcp://{pool}",
                '-u', f"{wallet}.{worker_name}",
                '-p', 'x',
                '--api-bind-http', '127.0.0.1:4067'
            ]
        elif miner == 'lolminer':
            # lolMiner command
            exe = 'lolMiner.exe' if os.name == 'nt' else 'lolMiner'
            return [
                os.path.join(self.miner_path, exe),
                '--algo', algorithm.upper(),
                '--pool', pool,
                '--user', f"{wallet}.{worker_name}",
                '--apiport', '4068'
            ]
        elif miner == 'gminer':
            # GMiner command
            exe = 'miner.exe' if os.name == 'nt' else 'miner'
            return [
                os.path.join(self.miner_path, exe),
                '--algo', algorithm,
                '--server', pool.split(':')[0],
                '--port', pool.split(':')[1] if ':' in pool else '3333',
                '--user', f"{wallet}.{worker_name}",
                '--api', '4069'
            ]
        
        return None
    
    def get_miner_api_stats(self) -> Optional[Dict[str, Any]]:
        """Get statistics from miner's API"""
        # Try T-Rex API
        try:
            import requests
            response = requests.get('http://127.0.0.1:4067/summary', timeout=2)
            if response.status_code == 200:
                data = response.json()
                # Parse T-Rex response
                return self._parse_trex_response(data)
        except:
            pass
        
        # Try lolMiner API
        try:
            import requests
            response = requests.get('http://127.0.0.1:4068', timeout=2)
            if response.status_code == 200:
                data = response.json()
                return self._parse_lolminer_response(data)
        except:
            pass
        
        return None
    
    def _parse_trex_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse T-Rex miner API response"""
        try:
            hashrate = data.get('hashrate', 0) / 1000000  # Convert to MH/s
            accepted = data.get('accepted_count', 0)
            rejected = data.get('rejected_count', 0)
            
            return {
                'hashrate': hashrate,
                'accepted': accepted,
                'rejected': rejected
            }
        except:
            return {}
    
    def _parse_lolminer_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse lolMiner API response"""
        try:
            gpus = data.get('GPUs', [])
            if gpus:
                hashrate = sum(gpu.get('Performance', 0) for gpu in gpus)
                accepted = data.get('Session', {}).get('Accepted', 0)
                rejected = data.get('Session', {}).get('Rejected', 0)
                
                return {
                    'hashrate': hashrate,
                    'accepted': accepted,
                    'rejected': rejected
                }
        except:
            return {}
        
        return {}

# Global miner controller instance
miner_controller = MinerController()
