import os
from pathlib import Path
from typing import Dict, Any, Optional

# Try to load config.yaml if available
try:
    from omegaconf import OmegaConf
    config_path = Path.cwd() / "config.yaml"
    if config_path.exists():
        yaml_config = OmegaConf.load(config_path)
        
        # Use OmegaConf to resolve variables and merge configurations
        # Support both nested otel: format and flat OTEL_ variable format
        def safe_get(config, path, default=None):
            try:
                return OmegaConf.select(config, path) or default
            except:
                return default
        
        otel_config = {
            'endpoint': safe_get(yaml_config, 'otel.endpoint') or safe_get(yaml_config, 'otel.OTEL_EXPORTER_OTLP_ENDPOINT') or yaml_config.get('OTEL_EXPORTER_OTLP_ENDPOINT'),
            'headers': safe_get(yaml_config, 'otel.headers') or safe_get(yaml_config, 'otel.OTEL_EXPORTER_OTLP_HEADERS') or yaml_config.get('OTEL_EXPORTER_OTLP_HEADERS'),
            'protocol': safe_get(yaml_config, 'otel.protocol') or safe_get(yaml_config, 'otel.OTEL_EXPORTER_OTLP_PROTOCOL') or yaml_config.get('OTEL_EXPORTER_OTLP_PROTOCOL'),
            'resource_attributes': safe_get(yaml_config, 'otel.resource_attributes') or safe_get(yaml_config, 'otel.OTEL_RESOURCE_ATTRIBUTES') or yaml_config.get('OTEL_RESOURCE_ATTRIBUTES'),
            'service_name': safe_get(yaml_config, 'otel.service_name') or safe_get(yaml_config, 'otel.OTEL_SERVICE_NAME') or yaml_config.get('OTEL_SERVICE_NAME'),
            'console': safe_get(yaml_config, 'otel.console') or safe_get(yaml_config, 'otel.OTEL_CONSOLE_ENABLED') or yaml_config.get('OTEL_CONSOLE_ENABLED'),
        }
        
        # Remove None values
        otel_config = {k: v for k, v in otel_config.items() if v is not None}
    else:
        otel_config = {}
except (ImportError, Exception):
    otel_config = {}

def parse_resource_attributes(attr_string: str) -> Dict[str, str]:
    """Parse resource attributes string into dictionary."""
    if not attr_string:
        return {}
    
    attrs = {}
    for pair in attr_string.split(','):
        if '=' in pair:
            key, value = pair.split('=', 1)
            attrs[key.strip()] = value.strip()
    return attrs

def parse_headers(headers_string: str) -> Dict[str, str]:
    """Parse headers string into dictionary."""
    if not headers_string:
        return {}
    
    headers = {}
    # Handle Authorization header format - decode URL encoding
    if headers_string.startswith('Authorization='):
        import urllib.parse
        auth_value = headers_string.split('=', 1)[1]
        # URL decode the value
        headers['Authorization'] = urllib.parse.unquote(auth_value)
    else:
        # Handle comma-separated key=value pairs
        for pair in headers_string.split(','):
            if '=' in pair:
                key, value = pair.split('=', 1)
                headers[key.strip()] = value.strip()
    return headers

# Configuration - Environment variables take precedence over config file
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", otel_config.get('endpoint', ''))
OTEL_HEADERS_STR = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", otel_config.get('headers', ''))
OTEL_PROTOCOL = os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", otel_config.get('protocol', 'http/protobuf'))
RESOURCE_ATTRIBUTES_STR = os.getenv("OTEL_RESOURCE_ATTRIBUTES", otel_config.get('resource_attributes', ''))

# Parse configuration
OTEL_HEADERS = parse_headers(OTEL_HEADERS_STR)
RESOURCE_ATTRIBUTES = parse_resource_attributes(RESOURCE_ATTRIBUTES_STR)

# Service configuration
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", RESOURCE_ATTRIBUTES.get('service.name', 'ohtell-app'))
SERVICE_NAMESPACE = RESOURCE_ATTRIBUTES.get('service.namespace', '')
DEPLOYMENT_ENVIRONMENT = RESOURCE_ATTRIBUTES.get('deployment.environment', 'development')

# Export configuration - Environment variables with config file fallbacks
SPAN_EXPORT_INTERVAL_MS = int(os.getenv("OTEL_SPAN_EXPORT_INTERVAL_MS", otel_config.get('span_export_interval_ms', "500")))   # 0.5 seconds
LOG_EXPORT_INTERVAL_MS = int(os.getenv("OTEL_LOG_EXPORT_INTERVAL_MS", otel_config.get('log_export_interval_ms', "500")))     # 0.5 seconds  
METRIC_EXPORT_INTERVAL_MS = int(os.getenv("OTEL_METRIC_EXPORT_INTERVAL_MS", otel_config.get('metric_export_interval_ms', "30000")))  # 30 seconds

# Batch sizes - smaller for faster export
MAX_EXPORT_BATCH_SIZE = int(os.getenv("OTEL_MAX_EXPORT_BATCH_SIZE", otel_config.get('max_export_batch_size', "50")))  # Small batches
MAX_QUEUE_SIZE = int(os.getenv("OTEL_MAX_QUEUE_SIZE", otel_config.get('max_queue_size', "512")))  # Smaller queue

# Metrics sampling configuration to reduce volume
METRICS_SAMPLING_RATE = float(os.getenv("OTEL_METRICS_SAMPLING_RATE", otel_config.get('metrics_sampling_rate', "0.1")))  # Sample 10% of metrics
METRICS_ENABLED = os.getenv("OTEL_METRICS_ENABLED", str(otel_config.get('metrics_enabled', "true"))).lower() == "true"

# Cleanup configuration
SKIP_CLEANUP = os.getenv("OTEL_WRAPPER_SKIP_CLEANUP", str(otel_config.get('skip_cleanup', "true"))).lower() == "true"

# Console output configuration
CONSOLE_ENABLED = os.getenv("OTEL_CONSOLE_ENABLED", str(otel_config.get('console', "false"))).lower() == "true"


def init(config: Any, app_name: str, service_namespace: str = "AI", deployment_env: Optional[str] = None) -> None:
    """
    Initialize OpenTelemetry with configuration and application name.
    
    Args:
        config: Configuration object with otel section containing:
            - endpoint: OTLP endpoint URL
            - headers: OTLP headers string
            - resource_attributes: Resource attributes string
            - protocol: OTLP protocol (optional)
        app_name: The name of the application (e.g., 'proxy-mcp-server', 'ai-core', 'ai-os-chat')
        service_namespace: The namespace group for the service (default: "AI")
        deployment_env: Deployment environment (e.g., 'production', 'staging', 'development'). 
                       If not provided, uses OTEL_DEPLOYMENT_ENVIRONMENT env var, then ENV env var, 
                       or 'development' as default.
    """
    global SERVICE_NAME, SERVICE_NAMESPACE, DEPLOYMENT_ENVIRONMENT, RESOURCE_ATTRIBUTES
    
    # Reset the tracer to ensure it uses the new service name
    from . import providers
    providers._tracer = None
    providers._tracer_provider = None
    providers._span_processor = None
    
    # Set application name and namespace
    SERVICE_NAME = app_name
    SERVICE_NAMESPACE = service_namespace
    
    # Set deployment environment - priority: function param > OTEL_DEPLOYMENT_ENVIRONMENT > ENV > default
    if deployment_env:
        DEPLOYMENT_ENVIRONMENT = deployment_env
    else:
        DEPLOYMENT_ENVIRONMENT = os.getenv("OTEL_DEPLOYMENT_ENVIRONMENT") or os.getenv("ENV", "development")
    
    # Update resource attributes
    RESOURCE_ATTRIBUTES['service.name'] = app_name
    RESOURCE_ATTRIBUTES['service.namespace'] = service_namespace
    RESOURCE_ATTRIBUTES['deployment.environment'] = DEPLOYMENT_ENVIRONMENT
    
    # Process config if provided
    if hasattr(config, 'otel') and config.otel:
        # Set environment variables for OpenTelemetry configuration
        if hasattr(config.otel, 'endpoint') and config.otel.endpoint:
            os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = config.otel.endpoint
        
        if hasattr(config.otel, 'headers') and config.otel.headers:
            os.environ['OTEL_EXPORTER_OTLP_HEADERS'] = config.otel.headers
        
        if hasattr(config.otel, 'resource_attributes') and config.otel.resource_attributes:
            # Parse existing attributes but preserve our app_name, service_namespace, and deployment_environment
            existing_attrs = parse_resource_attributes(config.otel.resource_attributes)
            existing_attrs['service.name'] = app_name
            existing_attrs['service.namespace'] = service_namespace
            existing_attrs['deployment.environment'] = DEPLOYMENT_ENVIRONMENT
            # Update global RESOURCE_ATTRIBUTES
            RESOURCE_ATTRIBUTES.update(existing_attrs)
        
        if hasattr(config.otel, 'protocol') and config.otel.protocol:
            os.environ['OTEL_EXPORTER_OTLP_PROTOCOL'] = config.otel.protocol
    
    # Update environment variables with final resource attributes
    os.environ['OTEL_SERVICE_NAME'] = app_name
    attrs = []
    for key, value in RESOURCE_ATTRIBUTES.items():
        attrs.append(f"{key}={value}")
    os.environ['OTEL_RESOURCE_ATTRIBUTES'] = ','.join(attrs)
    
    print(f"OpenTelemetry initialized for application: {app_name}")
    print(f"  Service namespace: {service_namespace}")
    print(f"  Deployment environment: {DEPLOYMENT_ENVIRONMENT}")
    if hasattr(config, 'otel') and config.otel:
        print(f"  Endpoint: {config.otel.get('endpoint', 'Not set')}")
        print(f"  Protocol: {config.otel.get('protocol', 'http/protobuf')}")
        print(f"  Headers: {'Set' if config.otel.get('headers') else 'Not set'}")


def setup_otel_from_config(config: Any) -> None:
    """
    Setup OpenTelemetry configuration from a config object.
    
    Args:
        config: Configuration object with otel section containing:
            - endpoint: OTLP endpoint URL
            - headers: OTLP headers string
            - resource_attributes: Resource attributes string
            - protocol: OTLP protocol (optional)
    """
    if not hasattr(config, 'otel') or not config.otel:
        return
    
    # Set environment variables for OpenTelemetry configuration
    if hasattr(config.otel, 'endpoint') and config.otel.endpoint:
        os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = config.otel.endpoint
    
    if hasattr(config.otel, 'headers') and config.otel.headers:
        os.environ['OTEL_EXPORTER_OTLP_HEADERS'] = config.otel.headers
    
    if hasattr(config.otel, 'resource_attributes') and config.otel.resource_attributes:
        os.environ['OTEL_RESOURCE_ATTRIBUTES'] = config.otel.resource_attributes
    
    if hasattr(config.otel, 'protocol') and config.otel.protocol:
        os.environ['OTEL_EXPORTER_OTLP_PROTOCOL'] = config.otel.protocol
    
    print(f"OpenTelemetry configuration set from config:")
    print(f"  Endpoint: {config.otel.get('endpoint', 'Not set')}")
    print(f"  Protocol: {config.otel.get('protocol', 'http/protobuf')}")
    print(f"  Resource attributes: {config.otel.get('resource_attributes', 'Not set')}")
    print(f"  Headers: {'Set' if config.otel.get('headers') else 'Not set'}")

