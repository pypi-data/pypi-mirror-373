"""
ohtell - OpenTelemetry Function Wrapper

A simple, decorator-based OpenTelemetry wrapper for tracing Python functions.
"""

__version__ = "0.2.13"

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

import os
import requests
import logging
from urllib.parse import urljoin

# Configure logging for ohtell
logger = logging.getLogger(__name__)

def _test_otlp_connection():
    """Test OTLP endpoint connection and authentication."""
    from .config import OTEL_ENDPOINT, OTEL_HEADERS_STR, OTEL_PROTOCOL, RESOURCE_ATTRIBUTES_STR, OTEL_HEADERS
    
    logger.info("OTEL Configuration:")
    logger.info(f"  OTEL_EXPORTER_OTLP_ENDPOINT: {OTEL_ENDPOINT or 'Not set'}")
    logger.info(f"  OTEL_EXPORTER_OTLP_PROTOCOL: {OTEL_PROTOCOL}")
    logger.info(f"  OTEL_EXPORTER_OTLP_HEADERS: {'<set>' if OTEL_HEADERS_STR else 'Not set'}")
    logger.info(f"  OTEL_RESOURCE_ATTRIBUTES: {RESOURCE_ATTRIBUTES_STR or 'Not set'}")
    
    endpoint = OTEL_ENDPOINT
    headers = OTEL_HEADERS
    
    if not endpoint:
        logger.warning("No OTLP endpoint configured")
        return
    
    # Test connection by sending a real "Restart ${service.name}" span
    try:
        from .config import SERVICE_NAME
        from .providers import get_tracer
        import time
        
        # Get tracer and create a test span
        tracer = get_tracer()
        logger.info(f"Testing OTLP connection with span: 'Restart {SERVICE_NAME}'")
        
        with tracer.start_as_current_span(f"Restart {SERVICE_NAME}") as span:
            span.set_attribute("test.connection", True)
            span.set_attribute("service.restart", True)
            time.sleep(0.01)  # Brief pause to make span meaningful
        
        # Force flush to send immediately
        from .providers import force_flush
        force_flush()
        
    except Exception as e:
        logger.error(f"Test span failed: {str(e)}")

# Test OTLP configuration on import
_test_otlp_connection()

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