"""
Test package imports and basic functionality.
"""

import pytest


def test_package_import():
    """Test that the package can be imported correctly."""
    import ohtell
    assert hasattr(otel_wrapper, '__version__')
    assert ohtell.__version__ == "0.1.0"


def test_all_exports_available():
    """Test that all expected exports are available."""
    from ohtell import (
        task, 
        entrypoint, 
        traced_task, 
        add_event, 
        create_traced_task_with_parent, 
        setup_logging, 
        force_flush, 
        trigger_export, 
        shutdown, 
        get_tracer, 
        get_meter, 
        setup_otel_from_config, 
        init
    )
    
    # Just check they exist
    assert callable(task)
    assert callable(entrypoint)
    assert callable(traced_task)
    assert callable(add_event)
    assert callable(create_traced_task_with_parent)
    assert callable(setup_logging)
    assert callable(force_flush)
    assert callable(trigger_export)
    assert callable(shutdown)
    assert callable(get_tracer)
    assert callable(get_meter)
    assert callable(setup_otel_from_config)
    assert callable(init)


def test_basic_decorator_functionality():
    """Test basic decorator functionality without full OTEL setup."""
    from ohtell import task
    
    @task(name="Test Function")
    def test_func(x: int, y: int) -> int:
        """Test function docstring."""
        return x + y
    
    # Should work even without OTEL setup
    result = test_func(2, 3)
    assert result == 5
    
    # Function metadata should be preserved
    assert test_func.__name__ == "test_func"
    assert "Test function docstring" in test_func.__doc__


def test_entrypoint_decorator():
    """Test entrypoint decorator basic functionality."""
    from ohtell import entrypoint
    
    @entrypoint(name="Entry Point")
    def entry_func(data: str) -> str:
        return f"processed: {data}"
    
    result = entry_func("test")
    assert result == "processed: test"


def test_add_event_without_active_span():
    """Test add_event returns False when no active span."""
    from ohtell import add_event
    
    # Should return False when no active span
    result = add_event("test_event", {"key": "value"})
    assert result is False