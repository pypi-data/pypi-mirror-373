#!/usr/bin/env python3
"""
Main entry point for rotating-mitmproxy when run as a module.
Allows: python -m rotating_mitmproxy
"""

from .cli import main

if __name__ == "__main__":
    main()
