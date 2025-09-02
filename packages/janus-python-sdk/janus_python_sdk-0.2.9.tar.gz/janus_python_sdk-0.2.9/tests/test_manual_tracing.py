"""
Unit tests for manual tool event tracing functions.

Tests the record_tool_event, start_tool_event, and finish_tool_event functions
with various scenarios including enabled/disabled tracing, edge cases, and
attribute correctness.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import time
from typing import Optional

# Import the functions we're testing
from janus_sdk import (
    record_tool_event,
    start_tool_event,
    finish_tool_event,
    ToolEventSpanHandle,
    init_tracing
)


class TestManualTracing(unittest.TestCase):
    """Test cases for manual tool event tracing functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock OpenTelemetry components
        self.mock_trace = Mock()
        self.mock_baggage = Mock()
        self.mock_otel_context = Mock()
        self.mock_span = Mock()
        self.mock_tracer = Mock()
        
        # Set up mock span attributes
        self.mock_span.set_attribute = Mock()
        self.mock_span.end = Mock()
        self.mock_span.get_span_context.return_value = Mock(trace_id=12345)
        self.mock_span.is_recording.return_value = True
        
        # Set up mock tracer
        # Create a context manager mock for start_as_current_span
        context_manager = Mock()
        context_manager.__enter__ = Mock(return_value=self.mock_span)
        context_manager.__exit__ = Mock(return_value=None)
        self.mock_tracer.start_as_current_span.return_value = context_manager
        self.mock_tracer.start_span.return_value = self.mock_span
        
        # Set up mock trace
        self.mock_trace.get_tracer.return_value = self.mock_tracer
        self.mock_trace.get_current_span.return_value = self.mock_span
        
        # Set up mock baggage
        self.mock_baggage.get_baggage.side_effect = lambda key: {
            "conv_id": "test-conv-123",
            "simulation_id": "test-sim-456",
            "janus_simulation": "true"
        }.get(key, None)

    def tearDown(self):
        """Clean up after tests."""
        # Reset any global state if needed
        pass

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    @patch('janus_sdk.trace', Mock())
    @patch('janus_sdk.baggage', Mock())
    @patch('janus_sdk.time.perf_counter')
    def test_record_tool_event_basic(self, mock_perf_counter):
        """Test basic record_tool_event functionality."""
        # Set up mocks
        mock_perf_counter.return_value = 100.0
        with patch('janus_sdk.trace', self.mock_trace), \
             patch('janus_sdk.baggage', self.mock_baggage):
            
            # Call the function
            record_tool_event(
                tool_name="test_tool",
                tool_input="test input",
                tool_output="test output"
            )
            
            # Verify tracer was called
            self.mock_trace.get_tracer.assert_called_once()
            self.mock_tracer.start_as_current_span.assert_called_once_with("test_tool_operation")
            
            # Verify span attributes were set
            self.mock_span.set_attribute.assert_any_call("function.name", "test_tool")
            self.mock_span.set_attribute.assert_any_call("function.input", "test input")
            self.mock_span.set_attribute.assert_any_call("function.output", "test output")
            self.mock_span.set_attribute.assert_any_call("function.success", True)

    @patch('janus_sdk._HAS_OTEL', False)
    def test_record_tool_event_tracing_disabled(self):
        """Test record_tool_event when tracing is disabled."""
        # Should return immediately without error
        result = record_tool_event("test_tool", "input", "output")
        self.assertIsNone(result)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', False)
    def test_record_tool_event_tracing_not_initialized(self):
        """Test record_tool_event when tracing is not initialized."""
        # Should return immediately without error
        result = record_tool_event("test_tool", "input", "output")
        self.assertIsNone(result)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    @patch('janus_sdk.trace', Mock())
    @patch('janus_sdk.baggage', Mock())
    def test_record_tool_event_with_error(self):
        """Test record_tool_event with error handling."""
        # Set up mocks
        with patch('janus_sdk.trace', self.mock_trace), \
             patch('janus_sdk.baggage', self.mock_baggage):
            
            # Call the function with an error
            error = Exception("Test error")
            record_tool_event(
                tool_name="test_tool",
                tool_input="test input",
                error=error
            )
            
            # Verify error attributes were set
            self.mock_span.set_attribute.assert_any_call("function.success", False)
            self.mock_span.set_attribute.assert_any_call("function.error", "Test error")
            self.mock_span.set_attribute.assert_any_call("function.error_type", "Exception")

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    @patch('janus_sdk.trace', Mock())
    @patch('janus_sdk.baggage', Mock())
    def test_record_tool_event_input_truncation(self):
        """Test that long inputs are truncated."""
        # Set up mocks
        with patch('janus_sdk.trace', self.mock_trace), \
             patch('janus_sdk.baggage', self.mock_baggage):
            
            # Create a long input string
            long_input = "x" * 150
            
            # Call the function
            record_tool_event(
                tool_name="test_tool",
                tool_input=long_input
            )
            
            # Verify input was truncated
            expected_truncated = "x" * 100 + "..."
            self.mock_span.set_attribute.assert_any_call("function.input", expected_truncated)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    @patch('janus_sdk.trace', Mock())
    @patch('janus_sdk.baggage', Mock())
    def test_record_tool_event_conversation_context(self):
        """Test that conversation context is properly set."""
        # Set up mocks
        with patch('janus_sdk.trace', self.mock_trace), \
             patch('janus_sdk.baggage', self.mock_baggage):
            
            # Call the function
            record_tool_event("test_tool")
            
            # Verify conversation context attributes were set
            self.mock_span.set_attribute.assert_any_call("conversation.id", "test-conv-123")
            self.mock_span.set_attribute.assert_any_call("janus.conversation_id", "test-conv-123")
            self.mock_span.set_attribute.assert_any_call("janus.simulation", True)
            self.mock_span.set_attribute.assert_any_call("janus.simulation_id", "test-sim-456")

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    @patch('janus_sdk.trace', Mock())
    @patch('janus_sdk.baggage', Mock())
    def test_start_tool_event_basic(self):
        """Test basic start_tool_event functionality."""
        # Set up mocks
        with patch('janus_sdk.trace', self.mock_trace), \
             patch('janus_sdk.baggage', self.mock_baggage):
            
            # Call the function
            handle = start_tool_event("test_tool", "test input")
            
            # Verify handle was returned
            self.assertIsInstance(handle, ToolEventSpanHandle)
            self.assertEqual(handle.span, self.mock_span)
            self.assertIsInstance(handle.start_time, float)
            
            # Verify tracer was called
            self.mock_trace.get_tracer.assert_called_once()
            self.mock_tracer.start_span.assert_called_once_with("test_tool_operation")
            
            # Verify span attributes were set
            self.mock_span.set_attribute.assert_any_call("function.name", "test_tool")
            self.mock_span.set_attribute.assert_any_call("function.input", "test input")

    @patch('janus_sdk._HAS_OTEL', False)
    def test_start_tool_event_tracing_disabled(self):
        """Test start_tool_event when tracing is disabled."""
        # Should return None
        result = start_tool_event("test_tool", "input")
        self.assertIsNone(result)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', False)
    def test_start_tool_event_tracing_not_initialized(self):
        """Test start_tool_event when tracing is not initialized."""
        # Should return None
        result = start_tool_event("test_tool", "input")
        self.assertIsNone(result)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    @patch('janus_sdk.trace', Mock())
    @patch('janus_sdk.baggage', Mock())
    def test_finish_tool_event_basic(self):
        """Test basic finish_tool_event functionality."""
        # Set up mocks
        with patch('janus_sdk.trace', self.mock_trace), \
             patch('janus_sdk.baggage', self.mock_baggage):
            
            # Create a handle
            handle = ToolEventSpanHandle(span=self.mock_span, start_time=100.0)
            
            # Mock time.perf_counter to return a later time
            with patch('time.perf_counter', return_value=100.5):
                # Call the function
                finish_tool_event(handle, "test output")
                
                # Verify span attributes were set
                self.mock_span.set_attribute.assert_any_call("function.output", "test output")
                self.mock_span.set_attribute.assert_any_call("function.success", True)
                self.mock_span.set_attribute.assert_any_call("function.duration_ms", 500.0)
                
                # Verify span was ended
                self.mock_span.end.assert_called_once()

    def test_finish_tool_event_none_handle(self):
        """Test finish_tool_event with None handle."""
        # Should not raise an error
        finish_tool_event(None, "output")

    def test_finish_tool_event_invalid_handle(self):
        """Test finish_tool_event with invalid handle."""
        # Create an invalid handle
        invalid_handle = Mock()
        del invalid_handle.span
        del invalid_handle.start_time
        
        # Should not raise an error
        finish_tool_event(invalid_handle, "output")

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    @patch('janus_sdk.trace', Mock())
    @patch('janus_sdk.baggage', Mock())
    def test_finish_tool_event_with_error(self):
        """Test finish_tool_event with error handling."""
        # Set up mocks
        with patch('janus_sdk.trace', self.mock_trace), \
             patch('janus_sdk.baggage', self.mock_baggage):
            
            # Create a handle
            handle = ToolEventSpanHandle(span=self.mock_span, start_time=100.0)
            
            # Mock time.perf_counter
            with patch('time.perf_counter', return_value=100.5):
                # Call the function with an error
                error = Exception("Test error")
                finish_tool_event(handle, error=error)
                
                # Verify error attributes were set
                self.mock_span.set_attribute.assert_any_call("function.success", False)
                self.mock_span.set_attribute.assert_any_call("function.error", "Test error")
                self.mock_span.set_attribute.assert_any_call("function.error_type", "Exception")

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    @patch('janus_sdk.trace', Mock())
    @patch('janus_sdk.baggage', Mock())
    def test_finish_tool_event_output_truncation(self):
        """Test that long outputs are truncated."""
        # Set up mocks
        with patch('janus_sdk.trace', self.mock_trace), \
             patch('janus_sdk.baggage', self.mock_baggage):
            
            # Create a handle
            handle = ToolEventSpanHandle(span=self.mock_span, start_time=100.0)
            
            # Create a long output string
            long_output = "x" * 150
            
            # Mock time.perf_counter
            with patch('time.perf_counter', return_value=100.5):
                # Call the function
                finish_tool_event(handle, long_output)
                
                # Verify output was truncated
                expected_truncated = "x" * 100 + "..."
                self.mock_span.set_attribute.assert_any_call("function.output", expected_truncated)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    @patch('janus_sdk.trace', Mock())
    @patch('janus_sdk.baggage', Mock())
    def test_start_finish_workflow(self):
        """Test the complete start_tool_event -> finish_tool_event workflow."""
        # Set up mocks
        with patch('janus_sdk.trace', self.mock_trace), \
             patch('janus_sdk.baggage', self.mock_baggage):
            
            # Start the tool event
            handle = start_tool_event("test_tool", "test input")
            self.assertIsInstance(handle, ToolEventSpanHandle)
            
            # Verify span was created but not ended
            self.mock_tracer.start_span.assert_called_once()
            self.mock_span.end.assert_not_called()
            
            # Finish the tool event
            with patch('time.perf_counter', return_value=100.5):
                finish_tool_event(handle, "test output")
                
                # Verify span was ended
                self.mock_span.end.assert_called_once()

    def test_tool_event_span_handle_dataclass(self):
        """Test the ToolEventSpanHandle dataclass."""
        # Create a handle
        span = Mock()
        start_time = 100.0
        handle = ToolEventSpanHandle(span=span, start_time=start_time)
        
        # Verify attributes
        self.assertEqual(handle.span, span)
        self.assertEqual(handle.start_time, start_time)


if __name__ == '__main__':
    unittest.main() 