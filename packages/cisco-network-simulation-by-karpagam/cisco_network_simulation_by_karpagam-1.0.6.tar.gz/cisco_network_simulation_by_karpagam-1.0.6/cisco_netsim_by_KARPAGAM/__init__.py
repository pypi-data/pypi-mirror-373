"""
Cisco Network Simulation by Karpagam
Professional Network Analysis and Simulation Toolkit

Created by: Karpagam  
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Karpagam"
__email__ = "karpagam@college.edu"
__description__ = "Professional Cisco Network Analysis & Simulation Toolkit"

# Import main function for easy access
from .main import main

# Package metadata
__all__ = ["main", "__version__", "__author__"]

def get_version():
    """Get package version"""
    return __version__

def print_banner():
    """Print package banner"""
    banner = f"""
╔══════════════════════════════════════════════════════╗
║          🌐 Cisco Network Simulation by Karpagam     ║
║        Professional Network Analysis Toolkit         ║
║                                                      ║
║  📝 Parse    🗺️ Topology   ✅ Validate             ║  
║  📊 Analyze  🎮 Simulate   📋 Report                ║
║                                                      ║
║  Version: {__version__:<10} Author: {__author__:<20}  ║
╚══════════════════════════════════════════════════════╝
    """
    print(banner)
