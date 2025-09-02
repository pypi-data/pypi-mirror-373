#!/usr/bin/env python3
"""
Simple test to verify ohtell works correctly.
"""

import sys
from pathlib import Path
import time

# Add the parent directory to the path so we can import ohtell
sys.path.insert(0, str(Path(__file__).parent))

from tracer import task


@task(name="Simple One")
def one():
    print("Function one starting")
    result = two()
    print(f"Function one got: {result}")
    return f"one({result})"


@task(name="Simple Two")
def two():
    print("Function two starting")
    result = three()
    print(f"Function two got: {result}")
    return f"two({result})"


@task(name="Simple Three")
def three():
    print("Function three doing work")
    time.sleep(0.1)
    print("Function three done")
    return "three()"


if __name__ == "__main__":
    print("Running simple ohtell test...")
    print("-" * 40)
    
    result = one()
    
    print("-" * 40)
    print(f"Final result: {result}")
    
    # Trigger async export (optional - will happen automatically)
    from config import trigger_export
    trigger_export()
    print("Done!")