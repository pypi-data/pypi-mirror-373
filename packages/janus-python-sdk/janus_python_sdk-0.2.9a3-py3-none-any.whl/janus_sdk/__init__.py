"""
Janus SDK - AI Agent Testing and Simulation Framework

This SDK provides tools for testing AI agents through automated conversations,
function call tracing, and rule-based evaluation.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
from dataclasses import dataclass
import logging
import os
import threading
import time
import uuid
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Tuple
from datetime import datetime
import tiktoken

import httpx
from httpx import AsyncHTTPTransport, Timeout
import json

# OpenTelemetry imports for tracing
try:
    from opentelemetry import baggage, trace
    from opentelemetry import context as otel_context
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    _HAS_OTEL = True
except ImportError:
    _HAS_OTEL = False

# Rich imports for progress display
try:
    from rich.console import Console, Group
    from rich.live import Live
    from rich.progress import Progress, BarColumn, TimeElapsedColumn, TimeRemainingColumn
    _HAS_RICH = True
    _console = Console()
except ImportError:
    _HAS_RICH = False
    _console = None

__all__ = ["run_simulations", "track", "record_tool_event", "start_tool_event", "finish_tool_event", "ToolEventSpanHandle"]

@dataclass
class ToolEventSpanHandle:
    """Handle for managing manual tool event spans.
    
    This dataclass stores the span reference and start time for manual tracing
    operations that span multiple function calls.
    """
    span: Any  # OpenTelemetry Span object
    start_time: float  # Start time from time.perf_counter()

# Configuration
_log = logging.getLogger(__name__)
_DEFAULT_BASE_URL = "https://api.withjanus.com"
_DEFAULT_CONTEXT = "You are testing an AI agent in a conversational scenario."
_DEFAULT_GOAL = "Evaluate the agent's performance through natural conversation."
_DEFAULT_JUDGE_MODEL = os.getenv("JANUS_JUDGE_MODEL", "openai/gpt-4.1-mini")
MAX_PARALLEL_SIMS = int(os.getenv("JANUS_MAX_PARALLEL_SIMS", "20"))

# Global tracing state
_TRACING_INITIALIZED = False
_TRACES_ENDPOINT: Optional[str] = None

_TOKEN_ENCODER = tiktoken.get_encoding("cl100k_base")

def _count_tokens(text):
    try:
        return len(_TOKEN_ENCODER.encode(text or ""))
    except Exception:
        return 0

def init_tracing(base_url: str, api_key: str) -> None:
    """Initialize OpenTelemetry tracing for the Janus SDK.
    
    Args:
        base_url: Base URL of your Janus backend (e.g., "http://localhost:8000")
        api_key: Your Janus API key
    """
    global _TRACING_INITIALIZED, _TRACES_ENDPOINT
    
    if not _HAS_OTEL:
        _log.warning("OpenTelemetry not available - tracing disabled")
        return
    
    _TRACES_ENDPOINT = f"{base_url.rstrip('/')}/traces"
    
    # Set up OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=_TRACES_ENDPOINT,
        headers={"Authorization": f"Bearer {api_key}"}
    )
    
    # Get or create tracer provider
    tracer_provider = trace.get_tracer_provider()
    if tracer_provider.__class__.__name__ == 'ProxyTracerProvider':
        real_tracer_provider = TracerProvider()
        trace.set_tracer_provider(real_tracer_provider)
        tracer_provider = real_tracer_provider
    
    tracer_provider.add_span_processor(SimpleSpanProcessor(otlp_exporter))
    
    _TRACING_INITIALIZED = True
    _log.info(f"Janus tracing initialized - endpoint: {_TRACES_ENDPOINT}")


def track(func: Callable) -> Callable:
    """Decorator that automatically traces function calls with conversation context.
    
    Usage:
        @track
        def my_function(x, y):
            return x + y
    
    The decorator automatically:
    - Creates spans with conversation context
    - Captures function inputs/outputs
    - Measures execution time
    - Links to parent traces
    """
    
    # Check if the function is async
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not _HAS_OTEL or not _TRACING_INITIALIZED:
                return await func(*args, **kwargs)
            
            tracer = trace.get_tracer(__name__)
            span_name = f"{func.__name__}_operation"
            
            # Get parent span BEFORE creating new span
            parent_span = trace.get_current_span()
            parent_trace_id = None
            if parent_span and parent_span.is_recording():
                parent_trace_id = parent_span.get_span_context().trace_id
            
            with tracer.start_as_current_span(span_name) as span:
                start_time = time.perf_counter()
                
                # Set basic function attributes
                span.set_attribute("function.name", func.__name__)
                
                # Get conversation context from baggage
                conv_id = baggage.get_baggage("conv_id")
                simulation_id = baggage.get_baggage("simulation_id")
                is_simulation = baggage.get_baggage("janus_simulation") == "true"
                
                if conv_id:
                    span.set_attribute("conversation.id", conv_id)
                    span.set_attribute("janus.conversation_id", conv_id)
                
                if is_simulation:
                    span.set_attribute("janus.simulation", True)
                
                if simulation_id:
                    span.set_attribute("janus.simulation_id", simulation_id)
                
                # Link to parent trace using the saved parent_trace_id
                if parent_trace_id:
                    span.set_attribute("trace.id", f"{parent_trace_id:032x}")
                    span.set_attribute("trace.correlation", True)
                
                # Capture function arguments
                _capture_function_inputs(span, func, args, kwargs)
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Record success metrics
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    span.set_attribute("function.duration_ms", round(duration_ms, 3))
                    span.set_attribute("function.success", True)
                    
                    # Capture output
                    _capture_function_output(span, result)
                    
                    return result
                    
                except Exception as e:
                    # Record failure metrics
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    span.set_attribute("function.duration_ms", round(duration_ms, 3))
                    span.set_attribute("function.success", False)
                    span.set_attribute("function.error", str(e))
                    span.set_attribute("function.error_type", type(e).__name__)
                    raise
        
        return async_wrapper
    
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not _HAS_OTEL or not _TRACING_INITIALIZED:
                return func(*args, **kwargs)
            
            tracer = trace.get_tracer(__name__)
            span_name = f"{func.__name__}_operation"
            
            # Get parent span BEFORE creating new span
            parent_span = trace.get_current_span()
            parent_trace_id = None
            if parent_span and parent_span.is_recording():
                parent_trace_id = parent_span.get_span_context().trace_id
            
            with tracer.start_as_current_span(span_name) as span:
                start_time = time.perf_counter()
                
                # Set basic function attributes
                span.set_attribute("function.name", func.__name__)
                
                # Get conversation context from baggage
                conv_id = baggage.get_baggage("conv_id")
                simulation_id = baggage.get_baggage("simulation_id")
                is_simulation = baggage.get_baggage("janus_simulation") == "true"
                
                if conv_id:
                    span.set_attribute("conversation.id", conv_id)
                    span.set_attribute("janus.conversation_id", conv_id)
                
                if is_simulation:
                    span.set_attribute("janus.simulation", True)
                
                if simulation_id:
                    span.set_attribute("janus.simulation_id", simulation_id)
                
                # Link to parent trace using the saved parent_trace_id
                if parent_trace_id:
                    span.set_attribute("trace.id", f"{parent_trace_id:032x}")
                    span.set_attribute("trace.correlation", True)
                
                # Capture function arguments
                _capture_function_inputs(span, func, args, kwargs)
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Record success metrics
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    span.set_attribute("function.duration_ms", round(duration_ms, 3))
                    span.set_attribute("function.success", True)
                    
                    # Capture output
                    _capture_function_output(span, result)
                    
                    return result
                    
                except Exception as e:
                    # Record failure metrics
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    span.set_attribute("function.duration_ms", round(duration_ms, 3))
                    span.set_attribute("function.success", False)
                    span.set_attribute("function.error", str(e))
                    span.set_attribute("function.error_type", type(e).__name__)
                    raise
        
        return sync_wrapper


def _capture_function_inputs(span, func: Callable, args: tuple, kwargs: dict) -> None:
    """Capture function input parameters as span attributes."""
    try:
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        for param_name, param_value in bound_args.arguments.items():
            if isinstance(param_value, (int, float, bool)):
                span.set_attribute(f"function.input.{param_name}", param_value)
            else:
                str_value = str(param_value)
                truncated = str_value[:100] + "..." if len(str_value) > 100 else str_value
                span.set_attribute(f"function.input.{param_name}", truncated)
    except Exception:
        # Don't fail if we can't capture arguments
        pass


def _capture_function_output(span, result: Any) -> None:
    """Capture function output as span attributes."""
    if isinstance(result, (int, float, bool)):
        span.set_attribute("function.output", result)
    elif result is not None:
        str_result = str(result)
        truncated = str_result[:100] + "..." if len(str_result) > 100 else str_result
        span.set_attribute("function.output", truncated)


def record_tool_event(
    tool_name: str,
    tool_input: Any = None,
    tool_output: Any = None,
    success: Optional[bool] = None,
    duration_ms: Optional[float] = None,
    error: Optional[Union[str, Exception]] = None
) -> None:
    """Record a tool event as a single span.
    
    This function creates and immediately finishes a span for a tool event,
    capturing all relevant information in one call.
    
    Args:
        tool_name: Name of the tool being traced
        tool_input: Input data passed to the tool (will be truncated if too long)
        tool_output: Output data returned by the tool (will be truncated if too long)
        success: Whether the tool execution was successful (auto-computed from error if not provided)
        duration_ms: Duration of the tool execution in milliseconds (auto-computed if not provided)
        error: Error that occurred during tool execution (string or Exception)
    
    Examples:
        # Basic usage
        record_tool_event("search_api", "query: weather in NYC", "temperature: 72°F")
        
        # With error handling
        try:
            result = call_external_api()
            record_tool_event("api_call", "request", result)
        except Exception as e:
            record_tool_event("api_call", "request", error=e)
        
        # With custom duration
        start_time = time.perf_counter()
        result = process_data()
        duration = (time.perf_counter() - start_time) * 1000
        record_tool_event("data_processing", "input_data", result, duration_ms=duration)
    """
    if not _HAS_OTEL or not _TRACING_INITIALIZED:
        return
    
    try:
        tracer = trace.get_tracer(__name__)
        span_name = f"{tool_name}_operation"
        
        # Get parent span BEFORE creating new span
        parent_span = trace.get_current_span()
        parent_trace_id = None
        if parent_span and parent_span.is_recording():
            parent_trace_id = parent_span.get_span_context().trace_id
        
        with tracer.start_as_current_span(span_name) as span:
            start_time = time.perf_counter()
            
            # Set basic function attributes
            span.set_attribute("function.name", tool_name)
            
            # Get conversation context from baggage
            conv_id = baggage.get_baggage("conv_id")
            simulation_id = baggage.get_baggage("simulation_id")
            is_simulation = baggage.get_baggage("janus_simulation") == "true"
            
            if conv_id:
                span.set_attribute("conversation.id", conv_id)
                span.set_attribute("janus.conversation_id", conv_id)
            
            if is_simulation:
                span.set_attribute("janus.simulation", True)
            
            if simulation_id:
                span.set_attribute("janus.simulation_id", simulation_id)
            
            # Link to parent trace using the saved parent_trace_id
            if parent_trace_id:
                span.set_attribute("trace.id", f"{parent_trace_id:032x}")
                span.set_attribute("trace.correlation", True)
            
            # Set tool input
            if tool_input is not None:
                if isinstance(tool_input, (int, float, bool)):
                    span.set_attribute("function.input", tool_input)
                else:
                    str_input = str(tool_input)
                    truncated = str_input[:100] + "..." if len(str_input) > 100 else str_input
                    span.set_attribute("function.input", truncated)
            
            # Set tool output
            if tool_output is not None:
                if isinstance(tool_output, (int, float, bool)):
                    span.set_attribute("function.output", tool_output)
                else:
                    str_output = str(tool_output)
                    truncated = str_output[:100] + "..." if len(str_output) > 100 else str_output
                    span.set_attribute("function.output", truncated)
            
            # Compute or use provided duration
            if duration_ms is None:
                duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Compute success if not provided
            if success is None:
                success = error is None
            
            # Set outcome attributes
            span.set_attribute("function.duration_ms", round(duration_ms, 3))
            span.set_attribute("function.success", success)
            
            if error is not None:
                span.set_attribute("function.error", str(error))
                span.set_attribute("function.error_type", type(error).__name__ if isinstance(error, Exception) else "str")
    
    except Exception as e:
        # Don't let tracing errors break the application
        _log.warning(f"Failed to record tool event for {tool_name}: {e}")


def start_tool_event(
    tool_name: str,
    tool_input: Any = None
) -> Optional[ToolEventSpanHandle]:
    """Start a tool event span and return a handle for later completion.
    
    This function creates a span for a tool event that will be completed later
    with finish_tool_event(). This is useful for tracing operations that span
    multiple function calls or async operations.
    
    Args:
        tool_name: Name of the tool being traced
        tool_input: Input data passed to the tool (will be truncated if too long)
    
    Returns:
        ToolEventSpanHandle containing the span and start time, or None if tracing is disabled
    
    Examples:
        # Basic usage
        handle = start_tool_event("database_query", "SELECT * FROM users")
        # ... do database work ...
        finish_tool_event(handle, "1000 rows returned")
        
        # With error handling
        handle = start_tool_event("external_api", "api_request")
        try:
            result = call_api()
            finish_tool_event(handle, result)
        except Exception as e:
            finish_tool_event(handle, error=e)
        
        # Check if tracing is enabled
        handle = start_tool_event("tool_name", "input")
        if handle is not None:
            # Tracing is enabled, proceed with work
            result = do_work()
            finish_tool_event(handle, result)
        else:
            # Tracing is disabled, just do work without tracing
            result = do_work()
    """
    if not _HAS_OTEL or not _TRACING_INITIALIZED:
        return None
    
    try:
        tracer = trace.get_tracer(__name__)
        span_name = f"{tool_name}_operation"
        
        # Get parent span BEFORE creating new span
        parent_span = trace.get_current_span()
        parent_trace_id = None
        if parent_span and parent_span.is_recording():
            parent_trace_id = parent_span.get_span_context().trace_id
        
        # Create span (not as current span to avoid interfering with existing context)
        span = tracer.start_span(span_name)
        start_time = time.perf_counter()
        
        # Set basic function attributes
        span.set_attribute("function.name", tool_name)
        
        # Get conversation context from baggage
        conv_id = baggage.get_baggage("conv_id")
        simulation_id = baggage.get_baggage("simulation_id")
        is_simulation = baggage.get_baggage("janus_simulation") == "true"
        turn_idx = baggage.get_baggage("turn_idx")
        
        if conv_id:
            span.set_attribute("conversation.id", conv_id)
            span.set_attribute("janus.conversation_id", conv_id)
        
        if is_simulation:
            span.set_attribute("janus.simulation", True)
        
        if simulation_id:
            span.set_attribute("janus.simulation_id", simulation_id)
        
        if turn_idx is not None:
            span.set_attribute("conversation.turn_idx", int(turn_idx))
            span.set_attribute("janus.turn_idx", int(turn_idx))
        
        # Link to parent trace using the saved parent_trace_id
        if parent_trace_id:
            span.set_attribute("trace.id", f"{parent_trace_id:032x}")
            span.set_attribute("trace.correlation", True)
        
        # Set tool input
        if tool_input is not None:
            if isinstance(tool_input, (int, float, bool)):
                span.set_attribute("function.input", tool_input)
            else:
                str_input = str(tool_input)
                truncated = str_input[:100] + "..." if len(str_input) > 100 else str_input
                span.set_attribute("function.input", truncated)
        
        return ToolEventSpanHandle(span=span, start_time=start_time)
    
    except Exception as e:
        # Don't let tracing errors break the application
        _log.warning(f"Failed to start tool event for {tool_name}: {e}")
        return None


def finish_tool_event(
    handle: ToolEventSpanHandle,
    tool_output: Any = None,
    error: Optional[Union[str, Exception]] = None
) -> None:
    """Finish a tool event span started with start_tool_event().
    
    This function completes a span for a tool event, setting the final attributes
    and ending the span. It should be called after the tool execution completes.
    
    Args:
        handle: ToolEventSpanHandle returned from start_tool_event()
        tool_output: Output data returned by the tool (will be truncated if too long)
        error: Error that occurred during tool execution (string or Exception)
    
    Examples:
        # Successful completion
        handle = start_tool_event("data_processing", "input_data")
        result = process_data()
        finish_tool_event(handle, result)
        
        # Error completion
        handle = start_tool_event("api_call", "request")
        try:
            result = call_api()
            finish_tool_event(handle, result)
        except Exception as e:
            finish_tool_event(handle, error=e)
        
        # Safe handling of None handle (when tracing is disabled)
        handle = start_tool_event("tool_name", "input")
        finish_tool_event(handle, "output")  # Safe even if handle is None
    """
    if handle is None:
        return
    
    try:
        # Validate handle has required attributes
        if not hasattr(handle, 'span') or not hasattr(handle, 'start_time'):
            _log.warning("Invalid ToolEventSpanHandle provided to finish_tool_event")
            return
        
        span = handle.span
        start_time = handle.start_time
        
        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Set tool output
        if tool_output is not None:
            if isinstance(tool_output, (int, float, bool)):
                span.set_attribute("function.output", tool_output)
            else:
                str_output = str(tool_output)
                truncated = str_output[:100] + "..." if len(str_output) > 100 else str_output
                span.set_attribute("function.output", truncated)
        
        # Compute success
        success = error is None
        
        # Set outcome attributes
        span.set_attribute("function.duration_ms", round(duration_ms, 3))
        span.set_attribute("function.success", success)
        
        if error is not None:
            span.set_attribute("function.error", str(error))
            span.set_attribute("function.error_type", type(error).__name__ if isinstance(error, Exception) else "str")
        
        # End the span
        span.end()
    
    except Exception as e:
        # Don't let tracing errors break the application
        _log.warning(f"Failed to finish tool event: {e}")


def _create_context_aware_agent(
    original_agent_factory: Callable, 
    conv_id: str, 
    sim_idx: int, 
    simulation_id: str,
    persona_kwargs: Optional[Dict[str, str]] = None
) -> Callable:
    """Create an agent wrapper that injects conversation context into traces."""
    
    def enhanced_agent_factory():
        original_agent = original_agent_factory()
        
        async def context_injected_agent(prompt: str) -> str:
            if not _HAS_OTEL:
                return await _maybe_await(original_agent(prompt, **(persona_kwargs or {})))
            
            # Save current context
            previous_ctx = otel_context.get_current()
            
            # Set conversation context in baggage
            ctx = baggage.set_baggage("conv_id", conv_id, previous_ctx)
            ctx = baggage.set_baggage("janus_simulation", "true", ctx)
            ctx = baggage.set_baggage("simulation_id", simulation_id, ctx)
            ctx = baggage.set_baggage("simulation_idx", str(sim_idx), ctx)
            token = otel_context.attach(ctx)
            
            try:
                # Create parent span for agent interaction
                tracer = trace.get_tracer("janus_sdk")
                with tracer.start_as_current_span("janus_agent_interaction") as span:
                    # Set conversation attributes
                    span.set_attribute("conversation.id", conv_id)
                    span.set_attribute("janus.conversation_id", conv_id)
                    span.set_attribute("janus.simulation", True)
                    span.set_attribute("janus.simulation_id", simulation_id)
                    span.set_attribute("janus.simulation_idx", sim_idx)
                    
                    # Truncate prompt for span attribute
                    truncated_prompt = prompt[:200] + "..." if len(prompt) > 200 else prompt
                    span.set_attribute("agent.prompt", truncated_prompt)
                    
                    # Get turn context if available
                    turn_idx = baggage.get_baggage("turn_idx")
                    if turn_idx is not None:
                        span.set_attribute("conversation.turn_idx", int(turn_idx))
                        span.set_attribute("janus.turn_idx", int(turn_idx))
                    
                    # Execute agent
                    result = await _maybe_await(
        original_agent(prompt, **(persona_kwargs or {}))
    )
                    # Record response
                    truncated_response = result[:200] + "..." if len(result) > 200 else result
                    span.set_attribute("agent.response", truncated_response)
                    span.set_attribute("agent.success", True)
                    
                    return result
            finally:
                # Always detach context to prevent bleed
                otel_context.detach(token)
        
        return context_injected_agent
    
    return enhanced_agent_factory


class JanusClient:
    """Async HTTP client for the Janus API."""

    def __init__(self, base_url: str, api_key: str, *, _client: Optional[httpx.AsyncClient] = None):
        """Initialize the Janus client.
        
        Args:
            base_url: Base URL of the Janus backend
            api_key: API key for authentication
            _client: Optional pre-configured httpx client
        """
        self._base = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        if _client is None:
            self._client = httpx.AsyncClient(
                headers=self._headers,
                timeout=Timeout(3600)
            )
            self._owns_client = True
        else:
            self._client = _client
            self._owns_client = False

    async def start(self, context: str, goal: str, custom_profile: Optional[str] = None) -> Tuple[str, str]:
        """Start a new conversation.
        
        Args:
            context: Context for the conversation
            goal: Goal for the conversation
            custom_profile: Optional JSON string representing a custom user persona/profile
            
        Returns:
            Tuple of (conversation_id, first_question)
        """
        payload = {
            "context": context,
            "goal": goal,
        }
        if custom_profile is not None:
            payload["custom_profile"] = custom_profile

        resp = await self._client.post(f"{self._base}/conv", json=payload)
        
        if resp.status_code != 200:
            self._log_error("start", resp)
        
        resp.raise_for_status()
        data = resp.json()
        return data["conv_id"], data["question"]

    async def turn(self, conv_id: str, answer: str) -> str:
        """Send an answer and get the next question.
        
        Args:
            conv_id: Conversation ID
            answer: Answer to the previous question
            
        Returns:
            Next question
        """
        resp = await self._client.post(f"{self._base}/conv/{conv_id}", json={
            "answer": answer,
        })
        
        if resp.status_code != 200:
            self._log_error("turn", resp)
        
        resp.raise_for_status()
        data = resp.json()
        return data["question"]

    def _log_error(self, operation: str, resp: httpx.Response) -> None:
        """Log HTTP errors with structured information."""
        try:
            err_body = resp.json()
            err_code = err_body.get("error", {}).get("code") if isinstance(err_body, dict) else None
        except Exception:
            err_body = resp.text
            err_code = None
            
        _log.error(
            f"JanusClient.{operation} | HTTP {resp.status_code} | "
            f"API_Code: {err_code} | body: {err_body}"
        )

    async def close(self) -> None:
        """Close the HTTP client if we own it."""
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()


async def _maybe_await(value):
    """Await a value if it's awaitable, otherwise return it directly."""
    if asyncio.iscoroutine(value):
        return await value
    return value


async def arun_simulations(
    *,
    target_agent: Callable[[], Callable[[str], Awaitable[str] | str]],
    api_key: str,
    num_simulations: int = 10,
    max_turns: int = 10,
    base_url: Optional[str] = None,
    context: Optional[str] = None,
    goal: Optional[str] = None,
    rules: Optional[Sequence[str]] = None,
    # Internal parameters (hidden from main API)
    enabled_judges: Optional[Sequence[str]] = ("rule",),
    num_judges: int = 3,
    judge_model: str = _DEFAULT_JUDGE_MODEL,
    judge_kwargs: Optional[Dict[str, Any]] = None,
    auto_init_tracing: bool = True,
    persona_kwargs: Optional[Dict[str, str]] = None,
) -> List[dict]:
    """Run multiple AI agent simulations asynchronously.
    
    Args:
        target_agent: Factory function that creates agent instances
        api_key: Your Janus API key for authentication
        num_simulations: Number of simulations to run (default: 10)
        max_turns: Maximum turns per conversation (default: 10)
        base_url: Janus backend URL (default: Railway production URL)
        context: Context for conversations (default: generic testing context)
        goal: Goal for conversations (default: generic evaluation goal)
        rules: Rules for evaluation (optional)
        persona_kwargs: stringified-JSON kwargs passed to every agent turn and serialised to the backend as a custom profile (optional)
        
    Returns:
        List of simulation results
    """
    # Set defaults for optional parameters
    if base_url is None:
        base_url = _DEFAULT_BASE_URL
    if context is None:
        context = _DEFAULT_CONTEXT
    if goal is None:
        goal = _DEFAULT_GOAL
    # Initialize tracing if needed
    if auto_init_tracing and not _TRACING_INITIALIZED:
        init_tracing(base_url, api_key)
    
    # Generate simulation ID
    simulation_id = uuid.uuid4().hex
    _log.info(f"Starting simulation batch with ID: {simulation_id}")

    # Set up concurrency control
    sem = asyncio.Semaphore(MAX_PARALLEL_SIMS)
    
    # Shared client for judge calls
    shared_client = httpx.AsyncClient(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        limits=httpx.Limits(
            max_connections=MAX_PARALLEL_SIMS,
            max_keepalive_connections=MAX_PARALLEL_SIMS,
            keepalive_expiry=30.0,
        ),
        transport=AsyncHTTPTransport(retries=3),
        timeout=Timeout(3600),
    )

    progress_ctx: Optional[dict] = None      # ← initialise early
    try:
        progress_ctx = _setup_progress_tracking(num_simulations)
        
        async def _run_single_simulation(sim_idx: int) -> dict:
            """Run a single simulation with proper error handling and tracing."""
            async with sem:
                transport = AsyncHTTPTransport(retries=3)
                async with httpx.AsyncClient(
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    limits=httpx.Limits(
                        max_connections=5,
                        max_keepalive_connections=5,
                        keepalive_expiry=30.0,
                    ),
                    transport=transport,
                    timeout=Timeout(3600),
                ) as session:
                    client = JanusClient(base_url, api_key, _client=session)
                    
                    # Start conversation
                    custom_profile = json.dumps(persona_kwargs) if persona_kwargs else None
                    question_start_timestamp = datetime.utcnow()
                    question_start = time.perf_counter()
                    conv_id, question = await client.start(context, goal, custom_profile=custom_profile)
                    question_end = time.perf_counter()
                    question_end_timestamp = datetime.utcnow()
                    question_generation_time = question_end - question_start
                    
                    # Create context-aware agent
                    agent = _create_context_aware_agent(target_agent, conv_id, sim_idx, simulation_id, persona_kwargs)()
                    
                    qa_pairs = []
                    
                    # Run conversation turns
                    for turn_idx in range(max_turns):
                        answer_start_timestamp = datetime.utcnow()
                        answer_start = time.perf_counter()
                        answer = await _maybe_await(agent(question))
                        answer_end = time.perf_counter()
                        answer_end_timestamp = datetime.utcnow()
                        answer_generation_time = answer_end - answer_start
                        
                        # Track next question timing
                        next_question_start_timestamp = datetime.utcnow()
                        next_question_start = time.perf_counter()
                        next_question = await client.turn(conv_id, answer)
                        next_question_end = time.perf_counter()
                        next_question_end_timestamp = datetime.utcnow()
                        question_generation_time = next_question_end - next_question_start
                        
                        qa_pairs.append({
                            "idx": turn_idx,
                            "q": question,
                            "a": answer,
                            "agent_metrics": {
                                "question_start_timestamp": next_question_start_timestamp.isoformat(),
                                "question_end_timestamp": next_question_end_timestamp.isoformat(),
                                "answer_start_timestamp": answer_start_timestamp.isoformat(),
                                "answer_end_timestamp": answer_end_timestamp.isoformat(),
                                "question_generation_time": question_generation_time,
                                "answer_generation_time": answer_generation_time,
                                "question_tokens": _count_tokens(question),
                                "answer_tokens": _count_tokens(answer),
                            }
                        })
                        
                        question = next_question
                    
                    # Submit transcript with simulation_id
                    try:
                        await session.post(
                            f"{base_url.rstrip('/')}/conversation",
                            json={
                                "conv_id": conv_id, 
                                "transcript": qa_pairs,
                                "simulation_id": simulation_id
                            },
                        )
                    except Exception as e:
                        _log.warning(f"Failed to submit transcript for {conv_id}: {e}")
                    
                    # Update progress
                    _update_progress(progress_ctx)
                    
                    return {
                        "sim_id": sim_idx,
                        "simulation_id": simulation_id,
                        "conv_id": conv_id,
                        "qa": qa_pairs,
                    }
        
        # Run all simulations
        results = await asyncio.gather(*[
            _run_single_simulation(i) for i in range(num_simulations)
        ])
        
        # Run judges if enabled
        if enabled_judges:
            await _run_judges(
                results, base_url, shared_client, enabled_judges, 
                rules, num_judges, judge_model, judge_kwargs
            )
        
        return results
        
    finally:
        await shared_client.aclose()
        _cleanup_progress_tracking(progress_ctx)


def _setup_progress_tracking(num_simulations: int):
    """Set up Rich progress tracking if available."""
    # Rich's Live() may only run in the main thread / main TTY.
    if (not _HAS_RICH
            or threading.current_thread() is not threading.main_thread()):
        return None
        
    progress = Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.completed]{task.completed}/{task.total}",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=_console,
        transient=True,
    )
    
    task_id = progress.add_task("Running Simulations...", total=num_simulations)
    
    def render_display():
        return Group(progress)
    
    live_ctx = Live(render_display(), refresh_per_second=8, console=_console)
    live_ctx.__enter__()
    
    return {
        "progress": progress,
        "task_id": task_id,
        "live_ctx": live_ctx,
        "render_display": render_display
    }


def _update_progress(progress_ctx):
    """Update progress tracking."""
    if not progress_ctx:
        return
        
    progress_ctx["progress"].update(progress_ctx["task_id"], advance=1)
    progress_ctx["live_ctx"].update(progress_ctx["render_display"]())


def _cleanup_progress_tracking(progress_ctx):
    """Clean up progress tracking."""
    if progress_ctx and progress_ctx["live_ctx"]:
        progress_ctx["live_ctx"].__exit__(None, None, None)


async def _run_judges(
    results: List[dict],
    base_url: str, 
    client: httpx.AsyncClient,
    enabled_judges: Sequence[str],
    rules: Optional[Sequence[str]],
    num_judges: int,
    judge_model: str,
    judge_kwargs: Optional[Dict[str, Any]]
) -> None:
    """Run judge evaluations on simulation results."""
    
    # Group answers by question for hallucination detection
    answers_by_question: Dict[str, List[str]] = {}
    for sim in results:
        for qa in sim["qa"]:
            answers_by_question.setdefault(qa["q"], []).append(qa["a"])
    
    # Rule-based judging
    if "rule" in enabled_judges:
        rule_tasks = []
        for sim in results:
            for qa in sim["qa"]:
                task = _submit_rule_judgment(
                    client, base_url, qa["q"], qa["a"], sim["conv_id"],
                    rules, num_judges, judge_model, judge_kwargs
                )
                rule_tasks.append(task)
        
        if rule_tasks:
            await asyncio.gather(*rule_tasks, return_exceptions=True)
    
    # Hallucination detection
    if "hallucination" in enabled_judges:
        hallu_tasks = []
        hallu_targets = []
        
        for sim in results:
            for qa in sim["qa"]:
                peers = [a for a in answers_by_question.get(qa["q"], []) if a != qa["a"]]
                task = _get_hallucination_metrics(client, base_url, qa["a"], peers)
                hallu_tasks.append(task)
                hallu_targets.append(qa)
        
        if hallu_tasks:
            hallu_results = await asyncio.gather(*hallu_tasks)
            for qa_dict, result in zip(hallu_targets, hallu_results):
                qa_dict.setdefault("judgments", {})["hallucination"] = result


async def _submit_rule_judgment(
    client: httpx.AsyncClient,
    base_url: str,
    question: str,
    answer: str,
    conv_id: str,
    rules: Sequence[str],
    num_judges: int,
    judge_model: str,
    judge_kwargs: Optional[Dict[str, Any]]
) -> None:
    """Submit a rule-based judgment request."""
    payload = {
        "question": question,
        "answer": answer,
        "rules": list(rules) if rules else None,
        "num_judges": num_judges,
        "judge_model": judge_model,
        "judge_kwargs": judge_kwargs or {},
        "enabled_judges": ["rule"],
        "conv_id": conv_id,
    }
    
    try:
        await client.post(f"{base_url.rstrip('/')}/judge", json=payload)
    except Exception as e:
        _log.error(f"Rule judge submission failed: {e}")


async def _get_hallucination_metrics(
    client: httpx.AsyncClient,
    base_url: str,
    answer: str,
    peers: List[str]
) -> Dict[str, Any]:
    """Get hallucination metrics for an answer."""
    payload = {
        "answer": answer,
        "other_answers": peers,
    }
    
    try:
        resp = await client.post(f"{base_url.rstrip('/')}/hallucination", json=payload)
        resp.raise_for_status()
        return resp.json().get("scores", {})
    except Exception as e:
        _log.error(f"Hallucination metrics failed: {e}")
        return {}


def run_simulations(
    *,
    target_agent: Callable[[], Callable[[str], Awaitable[str] | str]],
    api_key: str,
    num_simulations: int,
    max_turns: int,
    base_url: Optional[str] = None,
    context: Optional[str] = None,
    goal: Optional[str] = None,
    rules: Optional[Sequence[str]] = None,
    persona_kwargs: Optional[Dict[str, str]] = None,
):
    """Run multiple AI agent simulations synchronously.
    
    This is a simplified API that uses sensible defaults for most parameters.
    
    Args:
        target_agent: Factory function that creates agent instances
        api_key: Your Janus API key for authentication
        num_simulations: Number of simulations to run (default: 10)
        max_turns: Maximum turns per conversation (default: 10)
        base_url: Janus backend URL (default: Railway production URL)
        context: Context for conversations (default: generic testing context)
        goal: Goal for conversations (default: generic evaluation goal)
        rules: Rules for evaluation (optional)
        persona_kwargs: stringified-JSON kwargs passed to every agent turn and serialised to the backend as a custom profile (optional)
        
    Returns:
        List of simulation results
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(
            arun_simulations(
                target_agent=target_agent,
                api_key=api_key,
                num_simulations=num_simulations,
                max_turns=max_turns,
                base_url=base_url,
                context=context,
                goal=goal,
                rules=rules,
                persona_kwargs=persona_kwargs,
            )
        )
    else:
        return loop.create_task(
            arun_simulations(
                target_agent=target_agent,
                api_key=api_key,
                num_simulations=num_simulations,
                max_turns=max_turns,
                base_url=base_url,
                context=context,
                goal=goal,
                rules=rules,
                persona_kwargs=persona_kwargs,
            )
        )
