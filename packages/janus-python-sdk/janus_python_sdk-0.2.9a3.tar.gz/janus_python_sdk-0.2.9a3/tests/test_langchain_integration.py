"""
LangChain integration tests for manual tool event tracing functions.

Tests the functions in a simulated LangChain environment using CrossBeam's
exact callback methods to verify real-world integration.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import time
from typing import Dict, Any, Optional

# Import the functions we're testing
from janus_sdk import (
    record_tool_event,
    start_tool_event,
    finish_tool_event,
    ToolEventSpanHandle,
    init_tracing
)


class MockLangChainCallback:
    """Mock LangChain callback handler that uses our manual tracing functions."""
    
    def __init__(self):
        self._spans: Dict[str, ToolEventSpanHandle] = {}
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, run_id: str, **kwargs) -> None:
        """Handle tool start event - start tracing."""
        tool_name = serialized.get("name", "unknown_tool")
        handle = start_tool_event(tool_name, input_str)
        if handle is not None:
            self._spans[run_id] = handle
    
    def on_tool_end(self, output: str, run_id: str, **kwargs) -> None:
        """Handle tool end event - finish tracing successfully."""
        if run_id in self._spans:
            finish_tool_event(self._spans.pop(run_id), tool_output=output)
    
    def on_tool_error(self, error: Exception, run_id: str, **kwargs) -> None:
        """Handle tool error event - finish tracing with error."""
        if run_id in self._spans:
            finish_tool_event(self._spans.pop(run_id), error=error)
    
    def on_agent_action(self, action: Dict[str, Any], **kwargs) -> None:
        """Handle agent action event."""
        # Could use record_tool_event for one-shot agent actions
        pass
    
    def on_agent_finish(self, finish: Dict[str, Any], **kwargs) -> None:
        """Handle agent finish event."""
        # Could use record_tool_event for agent completion
        pass
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: list, **kwargs) -> None:
        """Handle LLM start event."""
        # Could use record_tool_event for LLM calls
        pass


class TestLangChainIntegration(unittest.TestCase):
    """LangChain integration tests for manual tool event tracing functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize tracing for integration tests
        with patch('janus_sdk.OTLPSpanExporter') as mock_exporter:
            mock_exporter.return_value = Mock()
            init_tracing("http://localhost:8000", "test-api-key")
        
        # Create our mock callback handler
        self.callback = MockLangChainCallback()

    def tearDown(self):
        """Clean up after tests."""
        # Clear any remaining spans
        self.callback._spans.clear()

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_tool_start_end_workflow(self):
        """Test the complete tool start -> end workflow."""
        # Simulate a tool start
        serialized = {"name": "search_tool"}
        input_str = "search query"
        run_id = "run_123"
        
        # Start the tool
        self.callback.on_tool_start(serialized, input_str, run_id)
        
        # Verify span was created
        self.assertIn(run_id, self.callback._spans)
        handle = self.callback._spans[run_id]
        self.assertIsInstance(handle, ToolEventSpanHandle)
        self.assertIsNotNone(handle.span)
        
        # Simulate tool completion
        output = "search results"
        self.callback.on_tool_end(output, run_id)
        
        # Verify span was finished and removed
        self.assertNotIn(run_id, self.callback._spans)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_tool_start_error_workflow(self):
        """Test the tool start -> error workflow."""
        # Simulate a tool start
        serialized = {"name": "api_tool"}
        input_str = "api request"
        run_id = "run_456"
        
        # Start the tool
        self.callback.on_tool_start(serialized, input_str, run_id)
        
        # Verify span was created
        self.assertIn(run_id, self.callback._spans)
        
        # Simulate tool error
        error = Exception("API timeout")
        self.callback.on_tool_error(error, run_id)
        
        # Verify span was finished and removed
        self.assertNotIn(run_id, self.callback._spans)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_multiple_tools_concurrent(self):
        """Test multiple tools running concurrently."""
        # Start multiple tools
        tools = [
            ("search_tool", "search query 1", "run_1"),
            ("api_tool", "api request 1", "run_2"),
            ("calculator_tool", "calculate 2+2", "run_3")
        ]
        
        # Start all tools
        for tool_name, input_str, run_id in tools:
            serialized = {"name": tool_name}
            self.callback.on_tool_start(serialized, input_str, run_id)
            self.assertIn(run_id, self.callback._spans)
        
        # Finish tools in different order
        self.callback.on_tool_end("search results", "run_1")
        self.callback.on_tool_error(Exception("API error"), "run_2")
        self.callback.on_tool_end("4", "run_3")
        
        # Verify all spans were finished
        self.assertEqual(len(self.callback._spans), 0)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_tool_with_unknown_name(self):
        """Test tool handling when name is not provided."""
        # Simulate a tool without a name
        serialized = {}  # No name field
        input_str = "some input"
        run_id = "run_unknown"
        
        # Start the tool
        self.callback.on_tool_start(serialized, input_str, run_id)
        
        # Should still create a span with default name
        self.assertIn(run_id, self.callback._spans)
        handle = self.callback._spans[run_id]
        self.assertIsInstance(handle, ToolEventSpanHandle)
        
        # Finish the tool
        self.callback.on_tool_end("some output", run_id)
        self.assertNotIn(run_id, self.callback._spans)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_missing_run_id_handling(self):
        """Test handling of missing run_id in finish events."""
        # Try to finish a tool that was never started
        self.callback.on_tool_end("output", "nonexistent_run_id")
        
        # Should not crash and should not have any spans
        self.assertEqual(len(self.callback._spans), 0)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_large_input_output_handling(self):
        """Test handling of large inputs and outputs in LangChain context."""
        # Create large input and output
        large_input = "x" * 500  # 500 characters
        large_output = "y" * 500  # 500 characters
        
        serialized = {"name": "large_data_tool"}
        run_id = "run_large"
        
        # Start tool with large input
        self.callback.on_tool_start(serialized, large_input, run_id)
        self.assertIn(run_id, self.callback._spans)
        
        # Finish tool with large output
        self.callback.on_tool_end(large_output, run_id)
        self.assertNotIn(run_id, self.callback._spans)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_conversation_context_in_langchain(self):
        """Test that conversation context is preserved in LangChain workflow."""
        from opentelemetry import baggage, context
        
        # Set conversation context
        ctx = baggage.set_baggage("conv_id", "langchain-conv-123")
        ctx = baggage.set_baggage("simulation_id", "langchain-sim-456")
        ctx = baggage.set_baggage("janus_simulation", "true")
        
        # Attach the context
        token = context.attach(ctx)
        
        try:
            # Start a tool - should pick up the context
            serialized = {"name": "context_test_tool"}
            input_str = "test input"
            run_id = "run_context"
            
            self.callback.on_tool_start(serialized, input_str, run_id)
            self.assertIn(run_id, self.callback._spans)
            
            # Finish the tool
            self.callback.on_tool_end("test output", run_id)
            self.assertNotIn(run_id, self.callback._spans)
            
        finally:
            # Always detach context
            context.detach(token)

    def test_tracing_disabled_in_langchain(self):
        """Test that LangChain integration works when tracing is disabled."""
        with patch('janus_sdk._HAS_OTEL', False):
            # Create a new callback with tracing disabled
            callback = MockLangChainCallback()
            
            # All operations should work without error
            serialized = {"name": "disabled_tool"}
            input_str = "test input"
            run_id = "run_disabled"
            
            # Start tool
            callback.on_tool_start(serialized, input_str, run_id)
            # Should not create any spans
            self.assertEqual(len(callback._spans), 0)
            
            # End tool
            callback.on_tool_end("test output", run_id)
            # Should not crash
            
            # Error tool
            callback.on_tool_error(Exception("test error"), run_id)
            # Should not crash

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_agent_action_with_record_tool_event(self):
        """Test using record_tool_event for agent actions."""
        # Simulate an agent action using the one-shot approach
        action = {
            "tool": "agent_action",
            "tool_input": "agent decision",
            "log": "Agent decided to take action"
        }
        
        # Use record_tool_event for one-shot agent actions
        result = record_tool_event(
            tool_name="agent_action",
            tool_input=action["tool_input"],
            tool_output=action["log"]
        )
        
        # Should complete without error
        self.assertIsNone(result)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_llm_start_with_record_tool_event(self):
        """Test using record_tool_event for LLM calls."""
        # Simulate an LLM call using the one-shot approach
        serialized = {"name": "gpt-4"}
        prompts = ["What is 2+2?"]
        
        # Use record_tool_event for LLM calls
        result = record_tool_event(
            tool_name="llm_call",
            tool_input=prompts[0],
            tool_output="The answer is 4."
        )
        
        # Should complete without error
        self.assertIsNone(result)

    @patch('janus_sdk._HAS_OTEL', True)
    @patch('janus_sdk._TRACING_INITIALIZED', True)
    def test_mixed_workflow(self):
        """Test a mixed workflow with both start/finish and one-shot patterns."""
        # Start a tool with start/finish pattern
        serialized = {"name": "long_running_tool"}
        input_str = "long operation"
        run_id = "run_long"
        
        self.callback.on_tool_start(serialized, input_str, run_id)
        self.assertIn(run_id, self.callback._spans)
        
        # Use one-shot pattern for quick operations
        record_tool_event("quick_tool", "quick input", "quick output")
        
        # Finish the long-running tool
        self.callback.on_tool_end("long operation result", run_id)
        self.assertNotIn(run_id, self.callback._spans)
        
        # Use one-shot pattern again
        record_tool_event("another_quick_tool", "another input", "another output")


if __name__ == '__main__':
    unittest.main() 