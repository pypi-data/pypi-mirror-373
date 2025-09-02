# ohtell

A simple, async-first OpenTelemetry decorator for tracing Python functions. Automatically captures traces, metrics, and logs with minimal setup.

## Features

- 🎯 **Async-first decorator API** - All functions become async when decorated
- 🖥️ **Console output by default** - No setup needed, outputs to console when no OTEL endpoint configured
- 🔄 **Automatic span hierarchy** - Nested function calls create proper parent-child relationships  
- 📊 **Complete observability** - Traces, metrics, and logs in one package
- 📝 **Print capture** - Automatically captures print statements as events and logs
- 🏷️ **Dynamic naming** - Template-based span names with parameters
- ⚡ **Zero-block export** - Fire-and-forget telemetry that doesn't block your code

## Installation

```bash
pip install ohtell
```

## Quick Start

```python
import asyncio
from ohtell import task

@task(name="Hello World")
async def hello(name: str):
    print(f"Hello {name}!")
    return f"Greetings, {name}"

# Run it
result = asyncio.run(hello("World"))
```

This outputs traces, metrics, and logs to the console by default. No configuration needed!

## Configuration

### Option 1: Environment Variables (OTLP Standard)

```bash
# OTLP endpoint (if not set, outputs to console)
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"

# Optional: Authentication headers
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer your-token"

# Optional: Service identification
export OTEL_SERVICE_NAME="my-app"
export OTEL_RESOURCE_ATTRIBUTES="service.namespace=production,deployment.environment=prod"

# Optional: Protocol (defaults to http/protobuf)
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
```

### Option 2: Config File (config.yaml)

Create a `config.yaml` file in your project root:

```yaml
otel:
  endpoint: "http://localhost:4317"
  headers: "Authorization=Bearer your-token"
  protocol: "grpc"  # or "http/protobuf"
  resource_attributes: "service.namespace=production,deployment.environment=prod"
```

### Option 3: Programmatic Configuration

```python
import asyncio
import os
from ohtell import task

# Just set environment variables in code
os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = 'http://localhost:4317'
os.environ['OTEL_EXPORTER_OTLP_HEADERS'] = 'Authorization=Bearer your-token'
os.environ['OTEL_SERVICE_NAME'] = 'my-app'

@task(name="Configured Task")
async def configured_task():
    return "configured"

asyncio.run(configured_task())
```

## `@task` vs `@entrypoint` - What's the Difference?

**Simple: `@entrypoint` is just `@task` with `is_entrypoint=True`**

### `@task` - Regular Functions
- Nested calls create child spans
- Root calls create new trace trees
- Use for most functions

### `@entrypoint` - Entry Points
- **Always starts a new root span** (breaks the observability stack)
- Use for API handlers, CLI commands, webhook handlers
- Forces a new trace even when called from within other traces

```python
import asyncio
from ohtell import task, entrypoint

@entrypoint(name="API Handler")  # Always creates NEW root span
async def api_endpoint(request_id: str):
    return await process_request(request_id)  # This becomes child of API Handler

@task(name="Business Logic")     # Creates child span
async def process_request(request_id: str):
    return await save_to_db(request_id)      # This becomes child of Business Logic

@task(name="Database Save")      # Creates child span
async def save_to_db(request_id: str):
    return f"saved {request_id}"

# Even if called from another trace, @entrypoint breaks the chain:
@task(name="Some Other Function")
async def other_function():
    # This would normally be a child span, but @entrypoint forces a new root
    return await api_endpoint("from-other-function")
```

**Use `@entrypoint` when you want to start fresh traces, not continue existing ones.**

## Examples

### Basic API Workflow

```python
import asyncio
from ohtell import task, entrypoint, add_event

@entrypoint(name="API Endpoint")
async def api_handler(request_id: str):
    """Simulate an API endpoint."""
    print(f"Processing request {request_id}")
    add_event("request_received", {"request_id": request_id})
    
    result = await process_data(request_id, data_size=100)
    
    add_event("request_completed", {"request_id": request_id, "result_size": len(result)})
    return result

@task(name="Data Processing")
async def process_data(request_id: str, data_size: int):
    """Simulate data processing."""
    print(f"Processing {data_size} items for {request_id}")
    
    processed = []
    for i in range(data_size):
        item_result = await transform_item(f"item_{i}")
        processed.append(item_result)
    
    print(f"Processed {len(processed)} items")
    return processed

@task(name="Transform Item")
async def transform_item(item: str):
    """Simulate item transformation."""
    await asyncio.sleep(0.001)  # Simulate work
    return f"transformed_{item}"

# Execute the workflow
result = asyncio.run(api_handler("test_request_123"))
```

### Error Handling

```python
import asyncio
from ohtell import task

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

results = asyncio.run(error_handler())
# Results: [('success', 'success'), ('error', 'Simulated failure')]
```

### Dynamic Task Names

```python
import asyncio
from ohtell import task

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

# Creates spans named: "backup-database-high", "backup-files-medium"
result1 = asyncio.run(scheduled_backup("database", "high", 1000))
result2 = asyncio.run(scheduled_backup("files", "medium", 500))
```

### Nested Span Hierarchy

```python
import asyncio
from ohtell import task

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

# Creates nested spans: Level 1 > Level 2 > Level 3
result = asyncio.run(level_1())
# Result: "level_1(level_2(level_3()))"
```

## What Gets Captured

Each decorated function automatically captures:

- **Traces**: Span hierarchy with timing, status, and relationships
- **Metrics**: Call counts, error rates, duration histograms, active task gauges
- **Logs**: Print statements and structured logs, correlated with traces
- **Events**: Custom events with `add_event()` function
- **Errors**: Automatic exception recording with full tracebacks
- **I/O**: Function arguments and return values (safely serialized)

## Metrics Collected

- `task_calls_total` - Total function calls (by task name, function, status)
- `task_errors_total` - Total errors (by error type)
- `task_prints_total` - Print statements captured
- `task_duration_seconds` - Function execution time distribution
- `task_input_size` - Size of input arguments (bytes)
- `task_output_size` - Size of return values (bytes)
- `active_tasks` - Currently executing functions

## Export Control

```python
from ohtell import force_flush, trigger_export, shutdown

# Wait for all data to be exported (blocks)
force_flush()

# Trigger export in background (non-blocking)
trigger_export()

# Manual shutdown
shutdown()
```

## Configuration Options

### Environment Variables

**Core OTLP Configuration:**
| Variable | Default | Config YAML Key | Description |
|----------|---------|-----------------|-------------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | *(none)* | `endpoint` | OTLP endpoint URL. If not set, outputs to console |
| `OTEL_EXPORTER_OTLP_HEADERS` | *(none)* | `headers` | Authentication headers |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `http/protobuf` | `protocol` | Protocol: `grpc` or `http/protobuf` |
| `OTEL_SERVICE_NAME` | `ohtell-app` | *(via resource_attributes)* | Service name |
| `OTEL_RESOURCE_ATTRIBUTES` | *(none)* | `resource_attributes` | Resource attributes (comma-separated key=value) |

**Export Configuration:**
| Variable | Default | Config YAML Key | Description |
|----------|---------|-----------------|-------------|
| `OTEL_SPAN_EXPORT_INTERVAL_MS` | `500` | `span_export_interval_ms` | Trace export interval (milliseconds) |
| `OTEL_LOG_EXPORT_INTERVAL_MS` | `500` | `log_export_interval_ms` | Log export interval (milliseconds) |
| `OTEL_METRIC_EXPORT_INTERVAL_MS` | `30000` | `metric_export_interval_ms` | Metric export interval (milliseconds) |
| `OTEL_MAX_EXPORT_BATCH_SIZE` | `50` | `max_export_batch_size` | Maximum batch size for exports |
| `OTEL_MAX_QUEUE_SIZE` | `512` | `max_queue_size` | Maximum queue size |

**ohtell-Specific Configuration:**
| Variable | Default | Config YAML Key | Description |
|----------|---------|-----------------|-------------|
| `OTEL_METRICS_SAMPLING_RATE` | `0.1` | `metrics_sampling_rate` | Metrics sampling rate (0.0 to 1.0) |
| `OTEL_METRICS_ENABLED` | `true` | `metrics_enabled` | Enable/disable metrics collection |
| `OTEL_WRAPPER_SKIP_CLEANUP` | `true` | `skip_cleanup` | Skip automatic cleanup on process exit |

**Environment variables always take precedence over config.yaml settings.**

### Config File Format (config.yaml)

```yaml
otel:
  # Core OTLP Configuration
  endpoint: "http://localhost:4317"           # OTLP endpoint
  headers: "Authorization=Bearer token123"    # Auth headers  
  protocol: "grpc"                           # grpc or http/protobuf
  resource_attributes: "key1=value1,key2=value2"  # Resource attributes
  
  # Export Intervals (milliseconds)
  span_export_interval_ms: 500               # Trace export interval (0.5 seconds)
  log_export_interval_ms: 500                # Log export interval (0.5 seconds)  
  metric_export_interval_ms: 30000           # Metric export interval (30 seconds)
  
  # Batch Configuration
  max_export_batch_size: 50                  # Maximum batch size for exports
  max_queue_size: 512                        # Maximum queue size
  
  # Metrics Configuration
  metrics_sampling_rate: 0.1                 # Sample 10% of metrics
  metrics_enabled: true                      # Enable metrics collection
  
  # Cleanup Configuration  
  skip_cleanup: true                         # Skip automatic cleanup on exit
```

The config file is automatically loaded from the project root if it exists. **Environment variables take precedence over config file values.**

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_integration.py  # Integration tests with real examples
pytest tests/test_config.py       # Configuration tests
pytest tests/test_metrics.py      # Metrics functionality tests
```

The integration tests in `tests/test_integration.py` contain realistic examples that demonstrate all features working together.