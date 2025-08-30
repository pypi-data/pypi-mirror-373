"""
Resource monitoring utilities
"""

import time
import tracemalloc
import logging
from typing import Optional, Dict, Any

try:
    import psutil
except ImportError:
    psutil = None
    print("Warning: psutil is not installed. Some monitoring features will be unavailable.")

from .snapshots import ResourceSnapshot, MemorySnapshot

logger = logging.getLogger("MonitoringLogger")

class ResourceMonitor:
    """Utility class for capturing resource snapshots"""

    @staticmethod
    def get_process() -> Optional[psutil.Process]:
        """Get the current process object"""
        if psutil is None:
            return None
        try:
            return psutil.Process()
        except psutil.Error:
            return None
        
    @staticmethod
    def capture_resources() -> Optional[ResourceSnapshot]:
        """Capture current resource usage snapshot"""
        process = ResourceMonitor.get_process()
        if process is None:
            return None
        
        try:
            # Get memory info
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()

            # Get I/O info
            try:
                io_counters = process.io_counters()
                io_read_bytes = io_counters.read_bytes
                io_write_bytes = io_counters.write_bytes
                io_read_count = io_counters.read_count
                io_write_count = io_counters.write_count
            except (psutil.Error, AttributeError):
                io_read_bytes = io_write_bytes = io_read_count = io_write_count = 0
            
            # Get network info (system-wide)
            try:
                net_io = psutil.net_io_counters()
                net_bytes_sent = net_io.bytes_sent if net_io else 0
                net_bytes_recv = net_io.bytes_recv if net_io else 0
            except (psutil.Error):
                net_bytes_sent = net_bytes_recv = 0
            
            # Get file/thread info
            try:
                open_files = len(process.open_files())
            except (psutil.Error, OSError):
                open_files = 0
            
            # Get thread info
            try:
                num_threads = process.num_threads()
            except (psutil.Error, OSError):
                num_threads = 0
            
            return ResourceSnapshot(
                timestamp=time.time(),
                cpu_percent=psutil.cpu_percent(),
                memory_rss=memory_info.rss,
                memory_vms=memory_info.vms,
                memory_percent=memory_percent,
                io_read_bytes=io_read_bytes,
                io_write_bytes=io_write_bytes,
                io_read_count=io_read_count,
                io_write_count=io_write_count,
                net_bytes_sent=net_bytes_sent,
                net_bytes_recv=net_bytes_recv,
                open_files=open_files,
                num_threads=num_threads
            )
        except psutil.Error as e:
            logger.warning(f"Failed to capture resource snapshot: {e}")
            return None
        
    @staticmethod
    def capture_memory() -> MemorySnapshot:
        """Capture current memory usage snapshot"""
        current_time = time.time()

        # Get tracemalloc info if available
        if tracemalloc.is_tracing():
            current_traced, peak_traced = tracemalloc.get_traced_memory()
            traced_memory = (current_traced, peak_traced)
        else:
            traced_memory = (0, 0)

        # Get process memory info
        process = ResourceMonitor.get_process()
        if process:
            try:
                memory_info = process.memory_info()
                current_size = memory_info.rss
                peak_size = getattr(memory_info, "peak_rss", memory_info.rss)
            except psutil.Error:
                current_size = peak_size = 0
        else:
            current_size = peak_size = 0

        return MemorySnapshot(
            timestamp=current_time,
            current_size=current_size,
            peak_size=peak_size,
            traced_memory=traced_memory
        )
    
    @staticmethod
    def format_bytes(bytes_val: int) -> str:
        """Format bytes into a human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.2f}{unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.2f}PB"
    
    @staticmethod
    def calculate_resource_diff(start: ResourceSnapshot, end: ResourceSnapshot) -> Dict[str, Any]:
        """Calculate differences between two resource snapshots"""
        if start is None or end is None:
            return {}
        
        duration = end.timestamp - start.timestamp
        
        return {
            "duration": duration,
            "cpu_percent_avg": end.cpu_percent,  # Current CPU usage
            "memory_rss_change": end.memory_rss - start.memory_rss,
            "memory_vms_change": end.memory_vms - start.memory_vms,
            "memory_percent_change": end.memory_percent - start.memory_percent,
            "io_read_bytes": end.io_read_bytes - start.io_read_bytes,
            "io_write_bytes": end.io_write_bytes - start.io_write_bytes,
            "io_read_count": end.io_read_count - start.io_read_count,
            "io_write_count": end.io_write_count - start.io_write_count,
            "net_bytes_sent": end.net_bytes_sent - start.net_bytes_sent,
            "net_bytes_recv": end.net_bytes_recv - start.net_bytes_recv,
            "open_files_change": end.open_files - start.open_files,
            "threads_change": end.num_threads - start.num_threads
        }