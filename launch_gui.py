#!/usr/bin/env python3
"""
Simple launcher for Crypto Sector Rotation Analyzer GUI
"""

import sys
from pathlib import Path

# Add the sector_rotation package to path
sys.path.insert(0, str(Path(__file__).parent / "sector_rotation"))

# Import and run GUI
from gui_app import main

if __name__ == "__main__":
    main()
