#!/usr/bin/env python3
"""
Test script to demonstrate cleanup on interrupt.
Run this and press Ctrl+C to test cleanup during interruption.
"""

import sys
from pathlib import Path
import time
import signal

# Add the parent directory to the path so we can import ohtell
sys.path.insert(0, str(Path(__file__).parent))

from tracer import task


@task(name="Long Running Task")
def long_running_task():
    """A task that runs for a while."""
    print("Starting long running task...")
    for i in range(10):
        print(f"Working... step {i+1}/10")
        time.sleep(1)  # Sleep for 1 second each iteration
    print("Long running task completed!")
    return "finished"


if __name__ == "__main__":
    print("=" * 60)
    print("Testing cleanup on interrupt (Ctrl+C)")
    print("=" * 60)
    print("Press Ctrl+C during execution to test cleanup...")
    print("")
    
    try:
        result = long_running_task()
        print(f"Task completed normally: {result}")
    except KeyboardInterrupt:
        print("\n💥 Interrupted by user!")
        print("Cleanup should still happen...")
    
    print("Script ending...")

# Even when interrupted, you should still see the cleanup:
# 🧹 Cleaning up OpenTelemetry resources...
# ✓ Final spans flushed
# ... etc