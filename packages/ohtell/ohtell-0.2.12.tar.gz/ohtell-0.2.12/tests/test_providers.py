"""
Test OTEL providers functionality.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
import logging


def test_get_tracer():
    """Test tracer creation and caching.""" 
    from ohtell.providers import get_tracer
    
    with patch('ohtell.providers.trace') as mock_trace:
        mock_tracer = MagicMock()
        mock_trace.get_tracer.return_value = mock_tracer
        
        # First call should create tracer
        tracer1 = get_tracer()
        assert tracer1 is mock_tracer
        
        # Second call should return cached tracer
        tracer2 = get_tracer()
        assert tracer2 is tracer1
        
        # get_tracer should only be called once
        mock_trace.get_tracer.assert_called_once_with("otel-wrapper", "0.1.0")


def test_get_meter():
    """Test meter creation and caching."""
    from ohtell.providers import get_meter
    
    with patch('ohtell.providers.metrics') as mock_metrics:
        mock_meter = MagicMock()
        mock_metrics.get_meter.return_value = mock_meter
        
        # First call should create meter
        meter1 = get_meter()
        assert meter1 is mock_meter
        
        # Second call should return cached meter
        meter2 = get_meter()
        assert meter2 is meter1


def test_setup_logging():
    """Test logging setup."""
    from ohtell.providers import setup_logging
    
    with patch('ohtell.providers.logging') as mock_logging:
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger
        
        # Test with custom name
        logger = setup_logging("test_logger")
        
        mock_logging.getLogger.assert_called_with("test_logger")
        assert logger is mock_logger
        
        # Test with default name
        setup_logging()
        mock_logging.getLogger.assert_called_with("otel-wrapper")


@patch('ohtell.providers._span_processor')
@patch('ohtell.providers._log_processor') 
@patch('ohtell.providers._metric_reader')
def test_force_flush(mock_metric_reader, mock_log_processor, mock_span_processor):
    """Test force flush functionality."""
    from ohtell.providers import force_flush
    
    # Set up mocks
    mock_span_processor.force_flush.return_value = True
    mock_log_processor.force_flush.return_value = True
    mock_metric_reader.force_flush.return_value = True
    
    # Test successful flush
    result = force_flush()
    assert result is True
    
    mock_span_processor.force_flush.assert_called_once()
    mock_log_processor.force_flush.assert_called_once()  
    mock_metric_reader.force_flush.assert_called_once()


@patch('ohtell.providers.threading')
def test_trigger_export(mock_threading):
    """Test trigger export functionality."""
    from ohtell.providers import trigger_export
    
    mock_thread = MagicMock()
    mock_threading.Thread.return_value = mock_thread
    
    # Test trigger export
    trigger_export()
    
    mock_threading.Thread.assert_called_once()
    mock_thread.start.assert_called_once()


@patch('ohtell.providers._tracer_provider')
@patch('ohtell.providers._logger_provider')
@patch('ohtell.providers._meter_provider')
def test_shutdown(mock_meter_provider, mock_logger_provider, mock_tracer_provider):
    """Test shutdown functionality."""
    from ohtell.providers import shutdown
    
    # Test shutdown
    shutdown()
    
    mock_tracer_provider.shutdown.assert_called_once()
    mock_logger_provider.shutdown.assert_called_once()
    mock_meter_provider.shutdown.assert_called_once()


def test_provider_initialization():
    """Test that providers are initialized correctly."""
    # Reset global state
    import otel_wrapper.providers as providers
    providers._tracer_provider = None
    providers._logger_provider = None
    providers._meter_provider = None
    
    with patch('ohtell.providers.TracerProvider') as mock_tracer_provider_class:
        with patch('ohtell.providers.LoggerProvider') as mock_logger_provider_class:
            with patch('ohtell.providers.MeterProvider') as mock_meter_provider_class:
                with patch('ohtell.providers.Resource') as mock_resource_class:
                    with patch('ohtell.providers.OTLPSpanExporter'):
                        with patch('ohtell.providers.OTLPLogExporter'):
                            with patch('ohtell.providers.OTLPMetricExporter'):
                                
                                # Mock instances
                                mock_tracer_provider = MagicMock()
                                mock_logger_provider = MagicMock()
                                mock_meter_provider = MagicMock()
                                mock_resource = MagicMock()
                                
                                mock_tracer_provider_class.return_value = mock_tracer_provider
                                mock_logger_provider_class.return_value = mock_logger_provider
                                mock_meter_provider_class.return_value = mock_meter_provider
                                mock_resource_class.create.return_value = mock_resource
                                
                                # This should trigger initialization
                                from ohtell.providers import get_tracer
                                get_tracer()
                                
                                # Check providers were created
                                mock_tracer_provider_class.assert_called_once_with(resource=mock_resource)
                                mock_logger_provider_class.assert_called_once_with(resource=mock_resource)
                                mock_meter_provider_class.assert_called_once_with(resource=mock_resource)