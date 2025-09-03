"""
OpenTelemetry providers initialization.
Separated from config to keep configuration pure.
"""
import logging
import atexit
from typing import Optional
from opentelemetry import trace, _logs, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

try:
    from .config import (
        OTEL_ENDPOINT, OTEL_HEADERS, OTEL_PROTOCOL,
        SERVICE_NAME, SERVICE_NAMESPACE, DEPLOYMENT_ENVIRONMENT,
        RESOURCE_ATTRIBUTES,
        SPAN_EXPORT_INTERVAL_MS, LOG_EXPORT_INTERVAL_MS, METRIC_EXPORT_INTERVAL_MS,
        MAX_EXPORT_BATCH_SIZE, MAX_QUEUE_SIZE, SKIP_CLEANUP, CONSOLE_ENABLED
    )
except ImportError:
    from config import (
        OTEL_ENDPOINT, OTEL_HEADERS, OTEL_PROTOCOL,
        SERVICE_NAME, SERVICE_NAMESPACE, DEPLOYMENT_ENVIRONMENT,
        RESOURCE_ATTRIBUTES,
        SPAN_EXPORT_INTERVAL_MS, LOG_EXPORT_INTERVAL_MS, METRIC_EXPORT_INTERVAL_MS,
        MAX_EXPORT_BATCH_SIZE, MAX_QUEUE_SIZE, SKIP_CLEANUP, CONSOLE_ENABLED
    )

# Import console exporters for fallback
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter
from opentelemetry.sdk._logs.export import ConsoleLogExporter

# Safe console exporters that handle closed streams
class SafeConsoleSpanExporter:
    def __init__(self):
        self._exporter = ConsoleSpanExporter()
    
    def export(self, spans):
        try:
            return self._exporter.export(spans)
        except (ValueError, OSError):
            # Handle closed stdout/stderr
            return None
    
    def shutdown(self, timeout_millis=None):
        try:
            return self._exporter.shutdown()
        except (ValueError, OSError):
            return None
    
    def force_flush(self, timeout_millis=None):
        try:
            return self._exporter.force_flush(timeout_millis)
        except (ValueError, OSError):
            return None

class SafeConsoleLogExporter:
    def __init__(self):
        self._exporter = ConsoleLogExporter()
    
    def export(self, logs):
        try:
            return self._exporter.export(logs)
        except (ValueError, OSError):
            return None
    
    def shutdown(self, timeout_millis=None):
        try:
            return self._exporter.shutdown()
        except (ValueError, OSError):
            return None
    
    def force_flush(self, timeout_millis=None):
        try:
            return self._exporter.force_flush(timeout_millis)
        except (ValueError, OSError):
            return None

class SafeConsoleMetricExporter:
    def __init__(self):
        self._exporter = ConsoleMetricExporter()
        # Copy required attributes from the wrapped exporter
        self._preferred_temporality = getattr(self._exporter, '_preferred_temporality', {})
        self._preferred_aggregation = getattr(self._exporter, '_preferred_aggregation', {})
    
    def export(self, metrics_data, timeout_millis=None):
        try:
            return self._exporter.export(metrics_data, timeout_millis)
        except (ValueError, OSError):
            return None
    
    def shutdown(self, timeout=None):
        try:
            return self._exporter.shutdown()
        except (ValueError, OSError):
            return None
    
    def force_flush(self, timeout_millis=None):
        try:
            return self._exporter.force_flush(timeout_millis)
        except (ValueError, OSError):
            return None



# Choose the right exporters based on protocol
if OTEL_PROTOCOL == 'grpc':
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
else:  # http/protobuf
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

# Global instances - initialized once
_tracer_provider: Optional[TracerProvider] = None
_logger_provider: Optional[LoggerProvider] = None
_meter_provider: Optional[MeterProvider] = None
_tracer = None
_otel_logger = None
_logging_handler = None
_meter = None
_span_processor = None
_log_processor = None
_metric_reader = None
_atexit_registered = False

def get_resource() -> Resource:
    """Create resource with service information from config."""
    # Import here to get the latest values
    from .config import SERVICE_NAME, SERVICE_NAMESPACE, DEPLOYMENT_ENVIRONMENT, RESOURCE_ATTRIBUTES
    
    resource_dict = {
        ResourceAttributes.SERVICE_VERSION: "0.1.0",
    }
    
    # Add service info
    if SERVICE_NAME:
        resource_dict[ResourceAttributes.SERVICE_NAME] = SERVICE_NAME
    if SERVICE_NAMESPACE:
        resource_dict[ResourceAttributes.SERVICE_NAMESPACE] = SERVICE_NAMESPACE
    if DEPLOYMENT_ENVIRONMENT:
        resource_dict[ResourceAttributes.DEPLOYMENT_ENVIRONMENT] = DEPLOYMENT_ENVIRONMENT
    
    # Add any other resource attributes from config
    for key, value in RESOURCE_ATTRIBUTES.items():
        if key not in ['service.name', 'service.namespace', 'deployment.environment']:
            resource_dict[key] = value
    
    return Resource.create(resource_dict)

def get_tracer():
    """Get or create the global tracer instance."""
    global _tracer_provider, _tracer, _span_processor
    
    if _tracer is None:
        # Create resource
        resource = get_resource()
        
        # Create tracer provider
        _tracer_provider = TracerProvider(resource=resource)
        
        # Choose exporter(s) based on configuration
        exporters = []
        
        if OTEL_ENDPOINT:
            # Create OTLP exporter - add /v1/traces for traces
            trace_endpoint = OTEL_ENDPOINT
            if not trace_endpoint.endswith('/v1/traces'):
                trace_endpoint = trace_endpoint.rstrip('/') + '/v1/traces'
            
            otlp_exporter = OTLPSpanExporter(
                endpoint=trace_endpoint,
                headers=OTEL_HEADERS,
            )
            exporters.append(otlp_exporter)
        
        if CONSOLE_ENABLED or not OTEL_ENDPOINT:
            # Add console exporter
            console_exporter = SafeConsoleSpanExporter()
            exporters.append(console_exporter)
        
        # Wrap exporter to catch and hide tracebacks
        class QuietSpanExporter:
            def __init__(self, wrapped_exporter):
                self._exporter = wrapped_exporter
                
            def export(self, spans):
                try:
                    return self._exporter.export(spans)
                except Exception as e:
                    # Log a clean error message instead of full traceback
                    logging.getLogger(__name__).error(f"Couldn't sync spans: {type(e).__name__}: {str(e)}")
                    return None
                    
            def shutdown(self, timeout_millis=None):
                try:
                    return self._exporter.shutdown(timeout_millis)
                except Exception:
                    return None
                    
            def force_flush(self, timeout_millis=None):
                try:
                    return self._exporter.force_flush(timeout_millis)
                except Exception:
                    return None

        # Composite exporter for multiple targets
        class CompositeSpanExporter:
            def __init__(self, exporters):
                self._exporters = [QuietSpanExporter(exp) for exp in exporters]
                
            def export(self, spans):
                results = []
                for exporter in self._exporters:
                    result = exporter.export(spans)
                    results.append(result)
                # Return success if any exporter succeeded
                return any(r is not None for r in results)
                    
            def shutdown(self, timeout_millis=None):
                for exporter in self._exporters:
                    exporter.shutdown(timeout_millis)
                    
            def force_flush(self, timeout_millis=None):
                for exporter in self._exporters:
                    exporter.force_flush(timeout_millis)
        
        # Add batch processor with composite exporter
        composite_exporter = CompositeSpanExporter(exporters)
        _span_processor = BatchSpanProcessor(
            composite_exporter,
            max_queue_size=MAX_QUEUE_SIZE,
            max_export_batch_size=MAX_EXPORT_BATCH_SIZE,
            schedule_delay_millis=SPAN_EXPORT_INTERVAL_MS,
            export_timeout_millis=5000,
        )
        
        _tracer_provider.add_span_processor(_span_processor)
        
        # Set as global tracer provider
        trace.set_tracer_provider(_tracer_provider)
        
        # Get tracer - use the actual service name from config
        from .config import SERVICE_NAME
        _tracer = trace.get_tracer(SERVICE_NAME, "0.1.0")
        
        # Register cleanup on exit
        _register_atexit()
    
    return _tracer

def get_logger_provider():
    """Get or create the global logger provider."""
    global _logger_provider, _otel_logger, _logging_handler, _log_processor
    
    if _logger_provider is None:
        # Create resource
        resource = get_resource()
        
        # Create logger provider
        _logger_provider = LoggerProvider(resource=resource)
        
        # Choose exporter(s) based on configuration
        exporters = []
        
        if OTEL_ENDPOINT:
            # Create OTLP log exporter - add /v1/logs for logs
            log_endpoint = OTEL_ENDPOINT
            if not log_endpoint.endswith('/v1/logs'):
                log_endpoint = log_endpoint.rstrip('/') + '/v1/logs'
            
            otlp_exporter = OTLPLogExporter(
                endpoint=log_endpoint,
                headers=OTEL_HEADERS,
            )
            exporters.append(otlp_exporter)
        
        if CONSOLE_ENABLED or not OTEL_ENDPOINT:
            # Add console exporter
            console_exporter = SafeConsoleLogExporter()
            exporters.append(console_exporter)
        
        # Wrap exporter to catch and hide tracebacks
        class QuietLogExporter:
            def __init__(self, wrapped_exporter):
                self._exporter = wrapped_exporter
                
            def export(self, logs):
                try:
                    return self._exporter.export(logs)
                except Exception as e:
                    # Log a clean error message instead of full traceback
                    logging.getLogger(__name__).error(f"Couldn't sync logs: {type(e).__name__}: {str(e)}")
                    return None
                    
            def shutdown(self, timeout_millis=None):
                try:
                    return self._exporter.shutdown(timeout_millis)
                except Exception:
                    return None
                    
            def force_flush(self, timeout_millis=None):
                try:
                    return self._exporter.force_flush(timeout_millis)
                except Exception:
                    return None

        # Composite exporter for multiple targets
        class CompositeLogExporter:
            def __init__(self, exporters):
                self._exporters = [QuietLogExporter(exp) for exp in exporters]
                
            def export(self, logs):
                results = []
                for exporter in self._exporters:
                    result = exporter.export(logs)
                    results.append(result)
                # Return success if any exporter succeeded
                return any(r is not None for r in results)
                    
            def shutdown(self, timeout_millis=None):
                for exporter in self._exporters:
                    exporter.shutdown(timeout_millis)
                    
            def force_flush(self, timeout_millis=None):
                for exporter in self._exporters:
                    exporter.force_flush(timeout_millis)
        
        # Add batch processor with composite exporter
        composite_exporter = CompositeLogExporter(exporters)
        _log_processor = BatchLogRecordProcessor(
            composite_exporter,
            max_queue_size=MAX_QUEUE_SIZE,
            max_export_batch_size=MAX_EXPORT_BATCH_SIZE,
            schedule_delay_millis=LOG_EXPORT_INTERVAL_MS,
            export_timeout_millis=5000,
        )
        
        _logger_provider.add_log_record_processor(_log_processor)
        
        # Set as global logger provider
        _logs.set_logger_provider(_logger_provider)
        
        # Get logger
        _otel_logger = _logs.get_logger(__name__, "0.1.0")
        
        # Create logging handler
        _logging_handler = LoggingHandler(level=logging.INFO, logger_provider=_logger_provider)
        
        # Register cleanup on exit
        _register_atexit()
    
    return _logger_provider

def get_meter_provider():
    """Get or create the global meter provider."""
    global _meter_provider, _meter, _metric_reader
    
    if _meter_provider is None:
        # Create resource
        resource = get_resource()
        
        # Choose exporter(s) based on configuration
        exporters = []
        
        if OTEL_ENDPOINT:
            # Create OTLP metric exporter - add /v1/metrics for metrics
            metric_endpoint = OTEL_ENDPOINT
            if not metric_endpoint.endswith('/v1/metrics'):
                metric_endpoint = metric_endpoint.rstrip('/') + '/v1/metrics'
            
            otlp_exporter = OTLPMetricExporter(
                endpoint=metric_endpoint,
                headers=OTEL_HEADERS,
            )
            exporters.append(otlp_exporter)
        
        if CONSOLE_ENABLED or not OTEL_ENDPOINT:
            # Add console exporter
            console_exporter = SafeConsoleMetricExporter()
            exporters.append(console_exporter)
        
        # Wrap exporter to catch and hide tracebacks
        class QuietMetricExporter:
            def __init__(self, wrapped_exporter):
                self._exporter = wrapped_exporter
                # Copy required attributes from the wrapped exporter
                self._preferred_temporality = getattr(wrapped_exporter, '_preferred_temporality', {})
                self._preferred_aggregation = getattr(wrapped_exporter, '_preferred_aggregation', {})
                
            def export(self, metrics_data, timeout_millis=None):
                try:
                    return self._exporter.export(metrics_data, timeout_millis)
                except Exception as e:
                    # Log a clean error message instead of full traceback
                    logging.getLogger(__name__).error(f"Couldn't sync metrics: {type(e).__name__}: {str(e)}")
                    return None
                    
            def shutdown(self, timeout=None):
                try:
                    return self._exporter.shutdown(timeout)
                except Exception:
                    return None
                    
            def force_flush(self, timeout_millis=None):
                try:
                    return self._exporter.force_flush(timeout_millis)
                except Exception:
                    return None

        # Composite exporter for multiple targets
        class CompositeMetricExporter:
            def __init__(self, exporters):
                self._exporters = [QuietMetricExporter(exp) for exp in exporters]
                # Use attributes from first exporter as default
                if exporters:
                    first = self._exporters[0]
                    self._preferred_temporality = getattr(first, '_preferred_temporality', {})
                    self._preferred_aggregation = getattr(first, '_preferred_aggregation', {})
                else:
                    self._preferred_temporality = {}
                    self._preferred_aggregation = {}
                
            def export(self, metrics_data, timeout_millis=None):
                results = []
                for exporter in self._exporters:
                    result = exporter.export(metrics_data, timeout_millis)
                    results.append(result)
                # Return success if any exporter succeeded
                return any(r is not None for r in results)
                    
            def shutdown(self, timeout=None):
                for exporter in self._exporters:
                    exporter.shutdown(timeout)
                    
            def force_flush(self, timeout_millis=None):
                for exporter in self._exporters:
                    exporter.force_flush(timeout_millis)
        
        # Create metric reader with composite exporter
        composite_exporter = CompositeMetricExporter(exporters)
        _metric_reader = PeriodicExportingMetricReader(
            exporter=composite_exporter,
            export_interval_millis=METRIC_EXPORT_INTERVAL_MS,
            export_timeout_millis=5000,
        )
        
        # Create meter provider
        _meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[_metric_reader]
        )
        
        # Set as global meter provider
        metrics.set_meter_provider(_meter_provider)
        
        # Get meter
        _meter = metrics.get_meter(__name__, "0.1.0")
        
        # Register cleanup on exit
        _register_atexit()
    
    return _meter_provider

def get_meter():
    """Get or create the global meter instance."""
    get_meter_provider()  # Ensure provider is initialized
    return _meter

def get_logging_handler():
    """Get the OpenTelemetry logging handler."""
    get_logger_provider()  # Ensure provider is initialized
    return _logging_handler

def setup_logging(logger_name: Optional[str] = None):
    """Set up Python logging to send to OpenTelemetry."""
    handler = get_logging_handler()
    if not handler:
        return None
    
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger()
    
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    return logger

def _cleanup_on_exit():
    """Cleanup function called on process exit."""
    if SKIP_CLEANUP:
        return
    
    # Production cleanup - flush first, then shutdown
    global _tracer_provider, _logger_provider, _meter_provider
    global _span_processor, _log_processor, _metric_reader
    
    try:
        # First, force flush all pending data with timeout
        if _span_processor:
            _span_processor.force_flush(timeout_millis=2000)
        if _log_processor:
            _log_processor.force_flush(timeout_millis=2000)
        if _metric_reader:
            _metric_reader.force_flush(timeout_millis=2000)
        
        # Then shutdown processors/readers
        if _span_processor:
            _span_processor.shutdown(timeout_millis=2000)
        if _log_processor:
            _log_processor.shutdown(timeout_millis=2000)
        if _metric_reader:
            _metric_reader.shutdown(timeout_millis=2000)
        
        # Finally shutdown providers
        if _tracer_provider:
            _tracer_provider.shutdown(timeout_millis=2000)
        if _logger_provider:
            _logger_provider.shutdown(timeout_millis=2000)
        if _meter_provider:
            _meter_provider.shutdown(timeout_millis=2000)
    except Exception:
        # Ignore shutdown errors to prevent crashes during exit
        pass

def _register_atexit():
    """Register the cleanup function to run on exit."""
    global _atexit_registered
    if not _atexit_registered:
        atexit.register(_cleanup_on_exit)
        _atexit_registered = True

def force_flush():
    """Force flush all telemetry data immediately (blocks)."""
    global _span_processor, _log_processor, _metric_reader
    
    if _span_processor:
        _span_processor.force_flush(timeout_millis=1000)
    if _log_processor:
        _log_processor.force_flush(timeout_millis=1000)
    if _metric_reader:
        _metric_reader.force_flush(timeout_millis=1000)

def trigger_export():
    """Just rely on the fast background export - no-op for simplicity."""
    pass

def shutdown():
    """Manually shutdown all OpenTelemetry providers."""
    _cleanup_on_exit()