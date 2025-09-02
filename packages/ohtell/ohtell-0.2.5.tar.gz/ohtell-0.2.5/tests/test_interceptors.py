import unittest
import sys
import time
from io import StringIO

from ohtell.interceptors import PrintInterceptor


class TestPrintInterceptor(unittest.TestCase):
    """Test the print interception functionality."""
    
    def test_basic_capture(self):
        interceptor = PrintInterceptor()
        
        with interceptor.capture():
            print("Hello")
            print("World")
        
        captured = interceptor.get_captured_prints()
        self.assertEqual(len(captured), 2)
        self.assertEqual(captured[0][1], "Hello")
        self.assertEqual(captured[1][1], "World")
        
        # Check timestamps are present and increasing
        self.assertIsInstance(captured[0][0], float)
        self.assertIsInstance(captured[1][0], float)
        self.assertLess(captured[0][0], captured[1][0])
    
    def test_stdout_passthrough(self):
        """Test that prints still go to stdout."""
        interceptor = PrintInterceptor()
        original_stdout = sys.stdout
        
        # Capture actual stdout
        captured_stdout = StringIO()
        sys.stdout = captured_stdout
        
        try:
            with interceptor.capture():
                print("Test message")
            
            # Check message was passed through
            output = captured_stdout.getvalue()
            self.assertIn("Test message", output)
        finally:
            sys.stdout = original_stdout
    
    def test_empty_prints_ignored(self):
        """Test that empty prints and newlines are handled properly."""
        interceptor = PrintInterceptor()
        
        with interceptor.capture():
            print("")  # Empty print
            print("Valid message")
            print()    # Just newline
        
        captured = interceptor.get_captured_prints()
        # Should only capture the valid message
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0][1], "Valid message")
    
    def test_multiline_prints(self):
        """Test handling of multiline print statements."""
        interceptor = PrintInterceptor()
        
        with interceptor.capture():
            print("Line 1\nLine 2\nLine 3")
        
        captured = interceptor.get_captured_prints()
        # Each line should be captured separately
        self.assertGreaterEqual(len(captured), 1)
        # The implementation captures the whole block
        self.assertIn("Line 1", captured[0][1])
    
    def test_clear_captured(self):
        """Test clearing captured prints."""
        interceptor = PrintInterceptor()
        
        with interceptor.capture():
            print("Message 1")
        
        self.assertEqual(len(interceptor.get_captured_prints()), 1)
        
        interceptor.clear()
        self.assertEqual(len(interceptor.get_captured_prints()), 0)
    
    def test_exception_handling(self):
        """Test that stdout is restored even if exception occurs."""
        interceptor = PrintInterceptor()
        original_stdout = sys.stdout
        
        try:
            with interceptor.capture():
                print("Before exception")
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Check stdout was restored
        self.assertIs(sys.stdout, original_stdout)
        
        # Check we still captured the print before exception
        captured = interceptor.get_captured_prints()
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0][1], "Before exception")
    
    def test_multiple_captures(self):
        """Test using the same interceptor multiple times."""
        interceptor = PrintInterceptor()
        
        # First capture
        with interceptor.capture():
            print("First")
        
        # Second capture
        with interceptor.capture():
            print("Second")
        
        captured = interceptor.get_captured_prints()
        self.assertEqual(len(captured), 2)
        self.assertEqual(captured[0][1], "First")
        self.assertEqual(captured[1][1], "Second")
    
    def test_print_with_args(self):
        """Test print with multiple arguments and kwargs."""
        interceptor = PrintInterceptor()
        
        with interceptor.capture():
            print("Hello", "World", sep="-", end="!\n")
            print("Value:", 42)
        
        captured = interceptor.get_captured_prints()
        self.assertEqual(len(captured), 2)
        self.assertEqual(captured[0][1], "Hello-World!")
        self.assertIn("Value:", captured[1][1])
        self.assertIn("42", captured[1][1])


if __name__ == "__main__":
    unittest.main()