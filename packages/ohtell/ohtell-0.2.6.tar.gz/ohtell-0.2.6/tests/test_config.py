"""
Test configuration and initialization functionality.
"""

import pytest
import os
from unittest.mock import patch, MagicMock


def test_parse_resource_attributes():
    """Test parsing resource attributes string."""
    from ohtell.config import parse_resource_attributes
    
    # Empty string
    assert parse_resource_attributes("") == {}
    
    # Single attribute
    result = parse_resource_attributes("service.name=test-app")
    assert result == {"service.name": "test-app"}
    
    # Multiple attributes
    result = parse_resource_attributes("service.name=test-app,service.version=1.0.0")
    assert result == {
        "service.name": "test-app",
        "service.version": "1.0.0"
    }
    
    # With spaces
    result = parse_resource_attributes("key1 = value1 , key2 = value2")
    assert result == {
        "key1": "value1",
        "key2": "value2"
    }


def test_parse_headers():
    """Test parsing headers string."""
    from ohtell.config import parse_headers
    
    # Empty string
    assert parse_headers("") == {}
    
    # Authorization header with URL encoding
    auth_header = "Authorization=Bearer%20token123"
    result = parse_headers(auth_header)
    assert result == {"Authorization": "Bearer token123"}
    
    # Multiple headers
    headers_str = "Content-Type=application/json,Accept=application/json"
    result = parse_headers(headers_str)
    assert result == {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def test_init_function():
    """Test the init function for configuring OTEL."""
    from ohtell.config import init, SERVICE_NAME, SERVICE_NAMESPACE, DEPLOYMENT_ENVIRONMENT
    
    # Create mock config
    config = MagicMock()
    config.otel.endpoint = "http://localhost:4317"
    config.otel.headers = "Authorization=Bearer test123"
    config.otel.resource_attributes = "custom.attr=value"
    config.otel.protocol = "grpc"
    
    with patch.dict(os.environ, {}, clear=True):
        init(config, "test-app", "TestNamespace", "production")
        
        # Check environment variables were set
        assert os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] == "http://localhost:4317"
        assert os.environ["OTEL_EXPORTER_OTLP_HEADERS"] == "Authorization=Bearer test123"
        assert os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] == "grpc"
        assert os.environ["OTEL_SERVICE_NAME"] == "test-app"
        
        # Check resource attributes include our values
        resource_attrs = os.environ["OTEL_RESOURCE_ATTRIBUTES"]
        assert "service.name=test-app" in resource_attrs
        assert "service.namespace=TestNamespace" in resource_attrs
        assert "deployment.environment=production" in resource_attrs
        assert "custom.attr=value" in resource_attrs


def test_init_with_env_vars():
    """Test init function respects existing environment variables."""
    from ohtell.config import init
    
    config = MagicMock()
    config.otel = None  # No otel config
    
    with patch.dict(os.environ, {
        "OTEL_DEPLOYMENT_ENVIRONMENT": "staging",
        "ENV": "development"
    }):
        init(config, "test-app")
        
        # Should use OTEL_DEPLOYMENT_ENVIRONMENT over ENV
        resource_attrs = os.environ.get("OTEL_RESOURCE_ATTRIBUTES", "")
        assert "deployment.environment=staging" in resource_attrs


def test_init_fallback_env():
    """Test init function fallback environment detection."""
    from ohtell.config import init
    
    config = MagicMock()
    config.otel = None
    
    with patch.dict(os.environ, {"ENV": "testing"}, clear=True):
        init(config, "test-app")
        
        # Should use ENV as fallback
        resource_attrs = os.environ.get("OTEL_RESOURCE_ATTRIBUTES", "")
        assert "deployment.environment=testing" in resource_attrs


def test_setup_otel_from_config():
    """Test setup_otel_from_config function."""
    from ohtell.config import setup_otel_from_config
    
    # Config without otel section
    config_no_otel = MagicMock()
    config_no_otel.otel = None
    
    # Should not raise error
    setup_otel_from_config(config_no_otel)
    
    # Config with otel section
    config = MagicMock()
    config.otel.endpoint = "http://test:4317"
    config.otel.headers = "test-header=value"
    config.otel.resource_attributes = "test.attr=value"
    config.otel.protocol = "http/protobuf"
    
    with patch.dict(os.environ, {}, clear=True):
        setup_otel_from_config(config)
        
        assert os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] == "http://test:4317"
        assert os.environ["OTEL_EXPORTER_OTLP_HEADERS"] == "test-header=value"
        assert os.environ["OTEL_RESOURCE_ATTRIBUTES"] == "test.attr=value"
        assert os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] == "http/protobuf"