"""
OpenTelemetry metrics for task execution.
Provides counters, histograms, and gauges for monitoring function performance.
"""

import time
import random
from typing import Dict, Optional
from opentelemetry.metrics import Instrument

try:
    # When installed as a package
    from .providers import get_meter
    from .config import METRICS_SAMPLING_RATE, METRICS_ENABLED
except ImportError:
    # When running directly
    from providers import get_meter
    from config import METRICS_SAMPLING_RATE, METRICS_ENABLED


class TaskMetrics:
    """Manages all metrics for task execution."""
    
    def __init__(self):
        self.meter = get_meter()
        self._instruments: Dict[str, Instrument] = {}
        self._enabled = METRICS_ENABLED
        self._sampling_rate = METRICS_SAMPLING_RATE
        if self._enabled:
            self._setup_instruments()
    
    def _setup_instruments(self):
        """Set up all the metric instruments."""
        
        # Counters
        self._instruments['task_calls_total'] = self.meter.create_counter(
            name="task_calls_total",
            description="Total number of task calls",
            unit="1"
        )
        
        self._instruments['task_errors_total'] = self.meter.create_counter(
            name="task_errors_total",
            description="Total number of task errors",
            unit="1"
        )
        
        # Histograms
        self._instruments['task_duration_seconds'] = self.meter.create_histogram(
            name="task_duration_seconds",
            description="Task execution duration in seconds",
            unit="s"
        )
        
        self._instruments['task_input_size'] = self.meter.create_histogram(
            name="task_input_size",
            description="Size of task input arguments (serialized length)",
            unit="bytes"
        )
        
        self._instruments['task_output_size'] = self.meter.create_histogram(
            name="task_output_size", 
            description="Size of task output (serialized length)",
            unit="bytes"
        )
        
        # Up/Down Counter for active tasks
        self._instruments['active_tasks'] = self.meter.create_up_down_counter(
            name="active_tasks",
            description="Number of currently active tasks",
            unit="1"
        )
        
        # Gauge for print statements
        self._instruments['task_prints_total'] = self.meter.create_counter(
            name="task_prints_total",
            description="Total number of print statements captured",
            unit="1"
        )
    
    def _should_sample(self) -> bool:
        """Determine if this metric should be sampled."""
        return random.random() < self._sampling_rate
    
    def record_task_start(self, task_name: str, function_name: str, module_name: str, 
                         is_root: bool, is_entrypoint: bool):
        """Record when a task starts."""
        if not self._enabled:
            return
            
        # Always record critical metrics (entrypoints and root spans)
        if is_entrypoint or is_root or self._should_sample():
            attributes = {
                "task.name": task_name,
                "function.name": function_name,
                "function.module": module_name,
                "task.is_root": is_root,
                "task.is_entrypoint": is_entrypoint,
            }
            
            # Increment call counter
            self._instruments['task_calls_total'].add(1, attributes)
            
            # Increment active tasks
            self._instruments['active_tasks'].add(1, attributes)
    
    def record_task_end(self, task_name: str, function_name: str, module_name: str,
                       is_root: bool, is_entrypoint: bool, duration: float,
                       success: bool, error_type: Optional[str] = None,
                       input_size: Optional[int] = None, output_size: Optional[int] = None,
                       print_count: int = 0):
        """Record when a task completes."""
        if not self._enabled:
            return
            
        # Always record critical metrics (entrypoints, root spans, and errors)
        if is_entrypoint or is_root or not success or self._should_sample():
            attributes = {
                "task.name": task_name,
                "function.name": function_name,
                "function.module": module_name,
                "task.is_root": is_root,
                "task.is_entrypoint": is_entrypoint,
                "task.status": "success" if success else "error"
            }
            
            # Record duration
            self._instruments['task_duration_seconds'].record(duration, attributes)
            
            # Record error if occurred
            if not success and error_type:
                error_attributes = {**attributes, "error.type": error_type}
                self._instruments['task_errors_total'].add(1, error_attributes)
            
            # Only record size metrics for sampled requests to reduce volume
            if self._should_sample():
                # Record input/output sizes if available
                if input_size is not None:
                    self._instruments['task_input_size'].record(input_size, attributes)
                
                if output_size is not None:
                    self._instruments['task_output_size'].record(output_size, attributes)
                
                # Record print statements
                if print_count > 0:
                    self._instruments['task_prints_total'].add(print_count, attributes)
            
            # Decrement active tasks
            self._instruments['active_tasks'].add(-1, attributes)
    
    def record_task_error(self, task_name: str, function_name: str, module_name: str,
                         error_type: str, is_root: bool, is_entrypoint: bool):
        """Record a task error (for additional error tracking)."""
        if not self._enabled:
            return
            
        # Always record errors
        attributes = {
            "task.name": task_name,
            "function.name": function_name,
            "function.module": module_name,
            "task.is_root": is_root,
            "task.is_entrypoint": is_entrypoint,
            "error.type": error_type,
        }
        
        self._instruments['task_errors_total'].add(1, attributes)


# Global metrics instance
_task_metrics = None

def get_task_metrics() -> TaskMetrics:
    """Get the global task metrics instance."""
    global _task_metrics
    if _task_metrics is None:
        _task_metrics = TaskMetrics()
    return _task_metrics