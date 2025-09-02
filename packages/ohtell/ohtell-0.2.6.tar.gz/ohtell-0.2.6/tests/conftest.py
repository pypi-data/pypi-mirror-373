"""
Pytest configuration and fixtures for ohtell tests.
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import ohtell modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(autouse=True)
def cleanup_telemetry():
    """Automatically cleanup telemetry after each test."""
    yield  # Run the test
    
    # Clean up after test
    try:
        from providers import _cleanup_on_exit
        _cleanup_on_exit()
        
        # Reset global state
        import providers
        providers._tracer_provider = None
        providers._logger_provider = None
        providers._meter_provider = None
        providers._tracer = None
        providers._meter = None
        providers._otel_logger = None
        providers._logging_handler = None
        providers._span_processor = None
        providers._log_processor = None
        providers._metric_reader = None
        providers._atexit_registered = False
        
        # Reset metrics global state
        import metrics
        metrics._task_metrics = None
        
    except Exception:
        # Ignore cleanup errors in tests
        pass

@pytest.fixture
def suppress_console_output():
    """Suppress console output during tests to avoid noise."""
    import io
    import contextlib
    
    @contextlib.contextmanager
    def suppress():
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            yield
    
    return suppress