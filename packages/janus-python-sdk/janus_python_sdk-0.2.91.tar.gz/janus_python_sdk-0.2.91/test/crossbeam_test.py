import asyncio
import os
from typing import Dict, Any, Type, List

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Import our Janus SDK functions
import janus_sdk as janus
from janus_sdk import ToolEventSpanHandle

# Load environment variables from .env file
load_dotenv()

# --- 1. Define a Simple Tool for the Agent ---
# This simulates an external tool that LangChain can call.

class WeatherInput(BaseModel):
    location: str = Field(description="The city and state, e.g., San Francisco, CA")

def search_weather(location: str) -> str:
    """A mock tool that looks up the weather for a given location."""
    print(f"--- TOOL CALLED: search_weather(location='{location}') ---")
    if "chicago" in location.lower():
        return "It's 75 degrees and sunny in Chicago."
    return f"The weather in {location} is nice."

class WeatherTool(BaseTool):
    name: str = "search_weather"                # Added : str
    description: str = "useful for when you need to answer questions about the weather" # Added : str
    args_schema: Type[BaseModel] = WeatherInput
    
    def _run(self, location: str):
        return search_weather(location)
    
    async def _arun(self, location: str):
        return search_weather(location)
# --- 2. Create the Custom LangChain Callback ---
# This is the core of the integration. It listens for LangChain events
# and calls our new manual tracing functions.

class JanusLangChainCallback(BaseCallbackHandler):
    """A LangChain callback that uses Janus to trace tool events."""
    
    def __init__(self):
        # A dictionary to hold the span handle for each tool call,
        # identified by LangChain's unique 'run_id'.
        self._span_handles: Dict[str, ToolEventSpanHandle] = {}
        print("DEBUG: JanusLangChainCallback initialized")
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], run_id: str, **kwargs) -> None:
        """Called when a chain starts - this should always fire."""
        print(f"DEBUG: on_chain_start called with run_id '{run_id}'")
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], run_id: str, **kwargs) -> None:
        """Called when LLM starts."""
        print(f"DEBUG: on_llm_start called with run_id '{run_id}'")
    
    def on_llm_end(self, response, run_id: str, **kwargs) -> None:
        """Called when LLM ends."""
        print(f"DEBUG: on_llm_end called with run_id '{run_id}'")
    
    def on_agent_action(self, action, run_id: str, **kwargs) -> None:
        """Called when agent takes an action."""
        print(f"DEBUG: on_agent_action called with run_id '{run_id}', action: {action}")
        
        # Extract tool information from the action
        if hasattr(action, 'tool') and hasattr(action, 'tool_input'):
            tool_name = action.tool
            tool_input = str(action.tool_input)
            print(f"AGENT_ACTION: Tool '{tool_name}' with input '{tool_input}'")
            
            # Start the trace using our SDK
            handle = janus.start_tool_event(tool_name, tool_input)
            print("TRACE ENABLED?", handle is not None)
            if handle:
                self._span_handles[run_id] = handle
    
    def on_agent_finish(self, finish, run_id: str, **kwargs) -> None:
        """Called when agent finishes."""
        print(f"DEBUG: on_agent_finish called with run_id '{run_id}'")
        
        # Check if we have a span handle for this run_id
        if run_id in self._span_handles:
            handle = self._span_handles.pop(run_id)
            # Get the output from the finish object
            output = str(finish.return_values.get('output', '')) if hasattr(finish, 'return_values') else ''
            print(f"AGENT_FINISH: Finishing trace with output: {output[:50]}...")
            janus.finish_tool_event(handle, output)

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, run_id: str, **kwargs) -> None:
        """Called by LangChain right before a tool starts."""
        tool_name = serialized.get("name", "unknown_tool")
        print(f"CALLBACK: on_tool_start for '{tool_name}' with run_id '{run_id}'")
        print(f"CALLBACK: serialized = {serialized}")
        print(f"CALLBACK: input_str = {input_str}")
        
        # Call our new function to start the trace
        handle = janus.start_tool_event(tool_name, input_str)
        print("TRACE ENABLED?", handle is not None)
        if handle:
            self._span_handles[run_id] = handle

    def on_tool_end(self, output: str, run_id: str, **kwargs) -> None:
        """Called by LangChain right after a tool finishes."""
        print(f"CALLBACK: on_tool_end for a tool")
        
        if run_id in self._span_handles:
            handle = self._span_handles.pop(run_id)
            # Call our new function to finish the trace
            janus.finish_tool_event(handle, output)

    def on_tool_error(self, error: BaseException, run_id: str, **kwargs) -> None:
        """Called by LangChain if a tool throws an error."""
        print(f"CALLBACK: on_tool_error for a tool")
        
        if run_id in self._span_handles:
            handle = self._span_handles.pop(run_id)
            # Call our new function to finish the trace, recording the error
            janus.finish_tool_event(handle, error=error)


# --- 3. Create the LangChain Agent ---
# This function sets up the agent and wires in our custom callback.

def create_langchain_agent():
    """Creates a LangChain agent equipped with our tool and callback."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [WeatherTool()]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    # Create the agent executor and, most importantly, pass in our callback
    janus_callback = JanusLangChainCallback()
    print(f"DEBUG: Created callback: {janus_callback}")
    
    # Create the executor with explicit callback configuration
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        callbacks=[janus_callback],
        verbose=True,
        handle_parsing_errors=True
    )
    
    # Also set callbacks on the LLM to ensure they're propagated
    llm.callbacks = [janus_callback]
    
    return agent_executor


# --- 4. Define the Main Execution Logic ---
# This is the entry point that will be called by janus.run_simulations.

def agent_factory():
    """A factory function that Janus can call to get a fresh agent instance."""
    agent_executor = create_langchain_agent()
    
    # run_simulations expects an awaitable function that takes a string prompt
    # and returns a string answer.
    async def agent_runner(prompt: str) -> str:
        response = await agent_executor.ainvoke({"input": prompt})
        return response["output"]
        
    return agent_runner


async def main():
    """Main function to configure and run the Janus simulation."""
    print("--- Starting Janus Simulation with LangChain Agent ---")
    
    # Import trace for flushing
    from opentelemetry import trace
    
    # Get the tracer provider to force a flush later
    tracer_provider = trace.get_tracer_provider()
    
    try:
        await janus.run_simulations(
            num_simulations=1,
            max_turns=2,
            target_agent=agent_factory,
            api_key=os.getenv("JANUS_API_KEY"),
                context="The user is asking 'What is the weather like in Chicago?'"
            )
    finally:
        # Force the tracer to send all buffered spans before the script exits
        print("--- Forcing trace flush ---")
        try:
            # Try to flush if the provider supports it
            if hasattr(tracer_provider, 'force_flush'):
                tracer_provider.force_flush()
            else:
                print("--- Tracer provider doesn't support force_flush, waiting 2 seconds ---")
                import time
                time.sleep(2)  # Give time for spans to be sent
        except Exception as e:
            print(f"--- Flush error (non-critical): {e} ---")
    print("--- Simulation Complete ---")


if __name__ == "__main__":
    asyncio.run(main())