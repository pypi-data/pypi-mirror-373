"""
Test metrics functionality.
"""

import pytest
from unittest.mock import MagicMock, patch


def test_task_metrics_creation():
    """Test that TaskMetrics can be created and used."""
    from ohtell.metrics import TaskMetrics
    
    # Mock meter
    mock_meter = MagicMock()
    mock_counter = MagicMock()
    mock_histogram = MagicMock()
    mock_up_down_counter = MagicMock()
    
    mock_meter.create_counter.return_value = mock_counter
    mock_meter.create_histogram.return_value = mock_histogram  
    mock_meter.create_up_down_counter.return_value = mock_up_down_counter
    
    # Create TaskMetrics instance
    metrics = TaskMetrics(mock_meter)
    
    # Check that meters were created
    assert mock_meter.create_counter.call_count == 3  # calls, errors, prints
    assert mock_meter.create_histogram.call_count == 3  # duration, input_size, output_size
    assert mock_meter.create_up_down_counter.call_count == 1  # active_tasks


def test_record_task_call():
    """Test recording a task call."""
    from ohtell.metrics import TaskMetrics
    
    mock_meter = MagicMock()
    metrics = TaskMetrics(mock_meter)
    
    # Record a successful call
    metrics.record_task_call("test_task", "test_func", "test_module", True, False, "success")
    
    # Check counter was incremented
    metrics.task_calls.add.assert_called_with(
        1, 
        {
            "task.name": "test_task",
            "function.name": "test_func", 
            "function.module": "test_module",
            "task.is_root": True,
            "task.is_entrypoint": False,
            "task.status": "success"
        }
    )


def test_record_task_error():
    """Test recording a task error.""" 
    from ohtell.metrics import TaskMetrics
    
    mock_meter = MagicMock()
    metrics = TaskMetrics(mock_meter)
    
    # Record an error
    metrics.record_task_error("test_task", "test_func", "ValueError", "Test error message")
    
    # Check error counter was incremented
    metrics.task_errors.add.assert_called_with(
        1,
        {
            "task.name": "test_task",
            "function.name": "test_func",
            "error.type": "ValueError", 
            "error.message": "Test error message"
        }
    )


def test_record_task_duration():
    """Test recording task duration."""
    from ohtell.metrics import TaskMetrics
    
    mock_meter = MagicMock()
    metrics = TaskMetrics(mock_meter)
    
    # Record duration
    metrics.record_task_duration("test_task", "test_func", 1.5, True, False)
    
    # Check histogram was recorded
    metrics.task_duration.record.assert_called_with(
        1.5,
        {
            "task.name": "test_task",
            "function.name": "test_func",
            "task.is_root": True,
            "task.is_entrypoint": False
        }
    )


def test_record_task_data_sizes():
    """Test recording input/output data sizes."""
    from ohtell.metrics import TaskMetrics
    
    mock_meter = MagicMock()
    metrics = TaskMetrics(mock_meter)
    
    # Record input size
    metrics.record_task_input_size("test_task", "test_func", 1024)
    metrics.task_input_size.record.assert_called_with(
        1024,
        {"task.name": "test_task", "function.name": "test_func"}
    )
    
    # Record output size  
    metrics.record_task_output_size("test_task", "test_func", 2048)
    metrics.task_output_size.record.assert_called_with(
        2048,
        {"task.name": "test_task", "function.name": "test_func"}
    )


def test_increment_active_tasks():
    """Test incrementing/decrementing active tasks counter."""
    from ohtell.metrics import TaskMetrics
    
    mock_meter = MagicMock()
    metrics = TaskMetrics(mock_meter)
    
    # Increment
    metrics.increment_active_tasks("test_task", "test_func")
    metrics.active_tasks.add.assert_called_with(
        1,
        {"task.name": "test_task", "function.name": "test_func"}
    )
    
    # Decrement
    metrics.decrement_active_tasks("test_task", "test_func")
    metrics.active_tasks.add.assert_called_with(
        -1,
        {"task.name": "test_task", "function.name": "test_func"}
    )


def test_record_print_event():
    """Test recording print events.""" 
    from ohtell.metrics import TaskMetrics
    
    mock_meter = MagicMock()
    metrics = TaskMetrics(mock_meter)
    
    # Record print
    metrics.record_print_event("test_task", "test_func")
    
    metrics.task_prints.add.assert_called_with(
        1,
        {"task.name": "test_task", "function.name": "test_func"}
    )


def test_get_task_metrics_singleton():
    """Test that get_task_metrics returns a singleton."""
    from ohtell.metrics import get_task_metrics
    
    with patch('otel_wrapper.metrics.get_meter') as mock_get_meter:
        mock_meter = MagicMock()
        mock_get_meter.return_value = mock_meter
        
        # First call should create instance
        metrics1 = get_task_metrics()
        
        # Second call should return same instance
        metrics2 = get_task_metrics()
        
        assert metrics1 is metrics2
        # get_meter should only be called once
        assert mock_get_meter.call_count == 1