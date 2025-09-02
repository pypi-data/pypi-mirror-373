"""
ohtell - OpenTelemetry Function Wrapper

A simple, decorator-based OpenTelemetry wrapper for tracing Python functions.
"""

__version__ = "0.2.5"

try:
    # When installed as a package
    from .tracer import task, entrypoint, traced_task, add_event, create_traced_task_with_parent
    from .providers import setup_logging, force_flush, trigger_export, shutdown, get_tracer, get_meter
    from .config import setup_otel_from_config, init
    from .config import *
except ImportError:
    # When running directly
    from tracer import task, entrypoint, traced_task, add_event, create_traced_task_with_parent
    from providers import setup_logging, force_flush, trigger_export, shutdown, get_tracer, get_meter
    from config import setup_otel_from_config, init
    from config import *

__all__ = [
    'task', 
    'entrypoint', 
    'traced_task', 
    'add_event', 
    'create_traced_task_with_parent', 
    'setup_logging', 
    'force_flush', 
    'trigger_export', 
    'shutdown', 
    'get_tracer', 
    'get_meter', 
    'setup_otel_from_config', 
    'init'
]