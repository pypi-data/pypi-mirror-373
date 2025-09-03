"""
Event handlers for team streaming operations.
"""

import logging
from typing import Dict, Any, AsyncGenerator, Optional
from openai.types.responses import (
    ResponseTextDeltaEvent, ResponseTextDoneEvent, ResponseCompletedEvent,
    ResponseOutputItemAddedEvent, ResponseOutputItemDoneEvent, ResponseOutputMessage,
    ResponseFunctionCallArgumentsDoneEvent, ResponseFunctionWebSearch
)
from agents import ItemHelpers


class StreamEventHandler:
    """Base class for handling stream events from OpenAI Agents SDK."""
    
    def __init__(self, current_agent: str):
        self.current_agent = current_agent
        self.logger = logging.getLogger(__name__)
    
    async def handle_event(self, event) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle a stream event and yield appropriate responses."""
        # Handle different event types based on the example pattern
        if event.type == "raw_response_event":
            async for response in self._handle_raw_response_event(event):
                yield response
        elif event.type == "agent_updated_stream_event":
            async for response in self._handle_agent_updated_event(event):
                yield response
        elif event.type == "run_item_stream_event":
            async for response in self._handle_run_item_event(event):
                yield response
        elif event.type == "message_output_event":
            async for response in self._handle_message_output_event(event):
                yield response
        elif isinstance(event, ResponseFunctionCallArgumentsDoneEvent):
            async for response in self._handle_function_call_args_done_event(event):
                yield response
        else:
            async for response in self._handle_unknown_event(event):
                yield response
    
    async def _handle_raw_response_event(self, event) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle raw response events with text delta data."""
        if hasattr(event, 'data') and event.data is not None:
            if isinstance(event.data, ResponseOutputItemDoneEvent):
                item = event.data
                if isinstance(item, ResponseFunctionWebSearch):
                    yield {
                        "id": item.id,
                        "type": "tool_call",
                        "status": "completed",
                        "call_id": getattr(event.item, 'id', f"tool_call_{self.current_agent}"),
                        "tool_name": 'web_search',
                        "tool_item": str(event.item.raw_item),
                        "tool_input": {"query": item.action.query},
                        "agent_name": self.current_agent,
                        "item_data": str(event.item),
                        "arguments": {"query": item.action.query},
                    }

                    return

            if isinstance(event.data, ResponseTextDeltaEvent):
                # Yield response in gnosari_agent format
                yield {
                    "id": f"response_{self.current_agent}",
                    "type": "response",
                    "content": event.data.delta,
                    "agent_name": self.current_agent
                }
    
    async def _handle_agent_updated_event(self, event) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle agent updated events."""
        if hasattr(event, 'new_agent') and event.new_agent:
            self.logger.info(f"Agent {event.new_agent.name} updated.")
            self.current_agent = event.new_agent.name
            yield {
                "type": "agent_updated",
                "agent_name": event.new_agent.name,
                "message": f"Agent updated: {event.new_agent.name}"
            }
    
    async def _handle_run_item_event(self, event) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle run item events (tool calls, outputs, etc.)."""
        if hasattr(event, 'item') and event.item:
            if event.item.type == "tool_call_item":
                raw_item = event.item.raw_item
                if isinstance(raw_item, ResponseFunctionWebSearch):
                    yield {
                        "id": getattr(event.item, 'id', f"tool_call_{self.current_agent}"),
                        "type": "tool_call",
                        "status": "completed",
                        "call_id": getattr(event.item, 'id', f"tool_call_{self.current_agent}"),
                        "tool_name": 'web_search',
                        "tool_item": str(event.item.raw_item),
                        "tool_input": getattr(event.item, 'arguments', {}),
                        "agent_name": self.current_agent,
                        "item_data": str(event.item),
                        "arguments": {} # dont know yet how to get the search item
                    }

                    return
                yield {
                    "id": getattr(event.item, 'id', f"tool_call_{self.current_agent}"),
                    "type": "tool_call",
                    "status": "completed",
                    "call_id": getattr(event.item, 'id', f"tool_call_{self.current_agent}"),
                    "tool_name": getattr(event.item.raw_item, 'name', 'unknown_tool'),
                    "tool_item": str(event.item.raw_item),
                    "tool_input": getattr(event.item, 'arguments', {}),
                    "agent_name": self.current_agent,
                    "item_data": str(event.item),
                    "arguments": getattr(event.item.raw_item, 'arguments', {})
                }
            elif event.item.type == "tool_call_output_item":
                # Tool output - yield tool result
                yield {
                    "type": "tool_result",
                    "content": getattr(event.item, 'output', ''),
                    "agent_name": self.current_agent
                }
            elif event.item.type == "message_output_item":
                # Message output - yield response
                content = getattr(event.item, 'content', '')
                if content:
                    yield {
                        "type": "response",
                        "content": content,
                        "agent_name": self.current_agent
                    }
            else:
                # Other item types - debug output
                yield {
                    "type_raw": str(event.item),
                    "type": str(event.item.type),
                }
    
    async def _handle_message_output_event(self, event) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle message output events."""
        yield {
            "type": "message_output",
            "agent_name": self.current_agent,
            "content": ItemHelpers.text_message_output(event.item),
            "item": str(event.item)
        }
    
    async def _handle_function_call_args_done_event(self, event) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle function call arguments done events."""
        yield {
            "type": "tool_call_arguments_done",
            "arguments": event.arguments,
            "item_id": event.item_id
        }
    
    async def _handle_unknown_event(self, event) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle unknown or unsupported event types."""
        # Check if event has data attribute before processing
        if not hasattr(event, 'data') or event.data is None:
            # Event without data - just yield basic event info
            yield {
                "type": "event_without_data",
                "event_type": event.type,
                "agent_name": self.current_agent,
                "message": "Event received but no data available",
                "data": str(event)
            }
        else:
            # Unknown event type
            yield {
                "type": "unknown",
                "event_type": event.type,
                "agent_name": self.current_agent,
                "data": str(event)
            }


class ErrorHandler:
    """Simplified error handler for team operations."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle error and return structured error response."""
        # Log the error with context
        self.logger.error(f"Error in streaming for {self.agent_name}: {error}")
        self.logger.error(f"Error type: {type(error).__name__}")
        
        return {
            "type": "error",
            "content": f"Error in streaming: {str(error)}",
            "error_type": type(error).__name__,
            "agent_name": self.agent_name
        }


class MCPServerManager:
    """Simplified MCP server connection management."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def connect_servers(self, agents: list):
        """Connect to all MCP servers across agents."""
        for agent in agents:
            if hasattr(agent, 'mcp_servers') and agent.mcp_servers:
                self.logger.info(f"Connecting MCP servers for agent: {agent.name}")
                await self._connect_agent_servers(agent)
    
    async def cleanup_servers(self, agents: list):
        """Clean up all MCP server connections across agents."""
        for agent in agents:
            if hasattr(agent, 'mcp_servers') and agent.mcp_servers:
                self.logger.info(f"Cleaning up MCP servers for agent: {agent.name}")
                await self._cleanup_agent_servers(agent)
    
    async def _connect_agent_servers(self, agent):
        """Connect MCP servers for a specific agent."""
        for server in agent.mcp_servers:
            try:
                if hasattr(server, 'connect') and not hasattr(server, '_connected'):
                    import asyncio
                    try:
                        await asyncio.wait_for(server.connect(), timeout=10.0)
                        server._connected = True
                        self.logger.debug(f"Connected to MCP server: {server.name}")
                    except asyncio.TimeoutError:
                        self.logger.warning(f"Timeout connecting to MCP server: {server.name}")
                    except asyncio.CancelledError:
                        self.logger.warning(f"Connection cancelled for MCP server: {server.name}")
                        break
            except Exception as e:
                self.logger.warning(f"Failed to connect to MCP server {server.name}: {e}")
    
    async def _cleanup_agent_servers(self, agent):
        """Clean up MCP servers for a specific agent."""
        for server in agent.mcp_servers:
            try:
                if hasattr(server, 'cleanup') and hasattr(server, '_connected'):
                    import asyncio
                    try:
                        await asyncio.wait_for(server.cleanup(), timeout=5.0)
                        delattr(server, '_connected')
                        self.logger.debug(f"Cleaned up MCP server: {server.name}")
                    except asyncio.TimeoutError:
                        self.logger.warning(f"Timeout cleaning up MCP server: {server.name}")
                    except asyncio.CancelledError:
                        self.logger.warning(f"Cleanup cancelled for MCP server: {server.name}")
                        break
            except Exception as e:
                self.logger.warning(f"Error cleaning up MCP server {server.name}: {e}")