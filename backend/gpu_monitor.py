"""
GPU Monitoring Module
Handles NVIDIA GPU monitoring using py3nvml
"""

import time
import threading
from typing import List, Dict, Any, Optional

try:
    from py3nvml import py3nvml as nvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False
    print("Warning: py3nvml not available. GPU monitoring will be limited.")

class GPUMonitor:
    def __init__(self):
        self.initialized = False
        self.gpu_count = 0
        self.gpu_handles = []
        self.monitoring = False
        self.monitor_thread = None
        self.latest_stats = {}
        
        if NVML_AVAILABLE:
            self.initialize()
    
    def initialize(self):
        """Initialize NVML and detect GPUs"""
        if not NVML_AVAILABLE:
            return False
        
        try:
            nvml.nvmlInit()
            self.gpu_count = nvml.nvmlDeviceGetCount()
            
            # Get handles for all GPUs
            for i in range(self.gpu_count):
                handle = nvml.nvmlDeviceGetHandleByIndex(i)
                self.gpu_handles.append(handle)
            
            self.initialized = True
            print(f"Initialized NVML. Found {self.gpu_count} GPU(s)")
            return True
        except Exception as e:
            print(f"Error initializing NVML: {e}")
            return False
    
    def shutdown(self):
        """Shutdown NVML"""
        if self.initialized and NVML_AVAILABLE:
            try:
                nvml.nvmlShutdown()
                self.initialized = False
            except:
                pass
    
    def get_gpu_info(self, gpu_id: int = 0) -> Dict[str, Any]:
        """Get basic GPU information"""
        if not self.initialized or gpu_id >= self.gpu_count:
            return self._get_mock_gpu_info(gpu_id)
        
        try:
            handle = self.gpu_handles[gpu_id]
            name = nvml.nvmlDeviceGetName(handle)
            
            # Handle both bytes and string return types
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            
            memory_info = nvml.nvmlDeviceGetMemoryInfo(handle)
            
            return {
                'id': gpu_id,
                'name': name,
                'memory_total': memory_info.total // (1024 * 1024),  # MB
                'driver_version': self._get_driver_version(),
                'cuda_version': self._get_cuda_version()
            }
        except Exception as e:
            print(f"Error getting GPU info: {e}")
            return self._get_mock_gpu_info(gpu_id)
    
    def get_gpu_stats(self, gpu_id: int = 0) -> Dict[str, Any]:
        """Get current GPU statistics"""
        if not self.initialized or gpu_id >= self.gpu_count:
            return self._get_mock_gpu_stats(gpu_id)
        
        try:
            handle = self.gpu_handles[gpu_id]
            
            # Temperature
            try:
                temperature = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
            except:
                temperature = 0
            
            # Fan speed
            try:
                fan_speed = nvml.nvmlDeviceGetFanSpeed(handle)
            except:
                fan_speed = 0
            
            # Power draw
            try:
                power_draw = nvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert mW to W
            except:
                power_draw = 0
            
            # Utilization
            try:
                utilization = nvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_utilization = utilization.gpu
                memory_utilization = utilization.memory
            except:
                gpu_utilization = 0
                memory_utilization = 0
            
            # Memory
            try:
                memory_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                memory_used = memory_info.used // (1024 * 1024)  # MB
                memory_total = memory_info.total // (1024 * 1024)  # MB
            except:
                memory_used = 0
                memory_total = 0
            
            # Clock speeds
            try:
                core_clock = nvml.nvmlDeviceGetClockInfo(handle, nvml.NVML_CLOCK_GRAPHICS)
                memory_clock = nvml.nvmlDeviceGetClockInfo(handle, nvml.NVML_CLOCK_MEM)
            except:
                core_clock = 0
                memory_clock = 0
            
            # Power limit
            try:
                power_limit = nvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000.0  # Convert mW to W
            except:
                power_limit = 0
            
            return {
                'gpu_id': gpu_id,
                'temperature': temperature,
                'fan_speed': fan_speed,
                'power_draw': power_draw,
                'power_limit': power_limit,
                'gpu_utilization': gpu_utilization,
                'memory_utilization': memory_utilization,
                'memory_used': memory_used,
                'memory_total': memory_total,
                'core_clock': core_clock,
                'memory_clock': memory_clock,
                'timestamp': time.time()
            }
        except Exception as e:
            print(f"Error getting GPU stats: {e}")
            return self._get_mock_gpu_stats(gpu_id)
    
    def get_all_gpu_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all GPUs"""
        stats = []
        for i in range(max(1, self.gpu_count)):
            stats.append(self.get_gpu_stats(i))
        return stats
    
    def _get_driver_version(self) -> str:
        """Get NVIDIA driver version"""
        try:
            version = nvml.nvmlSystemGetDriverVersion()
            if isinstance(version, bytes):
                version = version.decode('utf-8')
            return version
        except:
            return "Unknown"
    
    def _get_cuda_version(self) -> str:
        """Get CUDA version"""
        try:
            version = nvml.nvmlSystemGetCudaDriverVersion()
            major = version // 1000
            minor = (version % 1000) // 10
            return f"{major}.{minor}"
        except:
            return "Unknown"
    
    def _get_mock_gpu_info(self, gpu_id: int) -> Dict[str, Any]:
        """Return mock GPU info when NVML is not available"""
        return {
            'id': gpu_id,
            'name': 'NVIDIA GeForce GTX 1660 SUPER (Simulated)',
            'memory_total': 6144,
            'driver_version': 'Unknown',
            'cuda_version': 'Unknown'
        }
    
    def _get_mock_gpu_stats(self, gpu_id: int) -> Dict[str, Any]:
        """Return mock GPU stats when NVML is not available"""
        import random
        return {
            'gpu_id': gpu_id,
            'temperature': random.randint(50, 75),
            'fan_speed': random.randint(60, 80),
            'power_draw': random.uniform(80, 120),
            'power_limit': 125,
            'gpu_utilization': random.randint(80, 100),
            'memory_utilization': random.randint(60, 90),
            'memory_used': random.randint(3000, 5000),
            'memory_total': 6144,
            'core_clock': random.randint(1700, 1900),
            'memory_clock': random.randint(7000, 8000),
            'timestamp': time.time()
        }
    
    def start_monitoring(self, interval: int = 5, callback=None):
        """Start continuous monitoring in background thread"""
        if self.monitoring:
            return
        
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    stats = self.get_all_gpu_stats()
                    self.latest_stats = {
                        'gpus': stats,
                        'timestamp': time.time()
                    }
                    
                    if callback:
                        callback(self.latest_stats)
                    
                    time.sleep(interval)
                except Exception as e:
                    print(f"Error in monitoring loop: {e}")
                    time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
    
    def get_latest_stats(self) -> Dict[str, Any]:
        """Get the latest cached statistics"""
        if not self.latest_stats:
            return {
                'gpus': self.get_all_gpu_stats(),
                'timestamp': time.time()
            }
        return self.latest_stats

# Global GPU monitor instance
gpu_monitor = GPUMonitor()
