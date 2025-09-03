# This script defines the `SystemMonitor` class, which provides
# functionality for real-time monitoring of system resources such as
# CPU, memory, and GPU (if NVIDIA GPU and `pynvml` are available).
# It runs monitoring in a separate thread to collect performance
# statistics and also offers a static method to retrieve static
# system information.

import time
import psutil
import threading
import platform
import sys

class SystemMonitor:
    """
    Monitors system resources (CPU, memory, GPU) in real-time.
    """
    def __init__(self, interval: float = 0.5):
        """
        Initializes the SystemMonitor.

        Args:
            interval (float): The time interval (in seconds) between each resource sampling. Defaults to 0.5.
        """
        self.interval = interval
        self.system_stats = []
        self.monitoring = False
        self.monitor_thread = None
        self.gpu_available = False
        try:
            import pynvml
            pynvml.nvmlInit()
            self.gpu_available = True
        except Exception as e:
            # pynvml might not be installed or NVIDIA driver not found
            if 'pynvml' in str(e):
                print("Warning: pynvml not found. GPU monitoring will be disabled. Please install it with 'pip install nvidia-ml-py'.")
            else:
                print(f"Warning: Could not initialize NVML. GPU monitoring will be disabled. Error: {e}")
            self.gpu_available = False

    def _monitor_system_loop(self):
        """
        Internal loop to continuously monitor system resources.
        This method runs in a separate thread.
        """
        while self.monitoring:
            stats = {
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent(interval=None), # Non-blocking call
                'memory_percent': psutil.virtual_memory().percent,
                'memory_used_gb': psutil.virtual_memory().used / (1024**3)
            }
            
            if self.gpu_available:
                try:
                    import pynvml
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0) # Assuming single GPU for simplicity
                    gpu_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    stats['gpu_memory_used_gb'] = gpu_info.used / (1024**3)
                    stats['gpu_memory_total_gb'] = gpu_info.total / (1024**3)
                    stats['gpu_utilization'] = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                except Exception as e:
                    # If pynvml fails during monitoring, just skip GPU stats for this sample
                    if self.monitoring: # Only print if still monitoring
                        print(f"Warning: Error collecting GPU stats: {e}", file=sys.stderr)
                    pass
                    
            self.system_stats.append(stats)
            time.sleep(self.interval)

    def start(self):
        """
        Starts the system monitoring in a separate thread.
        """
        self.system_stats = []
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_system_loop)
        self.monitor_thread.daemon = True # Allow main program to exit even if thread is running
        self.monitor_thread.start()

    def stop(self):
        """
        Stops the system monitoring thread and returns collected statistics.

        Returns:
            list: A list of dictionaries, where each dictionary contains
                  resource statistics sampled at a specific timestamp.
        """
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1) # Wait for thread to finish
        return self.system_stats

    @staticmethod
    def get_system_info() -> dict:
        """
        Gathers static system information including OS, processor, Python version,
        total memory, CPU core counts, and GPU information (if available).

        Returns:
            dict: A dictionary containing static system information.
        """
        info = {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'total_memory_gb': psutil.virtual_memory().total / (1024**3),
            'cpu_count_physical': psutil.cpu_count(logical=False),
            'cpu_count_logical': psutil.cpu_count(logical=True)
        }
        try:
            import pynvml
            pynvml.nvmlInit()
            gpu_count = pynvml.nvmlDeviceGetCount()
            gpu_info = []
            for i in range(gpu_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_info.append({
                    'index': i,
                    'name': name,
                    'memory_total_gb': memory_info.total / (1024**3),
                    'memory_free_gb': memory_info.free / (1024**3)
                })
            info['gpu_info'] = gpu_info
        except Exception as e:
            info['gpu_info'] = f"Not available ({e})"
        return info