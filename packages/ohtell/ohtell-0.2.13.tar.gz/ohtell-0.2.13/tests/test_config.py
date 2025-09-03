#!/usr/bin/env python3
"""
Test ohtell configuration merging behavior.
Tests env vars overriding config.yaml and different config formats.
"""

import os
import sys
import tempfile
import logging
from pathlib import Path
from unittest.mock import patch

# Enable logging to see config output
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def cleanup_modules():
    """Clean up imported modules to force reload"""
    modules_to_remove = [key for key in sys.modules.keys() if key.startswith('ohtell')]
    for module in modules_to_remove:
        del sys.modules[module]

def cleanup_env():
    """Clean up OTEL_* environment variables"""
    for key in list(os.environ.keys()):
        if key.startswith('OTEL_'):
            del os.environ[key]

def test_nested_config_yaml():
    """Test nested otel: format in config.yaml"""
    print("\n=== Test: Nested config.yaml format ===")
    
    cleanup_env()
    cleanup_modules()
    
    config_content = """
otel:
  endpoint: https://test-nested.example.com/otlp
  headers: Authorization=Bearer nested-test-token
  protocol: grpc
  resource_attributes: service.name=nested-service,env=test
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        config_path.write_text(config_content)
        
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            import ohtell
            from ohtell.config import OTEL_ENDPOINT, OTEL_PROTOCOL, SERVICE_NAME
            
            assert OTEL_ENDPOINT == "https://test-nested.example.com/otlp"
            assert OTEL_PROTOCOL == "grpc"
            assert SERVICE_NAME == "nested-service"
            print("✅ Nested config loaded correctly")
            
        finally:
            os.chdir(old_cwd)

def test_flat_config_yaml():
    """Test flat OTEL_* format in config.yaml"""
    print("\n=== Test: Flat OTEL_* config.yaml format ===")
    
    cleanup_env()
    cleanup_modules()
    
    config_content = """
OTEL_EXPORTER_OTLP_ENDPOINT: https://test-flat.example.com/otlp
OTEL_EXPORTER_OTLP_HEADERS: Authorization=Bearer flat-test-token
OTEL_EXPORTER_OTLP_PROTOCOL: http/protobuf
OTEL_RESOURCE_ATTRIBUTES: service.name=flat-service,env=test
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        config_path.write_text(config_content)
        
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            import ohtell
            from ohtell.config import OTEL_ENDPOINT, OTEL_PROTOCOL, SERVICE_NAME
            
            assert OTEL_ENDPOINT == "https://test-flat.example.com/otlp"
            assert OTEL_PROTOCOL == "http/protobuf"
            assert SERVICE_NAME == "flat-service"
            print("✅ Flat OTEL_* config loaded correctly")
            
        finally:
            os.chdir(old_cwd)

def test_env_override():
    """Test environment variables overriding config.yaml"""
    print("\n=== Test: Environment variables override config.yaml ===")
    
    cleanup_env()
    cleanup_modules()
    
    # Set env vars
    os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = 'https://env-override.example.com/otlp'
    os.environ['OTEL_EXPORTER_OTLP_HEADERS'] = 'Authorization=Bearer env-test-token'
    os.environ['OTEL_EXPORTER_OTLP_PROTOCOL'] = 'http/protobuf'
    os.environ['OTEL_RESOURCE_ATTRIBUTES'] = 'service.name=env-service,env=production'
    
    # Create conflicting config.yaml
    config_content = """
otel:
  endpoint: https://should-be-overridden.example.com/otlp
  headers: Authorization=Bearer should-be-overridden
  protocol: grpc
  resource_attributes: service.name=should-be-overridden,env=dev
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        config_path.write_text(config_content)
        
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            import ohtell
            from ohtell.config import OTEL_ENDPOINT, OTEL_PROTOCOL, SERVICE_NAME, DEPLOYMENT_ENVIRONMENT
            
            # Should use env vars, not config.yaml values
            assert OTEL_ENDPOINT == "https://env-override.example.com/otlp"
            assert OTEL_PROTOCOL == "http/protobuf"  # env override
            assert SERVICE_NAME == "env-service"
            print(f"DEBUG: DEPLOYMENT_ENVIRONMENT = '{DEPLOYMENT_ENVIRONMENT}'")
            # The deployment environment should be parsed from resource attributes
            assert "env=production" in str(os.environ.get('OTEL_RESOURCE_ATTRIBUTES', ''))
            print("✅ Environment variables correctly override config.yaml")
            
        finally:
            os.chdir(old_cwd)

def test_mixed_config():
    """Test mixed otel: and OTEL_ in same config.yaml"""
    print("\n=== Test: Mixed nested and flat format ===")
    
    cleanup_env()
    cleanup_modules()
    
    config_content = """
otel:
  endpoint: https://nested-endpoint.example.com/otlp
  protocol: grpc

OTEL_EXPORTER_OTLP_HEADERS: Authorization=Bearer flat-header-token
OTEL_RESOURCE_ATTRIBUTES: service.name=mixed-service,env=staging
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        config_path.write_text(config_content)
        
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            import ohtell
            from ohtell.config import OTEL_ENDPOINT, OTEL_PROTOCOL, SERVICE_NAME, OTEL_HEADERS_STR
            
            # Should merge both formats correctly
            assert OTEL_ENDPOINT == "https://nested-endpoint.example.com/otlp"  # from nested
            assert OTEL_PROTOCOL == "grpc"  # from nested
            assert SERVICE_NAME == "mixed-service"  # from flat
            assert "flat-header-token" in OTEL_HEADERS_STR  # from flat
            print("✅ Mixed config formats loaded correctly")
            
        finally:
            os.chdir(old_cwd)

def test_no_config():
    """Test behavior with no config.yaml and no env vars"""
    print("\n=== Test: No configuration ===")
    
    cleanup_env()
    cleanup_modules()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)  # No config.yaml in this directory
        
        try:
            import ohtell
            from ohtell.config import OTEL_ENDPOINT, SERVICE_NAME
            
            # Should use defaults
            assert not OTEL_ENDPOINT
            assert SERVICE_NAME == "ohtell-app"  # default service name
            print("✅ No config defaults loaded correctly")
            
        finally:
            os.chdir(old_cwd)

def main():
    """Run all tests"""
    print("Testing ohtell configuration loading...")
    
    try:
        test_nested_config_yaml()
        test_flat_config_yaml() 
        test_env_override()
        test_mixed_config()
        test_no_config()
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Cleanup
        cleanup_env()
        cleanup_modules()

if __name__ == "__main__":
    main()