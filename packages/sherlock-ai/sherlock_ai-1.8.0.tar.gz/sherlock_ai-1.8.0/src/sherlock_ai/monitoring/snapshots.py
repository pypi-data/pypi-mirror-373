"""
Data classes for resource and memory snapshots
"""

from dataclasses import dataclass
from typing import Tuple

@dataclass
class ResourceSnapshot:
    """Snapshot of system resource at a point in time"""
    timestamp: float
    cpu_percent: float
    memory_rss: int # Resident Set Size in bytes
    memory_vms: int # Virtual Memory Size in bytes
    memory_percent: float
    io_read_bytes: int
    io_write_bytes: int
    io_read_count: int
    io_write_count: int
    net_bytes_sent: int
    net_bytes_recv: int
    open_files: int
    num_threads: int

@dataclass
class MemorySnapshot:
    """Snapshot of memory usage at a point in time"""
    timestamp: float
    current_size: int # Current memory usage in bytes
    peak_size: int # Peak memory usage in bytes
    traced_memory: Tuple[int, int] # (current, peak) from tracemalloc