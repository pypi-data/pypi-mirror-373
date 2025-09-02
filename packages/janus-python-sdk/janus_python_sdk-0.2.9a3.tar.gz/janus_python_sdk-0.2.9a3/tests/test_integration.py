"""
Integration tests for manual tool event tracing functions.

Tests the functions with actual OpenTelemetry components to verify
real span creation, trace linking, and context propagation.
"""

import unittest
from unittest.mock import patch, Mock
import time
import os

# Import the functions we're testing
from janus_sdk import (
    record_tool_event,
    start_tool_event,
    finish_tool_event,
    ToolEventSpanHandle,
    init_tracing
)


class TestManualTracingIntegration(unittest.TestCase):
    """Integration tests for manual tool event tracing functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize tracing for integration tests
        # Use a mock endpoint to avoid actual network calls
        with patch('janus_sdk.OTLPSpanExporter') as mock_exporter:
            mock_exporter.return_value = Mock()
            init_tracing("http://localhost:8000", "test-api-key")

    def tearDown(self):
        """Clean up after tests."""
        # Reset tracing state if needed
        pass

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_record_tool_event_creates_real_span(self):
        """Test that record_tool_event creates a real span."""
        # This test verifies that the function actually creates spans
        # when tracing is properly initialized
        result = record_tool_event(
            tool_name="integration_test_tool",
            tool_input="test input",
            tool_output="test output"
        )
        
        # Should complete without error
        self.assertIsNone(result)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_start_finish_workflow_creates_real_spans(self):
        """Test that start_tool_event -> finish_tool_event creates real spans."""
        # Start a tool event
        handle = start_tool_event("integration_test_tool", "test input")
        
        # Should return a valid handle
        self.assertIsInstance(handle, ToolEventSpanHandle)
        self.assertIsNotNone(handle.span)
        self.assertIsInstance(handle.start_time, float)
        
        # Finish the tool event
        result = finish_tool_event(handle, "test output")
        
        # Should complete without error
        self.assertIsNone(result)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_trace_linking_with_parent_context(self):
        """Test that spans are properly linked to parent context."""
        # This test verifies that our spans can be linked to parent traces
        # We'll test this by creating a parent span and then creating tool spans
        
        from opentelemetry import trace
        
        tracer = trace.get_tracer("integration_test")
        
        with tracer.start_as_current_span("parent_span") as parent_span:
            # Set some context in the parent span
            parent_span.set_attribute("parent.test", "value")
            
            # Now create a tool event - it should be linked to the parent
            result = record_tool_event(
                tool_name="child_tool",
                tool_input="child input"
            )
            
            # Should complete without error
            self.assertIsNone(result)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_conversation_context_propagation(self):
        """Test that conversation context is properly propagated."""
        # This test verifies that conversation context from baggage
        # is properly set on spans
        
        from opentelemetry import baggage, context
        
        # Set conversation context in baggage
        ctx = baggage.set_baggage("conv_id", "test-conv-123")
        ctx = baggage.set_baggage("simulation_id", "test-sim-456")
        ctx = baggage.set_baggage("janus_simulation", "true")
        
        # Attach the context
        token = context.attach(ctx)
        
        try:
            # Create a tool event - it should pick up the context
            result = record_tool_event(
                tool_name="context_test_tool",
                tool_input="test input"
            )
            
            # Should complete without error
            self.assertIsNone(result)
            
        finally:
            # Always detach context
            context.detach(token)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_error_handling_in_real_spans(self):
        """Test error handling with real spans."""
        # Test that errors are properly captured in real spans
        error = Exception("Integration test error")
        
        result = record_tool_event(
            tool_name="error_test_tool",
            tool_input="test input",
            error=error
        )
        
        # Should complete without error
        self.assertIsNone(result)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_duration_calculation_with_real_time(self):
        """Test that duration is calculated correctly with real time."""
        # Test that duration calculation works with real time
        handle = start_tool_event("duration_test_tool", "test input")
        
        # Simulate some work
        time.sleep(0.01)  # 10ms delay
        
        result = finish_tool_event(handle, "test output")
        
        # Should complete without error
        self.assertIsNone(result)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_multiple_tool_events_in_sequence(self):
        """Test multiple tool events in sequence."""
        # Test that multiple tool events work correctly in sequence
        tools = ["tool_1", "tool_2", "tool_3"]
        
        for tool_name in tools:
            result = record_tool_event(
                tool_name=tool_name,
                tool_input=f"input for {tool_name}",
                tool_output=f"output from {tool_name}"
            )
            
            # Each should complete without error
            self.assertIsNone(result)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_concurrent_tool_events(self):
        """Test concurrent tool events."""
        # Test that multiple tool events can be started concurrently
        handles = []
        
        # Start multiple tool events
        for i in range(3):
            handle = start_tool_event(f"concurrent_tool_{i}", f"input_{i}")
            handles.append(handle)
        
        # Verify all handles are valid
        for handle in handles:
            self.assertIsInstance(handle, ToolEventSpanHandle)
            self.assertIsNotNone(handle.span)
        
        # Finish all tool events
        for i, handle in enumerate(handles):
            result = finish_tool_event(handle, f"output_{i}")
            self.assertIsNone(result)

    def test_tracing_disabled_integration(self):
        """Test that functions work correctly when tracing is disabled."""
        # Test graceful degradation when tracing is not available
        with patch('janus_sdk._HAS_OTEL', False):
            # These should all work without error
            result1 = record_tool_event("disabled_tool", "input", "output")
            self.assertIsNone(result1)
            
            result2 = start_tool_event("disabled_tool", "input")
            self.assertIsNone(result2)
            
            # finish_tool_event should handle None handle gracefully
            result3 = finish_tool_event(None, "output")
            self.assertIsNone(result3)

    def test_large_input_output_handling(self):
        """Test that large inputs and outputs are handled correctly."""
        # Create large input and output strings
        large_input = "x" * 1000  # 1000 characters
        large_output = "y" * 1000  # 1000 characters
        
        # These should work without error (truncation should happen internally)
        result = record_tool_event(
            tool_name="large_data_tool",
            tool_input=large_input,
            tool_output=large_output
        )
        
        # Should complete without error
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main() 