#!/usr/bin/env python3
"""
Test script to verify ohtell distributed tracing with __otel_context parameter.
"""

import asyncio
import logging
import sys
import os

# Add the parent directory to sys.path to import ohtell
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ohtell import task, get_otel_context, set_trace_id

# Set up logging to see debug messages
logging.basicConfig(level=logging.INFO)

# Set up telemetry with console output
os.environ["OTEL_CONSOLE_ENABLED"] = "true"

@task(name="print_context")
async def print_context():
    """Returns current trace context."""
    return get_otel_context()

async def simulate_queue_processing():
    """Simulate queue message processing with trace context."""
    
    # Simulate producer creating a message with trace context
    @task(name="producer")
    async def producer():
        context = get_otel_context()
        message = {
            "data": "user_signup",
            "user_id": "123",
            "__otel_context": context
        }
        return message
    
    # Simulate consumer processing message
    @task(name="consumer")
    async def consumer(message):
        # Just pass __otel_context, avoid parameter conflicts
        context = message.get("__otel_context")
        if context:
            return await process_data(message["data"], message["user_id"], __otel_context=context)
        else:
            return await process_data(message["data"], message["user_id"])
    
    @task(name="process_data") 
    async def process_data(data, user_id):
        return f"processed {data} for {user_id}"
    
    # Test the flow
    message = await producer()
    result = await consumer(message)
    
    return result

async def main():
    """Test distributed tracing scenarios."""
    
    # Test 1: Queue processing (same trace)
    result1 = await simulate_queue_processing()
    
    # Test 2: External trace injection
    external_context = {
        'trace_id': 'deadbeefcafebabe1234567890abcdef',
        'span_id': 'fedcba9876543210',
        'trace_flags': 1,
        'is_remote': True
    }
    
    context2 = await print_context(__otel_context=external_context)
    
    print(f"Queue processing result: {result1}")
    print(f"External trace_id: {context2['trace_id']}")
    
    # Verify external trace injection works
    assert context2['trace_id'] == 'deadbeefcafebabe1234567890abcdef'
    print("✅ Distributed tracing tests passed!")
    
    await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())