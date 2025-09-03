import functools
import json
import traceback
import logging
import time
from typing import Any, Optional, Dict, Callable
from datetime import datetime
import inspect

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, SpanKind

try:
    # When installed as a package
    from .providers import get_tracer, setup_logging
    from .metrics import get_task_metrics
except ImportError:
    # When running directly
    from providers import get_tracer, setup_logging
    from metrics import get_task_metrics


def safe_serialize(obj: Any) -> Any:
    """Safely serialize objects for span attributes."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [safe_serialize(item) for item in obj[:10]]  # Limit to 10 items
    elif isinstance(obj, dict):
        return {k: safe_serialize(v) for k, v in list(obj.items())[:10]}  # Limit to 10 items
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return f"<{obj.__class__.__name__} object>"
    else:
        return str(obj)[:100]  # Limit string representation


def add_event(event_name: str, attributes: Optional[Dict[str, Any]] = None) -> bool:
    """
    Add an event to the current active span if one exists.
    
    Args:
        event_name: Name of the event
        attributes: Optional attributes to include with the event
        
    Returns:
        True if event was added, False if no active span
    """
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        current_span.add_event(event_name, attributes or {})
        return True
    return False


def format_task_name(template: str, **kwargs) -> str:
    """Format task name with template variables like Prefect."""
    try:
        # Handle datetime formatting
        for key, value in kwargs.items():
            if isinstance(value, datetime) and ':' in template:
                # Extract format after colon
                pattern = f"{{{key}:([^}}]+)}}"
                import re
                match = re.search(pattern, template)
                if match:
                    date_format = match.group(1)
                    formatted_date = value.strftime(date_format.replace('%', ''))
                    template = template.replace(f"{{{key}:{match.group(1)}}}", formatted_date)
        
        # Regular string formatting for remaining variables
        return template.format(**kwargs)
    except Exception:
        return template


class task:
    """
    Decorator for tracing functions with OpenTelemetry.
    
    Similar to Prefect's @task decorator, supports:
    - Custom task names with template variables
    - Task descriptions
    - Automatic span creation and nesting
    - Input/output capture
    - Print statement interception
    - Automatic logging to SigNoz
    - Span kind differentiation (root/child)
    - Comprehensive metrics collection
    """
    
    # Class-level logger setup
    _logger_initialized = False
    _task_logger = None
    
    @classmethod
    def _ensure_logger(cls):
        """Ensure the task logger is initialized."""
        if not cls._logger_initialized:
            cls._task_logger = setup_logging("otel_wrapper.task")
            cls._logger_initialized = True
        return cls._task_logger
    
    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_entrypoint: bool = False,
        trace_context_key: Optional[str] = None,
    ):
        self.name = name
        self.description = description
        self.is_entrypoint = is_entrypoint
        self.trace_context_key = trace_context_key or "trace_context"
        self.tracer = get_tracer()
        self.logger = self._ensure_logger()
        self.metrics = get_task_metrics()
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Start timing
            start_time = time.time()
            
            # Determine span name
            span_name = self.name or func.__name__
            
            # Build context for name template if it contains variables
            if self.name and '{' in self.name:
                # Get parameter names
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Format the span name with parameters
                span_name = format_task_name(self.name, **bound_args.arguments)
            
            # Extract trace context if present in arguments
            trace_context_value = None
            if self.trace_context_key in kwargs:
                trace_context_value = kwargs[self.trace_context_key]
            else:
                # Look for trace_context in any of the arguments
                for arg in args:
                    if isinstance(arg, dict) and self.trace_context_key in arg:
                        trace_context_value = arg[self.trace_context_key]
                        break
                    # Also check for common trace ID patterns
                    if isinstance(arg, str) and (
                        arg.startswith('trace_') or 
                        len(arg) == 36 and arg.count('-') == 4  # UUID format
                    ):
                        trace_context_value = arg
                        break
            
            # Check if we have a current span (to determine if this is a root span)
            current_span = trace.get_current_span()
            is_root = current_span is None or not current_span.is_recording()
            
            # Determine span kind
            if self.is_entrypoint or is_root:
                span_kind = SpanKind.SERVER  # Entry point spans
            else:
                span_kind = SpanKind.INTERNAL  # Child spans
            
            # Record task start metrics
            self.metrics.record_task_start(
                task_name=span_name,
                function_name=func.__name__,
                module_name=func.__module__,
                is_root=is_root,
                is_entrypoint=self.is_entrypoint
            )
            
            # Get current trace ID for logging
            current_span = trace.get_current_span()
            current_trace_id = None
            if current_span and current_span.is_recording():
                current_trace_id = format(current_span.get_span_context().trace_id, '032x')
            
            # Log task start
            self.logger.debug(f"Task started: {span_name} (parent_trace: {current_trace_id}, is_root: {is_root})", extra={
                "task.name": span_name,
                "task.function": func.__name__,
                "task.module": func.__module__,
                "task.is_root": is_root,
                "task.is_entrypoint": self.is_entrypoint,
                "parent_trace_id": current_trace_id,
            })
            
            
            # Prepare span attributes
            span_attributes = {
                "task.is_root": is_root,
            }
            
            # Add trace context linking if available
            if trace_context_value:
                span_attributes["linked.trace_id"] = str(trace_context_value)
                span_attributes["trace.context"] = str(trace_context_value)
            
            # Start span with appropriate kind
            with self.tracer.start_as_current_span(
                span_name,
                kind=span_kind,
                attributes=span_attributes
            ) as span:
                # Add description as attribute
                if self.description:
                    span.set_attribute("task.description", self.description)
                
                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                # Log the span's trace ID
                new_trace_id = format(span.get_span_context().trace_id, '032x')
                self.logger.debug(f"Span created: {span_name} (trace_id: {new_trace_id}, parent_trace: {current_trace_id})")
                
                # Add trace context linking event
                if trace_context_value:
                    span.add_event("trace_context_linked", {
                        "linked_trace_id": str(trace_context_value),
                        "span_name": span_name,
                        "function": func.__name__
                    })
                
                
                # Variables for metrics
                input_size = None
                output_size = None
                serialized_args = None
                serialized_kwargs = None
                serialized_result = None
                
                # Capture input arguments
                try:
                    if args:
                        serialized_args = json.dumps(safe_serialize(args))
                        span.set_attribute("function.args", serialized_args)
                        input_size = len(serialized_args.encode('utf-8'))
                        self.logger.debug(f"Task args: {serialized_args}", extra={"task.name": span_name})
                    if kwargs:
                        serialized_kwargs = json.dumps(safe_serialize(kwargs))
                        span.set_attribute("function.kwargs", serialized_kwargs)
                        kwargs_size = len(serialized_kwargs.encode('utf-8'))
                        input_size = (input_size or 0) + kwargs_size
                        self.logger.debug(f"Task kwargs: {serialized_kwargs}", extra={"task.name": span_name})
                except Exception as e:
                    span.set_attribute("function.args_error", str(e))
                
                # Execute function
                result = None
                error = None
                error_type = None
                
                try:
                    if inspect.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    # Capture output
                    try:
                        serialized_result = json.dumps(safe_serialize(result))
                        span.set_attribute("function.result", serialized_result)
                        output_size = len(serialized_result.encode('utf-8'))
                        self.logger.debug(f"Task result: {serialized_result}", extra={"task.name": span_name})
                    except Exception as e:
                        span.set_attribute("function.result_error", str(e))
                    
                    # Set success status
                    span.set_status(Status(StatusCode.OK))
                    
                    # Log task completion
                    self.logger.debug(f"Task completed: {span_name}", extra={
                        "task.name": span_name,
                        "task.status": "success",
                        "task.is_root": is_root,
                    })
                    
                except Exception as e:
                    error = e
                    error_type = type(e).__name__
                    
                    # Record exception
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    
                    # Add traceback
                    tb = traceback.format_exc()
                    span.set_attribute("error.traceback", tb)
                    
                    # Application error - log as DEBUG since any exception here is from user code
                    # Ohtell itself doesn't execute tasks, it only wraps them
                    self.logger.debug(f"Task failed with application error: {span_name}", extra={
                        "task.name": span_name,
                        "task.status": "error",
                        "task.is_root": is_root,
                        "error.type": error_type,
                        "error.message": str(e),
                        "error.category": "application"
                    })
                
                finally:
                    # Calculate duration
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    # Record task end metrics
                    self.metrics.record_task_end(
                        task_name=span_name,
                        function_name=func.__name__,
                        module_name=func.__module__,
                        is_root=is_root,
                        is_entrypoint=self.is_entrypoint,
                        duration=duration,
                        success=(error is None),
                        error_type=error_type,
                        input_size=input_size,
                        output_size=output_size,
                        print_count=0
                    )
                
                # Re-raise exception if occurred
                if error:
                    raise error
                
                return result
        
        # Store original function reference
        wrapper.__wrapped__ = func
        
        return wrapper


# Convenience decorators for common span types
def entrypoint(name: Optional[str] = None, description: Optional[str] = None, task_run_name: Optional[str] = None):
    """Decorator for entry point functions (e.g., API handlers, main functions)."""
    return task(name=name, description=description, task_run_name=task_run_name, is_entrypoint=True)


def traced_task(name: Optional[str] = None, description: Optional[str] = None, task_run_name: Optional[str] = None, trace_context_key: str = "trace_id"):
    """
    Decorator for tasks that automatically link trace context.
    
    Args:
        name: Task name
        description: Task description  
        task_run_name: Template for dynamic task names
        trace_context_key: Parameter name or key to look for trace context (default: "trace_id")
    
    Usage:
        @traced_task(description="Process queue message")
        def process_message(content, trace_id):
            # trace_id automatically linked in span
            pass
    """
    return task(
        name=name,
        description=description, 
        task_run_name=task_run_name,
        trace_context_key=trace_context_key
    )


def create_traced_task_with_parent(parent_trace_id: str, parent_span_id: str):
    """
    Create a task decorator that creates spans as children of the specified parent trace and span.
    
    Args:
        parent_trace_id: The parent trace ID as a hex string
        parent_span_id: The parent span ID as a hex string
    """
    def traced_task_decorator(name: str, **kwargs):
        """
        Task decorator that creates spans within the parent trace context.
        """
        def decorator(func):
            async def wrapper(*args, **func_kwargs):
                tracer = get_tracer()
                
                try:
                    # Parse the parent trace ID and span ID
                    parent_trace_id_int = int(parent_trace_id, 16)
                    parent_span_id_int = int(parent_span_id, 16)
                    
                    # Create a span context for the actual parent span
                    parent_span_context = trace.SpanContext(
                        trace_id=parent_trace_id_int,
                        span_id=parent_span_id_int,  # Use the actual parent span ID
                        is_remote=True,
                        trace_flags=trace.TraceFlags(0x01)  # SAMPLED flag
                    )
                    
                    # Create a context with the parent span
                    from opentelemetry import context
                    parent_context = trace.set_span_in_context(
                        trace.NonRecordingSpan(parent_span_context),
                        context.get_current()
                    )
                    
                    # Create a new span as a child of the parent
                    with tracer.start_as_current_span(
                        name=name,
                        context=parent_context,
                        kind=SpanKind.SERVER,
                        attributes={
                            'task.description': kwargs.get('description', ''),
                            'task.run_name': kwargs.get('task_run_name', name),
                            'parent.trace_id': parent_trace_id,
                            'parent.span_id': parent_span_id,
                            'trace.propagated': True
                        }
                    ) as span:
                        logging.debug(f"Created child span in parent trace {parent_trace_id}")
                        
                        # Set input attributes
                        span.set_attribute('function.name', func.__name__)
                        span.set_attribute('function.module', func.__module__)
                        if args or func_kwargs:
                            span.set_attribute('function.args', str(list(args) + [func_kwargs]))
                        
                        try:
                            result = await func(*args, **func_kwargs)
                            
                            # Set result attribute
                            if result is not None:
                                span.set_attribute('function.result', str(result)[:1000])  # Limit length
                            
                            span.set_status(Status(StatusCode.OK))
                            return result
                            
                        except Exception as e:
                            span.record_exception(e)
                            span.set_status(Status(StatusCode.ERROR, str(e)))
                            raise
                        
                except Exception as e:
                    # If trace context creation fails, fall back to regular task
                    logging.warning(f"Failed to create traced span with parent {parent_trace_id}:{parent_span_id}: {e}")
                    return await task(name=name, **kwargs)(func)(*args, **func_kwargs)
                    
            return wrapper
        return decorator
    return traced_task_decorator