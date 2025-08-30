#!/usr/bin/env python3
"""
Script to dynamically discover source files for Micro-Manager device adapters.
This script scans a DeviceAdapter directory and returns lists of source files.

While this isn't the recommended approach for a meson.build file, it lets us add some
degree of flexibility in using a single meson.build file to build multiple different
versions of mmCoreAndDevices (which may change source over time).

Usage:
    python3 discover_sources.py <adapter_name>     # List sources for specific adapter

Examples:
    python3 discover_sources.py DemoCamera         # Show DemoCamera sources
"""

from pathlib import Path

if __name__ == "__main__":
    import sys

    # Allow specifying adapter name as command line argument
    if len(sys.argv) < 2:
        raise ValueError("Usage: python3 discover_sources.py <adapter_name>")

    adapter_name = sys.argv[1]
    base_path = Path("src/mmCoreAndDevices/DeviceAdapters")
    adapter_path = base_path / adapter_name
    if not adapter_path.exists() or not adapter_path.is_dir():
        raise ValueError(
            f"Adapter path {adapter_path} does not exist or is not a directory."
        )
    for source in sorted(adapter_path.rglob("*.cpp")):
        print(source)
