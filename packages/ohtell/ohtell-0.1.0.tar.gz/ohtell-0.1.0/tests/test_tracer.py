import unittest
from unittest.mock import Mock, patch, MagicMock
import datetime
import json

from ohtell import task
from ohtell.tracer import safe_serialize, format_task_name


class TestSafeSerialization(unittest.TestCase):
    """Test safe serialization of various object types."""
    
    def test_primitive_types(self):
        self.assertEqual(safe_serialize(None), None)
        self.assertEqual(safe_serialize("hello"), "hello")
        self.assertEqual(safe_serialize(42), 42)
        self.assertEqual(safe_serialize(3.14), 3.14)
        self.assertEqual(safe_serialize(True), True)
    
    def test_collections(self):
        # Lists
        self.assertEqual(safe_serialize([1, 2, 3]), [1, 2, 3])
        
        # Large lists are truncated
        large_list = list(range(20))
        serialized = safe_serialize(large_list)
        self.assertEqual(len(serialized), 10)
        
        # Dicts
        self.assertEqual(safe_serialize({"a": 1, "b": 2}), {"a": 1, "b": 2})
    
    def test_datetime(self):
        dt = datetime.datetime(2024, 1, 1, 12, 0, 0)
        self.assertEqual(safe_serialize(dt), "2024-01-01T12:00:00")
    
    def test_custom_objects(self):
        class CustomObj:
            pass
        
        obj = CustomObj()
        self.assertEqual(safe_serialize(obj), "<CustomObj object>")


class TestTaskNameFormatting(unittest.TestCase):
    """Test dynamic task name formatting."""
    
    def test_simple_formatting(self):
        result = format_task_name("hello-{name}", name="world")
        self.assertEqual(result, "hello-world")
    
    def test_datetime_formatting(self):
        dt = datetime.datetime(2024, 1, 15, 10, 30, 0)
        result = format_task_name("task-{date:%A}", date=dt)
        self.assertEqual(result, "task-Monday")
        
        result = format_task_name("run-{date:%Y-%m-%d}", date=dt)
        self.assertEqual(result, "run-2024-01-15")


class TestTaskDecorator(unittest.TestCase):
    """Test the @task decorator functionality."""
    
    def setUp(self):
        # Mock the tracer
        self.mock_tracer = Mock()
        self.mock_span = MagicMock()
        self.mock_span.__enter__ = Mock(return_value=self.mock_span)
        self.mock_span.__exit__ = Mock(return_value=None)
        
        # Patch get_tracer to return our mock
        patcher = patch('ohtell.tracer.get_tracer')
        self.addCleanup(patcher.stop)
        self.mock_get_tracer = patcher.start()
        self.mock_get_tracer.return_value = self.mock_tracer
        self.mock_tracer.start_as_current_span.return_value = self.mock_span
    
    def test_basic_decoration(self):
        @task(name="Test Task", description="A test task")
        def test_func(x, y):
            return x + y
        
        result = test_func(1, 2)
        self.assertEqual(result, 3)
        
        # Check span was created with correct name
        self.mock_tracer.start_as_current_span.assert_called_once_with("Test Task")
        
        # Check attributes were set
        self.mock_span.set_attribute.assert_any_call("task.description", "A test task")
        self.mock_span.set_attribute.assert_any_call("function.name", "test_func")
    
    def test_input_output_capture(self):
        @task()
        def test_func(a, b=10):
            return {"sum": a + b}
        
        result = test_func(5, b=15)
        
        # Check input capture
        args_calls = [call for call in self.mock_span.set_attribute.call_args_list 
                      if call[0][0] == "function.args"]
        self.assertEqual(len(args_calls), 1)
        self.assertEqual(json.loads(args_calls[0][0][1]), [5])
        
        kwargs_calls = [call for call in self.mock_span.set_attribute.call_args_list 
                        if call[0][0] == "function.kwargs"]
        self.assertEqual(len(kwargs_calls), 1)
        self.assertEqual(json.loads(kwargs_calls[0][0][1]), {"b": 15})
        
        # Check output capture
        result_calls = [call for call in self.mock_span.set_attribute.call_args_list 
                        if call[0][0] == "function.result"]
        self.assertEqual(len(result_calls), 1)
        self.assertEqual(json.loads(result_calls[0][0][1]), {"sum": 20})
    
    def test_exception_handling(self):
        @task(name="Failing Task")
        def failing_func():
            raise ValueError("Test error")
        
        with self.assertRaises(ValueError):
            failing_func()
        
        # Check exception was recorded
        self.mock_span.record_exception.assert_called_once()
        self.mock_span.set_status.assert_called()
    
    def test_print_capture(self):
        @task()
        def printing_func():
            print("Hello")
            print("World")
            return "done"
        
        result = printing_func()
        self.assertEqual(result, "done")
        
        # Check events were added for prints
        print_events = [call for call in self.mock_span.add_event.call_args_list 
                        if call[0][0] == "print"]
        self.assertEqual(len(print_events), 2)
        self.assertEqual(print_events[0][0][1]["message"], "Hello")
        self.assertEqual(print_events[1][0][1]["message"], "World")


class TestNestedSpans(unittest.TestCase):
    """Test that nested function calls create proper span hierarchy."""
    
    def setUp(self):
        # Reset any global state
        import ohtell.config
        ohtell.config._tracer = None
        ohtell.config._tracer_provider = None
    
    @patch('ohtell.config.trace.get_tracer')
    @patch('ohtell.config.trace.set_tracer_provider')
    @patch('ohtell.config.BatchSpanProcessor')
    @patch('ohtell.config.OTLPSpanExporter')
    def test_nested_calls(self, mock_exporter_class, mock_processor_class, 
                         mock_set_provider, mock_get_tracer):
        # Set up mocks
        mock_tracer = Mock()
        mock_get_tracer.return_value = mock_tracer
        
        # Create separate spans for each call
        spans = []
        
        def create_span(name):
            span = MagicMock()
            span.__enter__ = Mock(return_value=span)
            span.__exit__ = Mock(return_value=None)
            spans.append((name, span))
            return span
        
        mock_tracer.start_as_current_span.side_effect = create_span
        
        # Define nested functions
        @task(name="outer")
        def outer():
            return inner()
        
        @task(name="inner")
        def inner():
            return "result"
        
        # Execute
        result = outer()
        self.assertEqual(result, "result")
        
        # Check both spans were created
        self.assertEqual(len(spans), 2)
        self.assertEqual(spans[0][0], "outer")
        self.assertEqual(spans[1][0], "inner")


if __name__ == "__main__":
    unittest.main()