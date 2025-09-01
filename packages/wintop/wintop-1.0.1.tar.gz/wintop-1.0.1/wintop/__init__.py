"""
WinTop - Windows System Monitor

A top-like utility for Windows that displays system resource usage including:
- CPU usage
- Memory usage
- Disk usage
- Network I/O
- Process statistics
"""

from .wintop import WinTop, main

__version__ = "1.0.0"
__all__ = ["WinTop", "main"]