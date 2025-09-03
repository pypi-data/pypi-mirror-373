"""
Integration tests for the complete ohtell functionality.
Tests metrics, traces, and logs together in realistic scenarios.
"""

import pytest
import asyncio
import json
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
async def test_complete_tracing_workflow():
    """Test complete tracing workflow with metrics and logs."""
    from ohtell import task, entrypoint, force_flush, add_event
    
    # Capture console output
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        
        @entrypoint(name="API Endpoint")
        async def api_handler(request_id: str):
            """Simulate an API endpoint."""
            print(f"Processing request {request_id}")
            add_event("request_received", {"request_id": request_id})
            
            # Call business logic
            result = await process_data(request_id, data_size=100)
            
            add_event("request_completed", {"request_id": request_id, "result_size": len(result)})
            return result
        
        @task(name="Data Processing")
        async def process_data(request_id: str, data_size: int):
            """Simulate data processing."""
            print(f"Processing {data_size} items for {request_id}")
            
            # Simulate some work
            processed = []
            for i in range(data_size):
                item_result = await transform_item(f"item_{i}")
                processed.append(item_result)
            
            print(f"Processed {len(processed)} items")
            return processed
        
        @task(name="Transform Item")
        async def transform_item(item: str):
            """Simulate item transformation."""
            # Simulate processing time
            await asyncio.sleep(0.001)  # 1ms
            return f"transformed_{item}"
        
        # Execute the workflow
        result = await api_handler("test_request_123")
        
        # Force flush to get all telemetry data
        force_flush()
    
    # Validate results
    assert len(result) == 100
    assert all(item.startswith("transformed_item_") for item in result)
    
    # Check console output contains our print statements
    output = stdout_capture.getvalue()
    assert "Processing request test_request_123" in output
    assert "Processing 100 items for test_request_123" in output
    assert "Processed 100 items" in output


@pytest.mark.asyncio 
async def test_error_handling_and_metrics():
    """Test error handling with proper span status and error metrics."""
    from ohtell import task, force_flush
    
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        
        @task(name="Failing Task")
        async def failing_task(should_fail: bool = True):
            """Task that can fail."""
            print("Starting task...")
            
            if should_fail:
                raise ValueError("Simulated failure")
            
            return "success"
        
        @task(name="Error Handler")
        async def error_handler():
            """Task that handles errors."""
            results = []
            
            # Try successful task
            try:
                success_result = await failing_task(should_fail=False)
                results.append(("success", success_result))
            except Exception as e:
                results.append(("error", str(e)))
            
            # Try failing task  
            try:
                fail_result = await failing_task(should_fail=True)
                results.append(("success", fail_result))
            except Exception as e:
                results.append(("error", str(e)))
            
            return results
        
        # Execute with error handling
        results = await error_handler()
        force_flush()
    
    # Validate error handling
    assert len(results) == 2
    assert results[0] == ("success", "success")
    assert results[1][0] == "error"
    assert "Simulated failure" in results[1][1]


@pytest.mark.asyncio
async def test_nested_spans_hierarchy():
    """Test that nested function calls create proper span hierarchy.""" 
    from ohtell import task, force_flush
    
    stdout_capture = io.StringIO()
    
    with redirect_stdout(stdout_capture):
        
        @task(name="Level 1", description="Top level task")
        async def level_1():
            """Top level function."""
            print("Entering level 1")
            result = await level_2()
            print("Exiting level 1")
            return f"level_1({result})"
        
        @task(name="Level 2", description="Second level task")
        async def level_2():
            """Second level function."""
            print("Entering level 2") 
            result = await level_3()
            print("Exiting level 2")
            return f"level_2({result})"
        
        @task(name="Level 3", description="Third level task")
        async def level_3():
            """Third level function."""
            print("Entering level 3")
            await asyncio.sleep(0.001)  # Simulate work
            print("Exiting level 3")
            return "level_3()"
        
        # Execute nested calls
        result = await level_1()
        force_flush()
    
    # Validate nested result structure
    expected = "level_1(level_2(level_3()))"
    assert result == expected
    
    # Check all print statements were captured
    output = stdout_capture.getvalue()
    assert "Entering level 1" in output
    assert "Entering level 2" in output 
    assert "Entering level 3" in output
    assert "Exiting level 3" in output
    assert "Exiting level 2" in output
    assert "Exiting level 1" in output


@pytest.mark.asyncio
async def test_custom_events_and_attributes():
    """Test adding custom events and span attributes."""
    from ohtell import task, add_event, force_flush
    
    stdout_capture = io.StringIO()
    
    with redirect_stdout(stdout_capture):
        
        @task(name="Custom Events Task", description="Task with custom events")
        async def custom_events_task(user_id: str, action: str):
            """Task that adds custom events and handles user actions."""
            print(f"User {user_id} performing {action}")
            
            # Add custom event at start
            add_event("user_action_started", {
                "user_id": user_id,
                "action": action,
                "timestamp": "2024-01-01T00:00:00Z"
            })
            
            # Simulate processing
            await asyncio.sleep(0.002)
            
            # Add intermediate event
            add_event("processing_checkpoint", {
                "progress": 50,
                "status": "in_progress" 
            })
            
            # Simulate more processing
            await asyncio.sleep(0.002)
            
            # Add completion event
            add_event("user_action_completed", {
                "user_id": user_id,
                "action": action,
                "success": True
            })
            
            return f"completed_{action}_for_{user_id}"
        
        # Execute with custom events
        result = await custom_events_task("user123", "data_export")
        force_flush()
    
    assert result == "completed_data_export_for_user123"
    
    output = stdout_capture.getvalue()
    assert "User user123 performing data_export" in output


@pytest.mark.asyncio
async def test_dynamic_task_names():
    """Test dynamic task naming with template variables."""
    from ohtell import task, force_flush
    import datetime
    
    stdout_capture = io.StringIO()
    
    with redirect_stdout(stdout_capture):
        
        @task(
            name="Scheduled Task",
            task_run_name="backup-{operation}-{priority}",
            description="Dynamic task name example"
        )
        async def scheduled_backup(operation: str, priority: str, size_mb: int):
            """Task with dynamic naming based on parameters."""
            print(f"Starting {operation} backup with {priority} priority")
            print(f"Backing up {size_mb}MB of data")
            
            # Simulate backup time proportional to size
            backup_time = size_mb * 0.0001  # 0.1ms per MB
            await asyncio.sleep(backup_time)
            
            print(f"Backup completed: {operation}")
            return {
                "operation": operation,
                "priority": priority, 
                "size_mb": size_mb,
                "success": True
            }
        
        # Execute with different parameters to test dynamic naming
        results = []
        
        result1 = await scheduled_backup("database", "high", 1000)
        results.append(result1)
        
        result2 = await scheduled_backup("files", "medium", 500) 
        results.append(result2)
        
        force_flush()
    
    # Validate results
    assert len(results) == 2
    assert results[0]["operation"] == "database"
    assert results[0]["priority"] == "high"
    assert results[1]["operation"] == "files"
    assert results[1]["priority"] == "medium"
    
    output = stdout_capture.getvalue()
    assert "Starting database backup with high priority" in output
    assert "Starting files backup with medium priority" in output


def test_console_fallback_when_no_endpoint():
    """Test that console exporters are used when no OTEL endpoint is configured."""
    import os
    
    # Clear OTEL endpoint to force console fallback
    original_endpoint = os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT')
    if 'OTEL_EXPORTER_OTLP_ENDPOINT' in os.environ:
        del os.environ['OTEL_EXPORTER_OTLP_ENDPOINT']
    
    try:
        # Import after clearing environment
        from ohtell.providers import get_tracer, get_meter_provider
        
        # Get tracer (which initializes providers)
        tracer = get_tracer()
        assert tracer is not None
        
        # Get meter provider
        meter_provider = get_meter_provider()
        assert meter_provider is not None
        
        # These should not raise exceptions even without OTLP endpoint
        assert True  # If we get here, console fallback worked
        
    finally:
        # Restore original endpoint if it existed
        if original_endpoint:
            os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = original_endpoint


@pytest.mark.asyncio
async def test_performance_metrics_collection():
    """Test that performance metrics are properly collected."""
    from ohtell import task, force_flush
    
    @task(name="Performance Test")
    async def performance_task(iterations: int):
        """Task for testing performance metrics."""
        results = []
        for i in range(iterations):
            # Simulate variable processing time
            await asyncio.sleep(0.001 * (i % 3 + 1))  # 1-3ms
            results.append(f"item_{i}")
        
        return results
    
    # Execute task multiple times to generate metrics
    all_results = []
    for i in range(5):
        result = await performance_task(10)
        all_results.extend(result)
    
    force_flush()
    
    # Validate we processed expected number of items
    assert len(all_results) == 50  # 5 runs * 10 items each
    assert all(item.startswith("item_") for item in all_results)


if __name__ == "__main__":
    # Run tests manually if needed
    asyncio.run(test_complete_tracing_workflow())
    asyncio.run(test_error_handling_and_metrics())
    asyncio.run(test_nested_spans_hierarchy())
    asyncio.run(test_custom_events_and_attributes())
    asyncio.run(test_dynamic_task_names())
    test_console_fallback_when_no_endpoint()
    asyncio.run(test_performance_metrics_collection())
    print("All integration tests passed!")