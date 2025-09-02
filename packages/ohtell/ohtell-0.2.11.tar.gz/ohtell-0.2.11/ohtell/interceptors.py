import sys
import io
import logging
from contextlib import contextmanager
from typing import List, Tuple, Optional
import time


class PrintInterceptor:
    """Captures print statements during function execution and logs them."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.captured: List[Tuple[float, str]] = []
        self._original_stdout = None
        self._capture_buffer = None
        self.logger = logger or logging.getLogger(__name__)
    
    @contextmanager
    def capture(self):
        """Context manager to capture stdout."""
        self._original_stdout = sys.stdout
        self._capture_buffer = io.StringIO()
        
        # Create a custom stdout that captures and passes through
        class TeeStdout:
            def __init__(self, interceptor, buffer):
                self.interceptor = interceptor
                self.buffer = buffer
                self.original = interceptor._original_stdout
            
            def write(self, text):
                # Write to both original stdout and capture buffer
                self.original.write(text)
                self.buffer.write(text)
                
                # Record non-empty writes with timestamp
                if text and text != '\n':
                    timestamp = time.time()
                    message = text.rstrip('\n')
                    self.interceptor.captured.append((timestamp, message))
                    
                
                return len(text)
            
            def flush(self):
                self.original.flush()
                self.buffer.flush()
            
            def __getattr__(self, name):
                # Delegate other attributes to original stdout
                return getattr(self.original, name)
        
        sys.stdout = TeeStdout(self, self._capture_buffer)
        
        try:
            yield self
        finally:
            # Restore original stdout
            sys.stdout = self._original_stdout
            self._capture_buffer.close()
    
    def get_captured_prints(self) -> List[Tuple[float, str]]:
        """Get list of captured prints with timestamps."""
        return self.captured.copy()
    
    def clear(self):
        """Clear captured prints."""
        self.captured.clear()