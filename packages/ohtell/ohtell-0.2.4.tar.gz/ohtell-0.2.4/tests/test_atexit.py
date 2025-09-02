#!/usr/bin/env python3
"""
Test script to demonstrate automatic cleanup on exit.
Shows that telemetry data is automatically flushed and background threads are shut down.
"""

import sys
from pathlib import Path
import time

# Add the parent directory to the path so we can import ohtell
sys.path.insert(0, str(Path(__file__).parent))

from tracer import task


@task(name="Test Function", description="Simple test to generate telemetry")
def test_function(message: str):
    """Simple test function."""
    print(f"Processing: {message}")
    time.sleep(0.1)  # Simulate some work
    return f"processed-{message}"


@task(name="Another Function")  
def another_function():
    """Another function to generate more telemetry."""
    print("Doing more work...")
    for i in range(3):
        print(f"Step {i+1}")
        time.sleep(0.05)
    return "more-work-done"


if __name__ == "__main__":
    print("=" * 50)
    print("Testing automatic cleanup on exit")
    print("=" * 50)
    
    print("1. Calling test functions to generate telemetry...")
    result1 = test_function("hello")
    print(f"Result 1: {result1}")
    
    result2 = another_function()
    print(f"Result 2: {result2}")
    
    print("\n2. Script ending - watch for automatic cleanup...")
    print("   (No manual force_flush() call needed)")
    
    # Exit without manual cleanup - atexit should handle it
    print("\n3. Exiting now...")

# When this script exits, you should see:
# 🧹 Cleaning up OpenTelemetry resources...
# ✓ Final spans flushed
# ✓ Final logs flushed  
# ✓ Final metrics flushed
# ✓ Tracer provider shutdown
# ✓ Logger provider shutdown
# ✓ Meter provider shutdown
# 🎯 OpenTelemetry cleanup complete!