#!/usr/bin/env python3
"""
Universal Printer Wizard - Main Entry Point

Simply runs the TUI application from the src directory.
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main application
from tui import main
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCancelled by user. Exiting.")
