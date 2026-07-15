#!/usr/bin/env python3
"""
PrivateScan — Offline Document & Image Analyzer
100% On-Device AI. Nothing leaves your machine.

Built for OSDHack 2026
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ui import PrivateScanApp


def main():
    """Launch PrivateScan application."""
    app = PrivateScanApp()
    app.mainloop()


if __name__ == "__main__":
    main()
