"""
Team Runner - Uses OpenAI Agents SDK Runner to execute teams.
"""

import logging
import asyncio
from typing import Optional, AsyncGenerator, Dict, Any
from agents import Runner, RunConfig

from .team import Team
from .event_handlers import StreamEventHandler, ErrorHandler, MCPServerManager


class TeamRunner:
    """Team runner using OpenAI Agents SDK Runner."""
    
    def __init__(self, team: Team):
        self.team = team
        self.logger = logging.getLogger(__name__)
    
    async def run_team_async(self, message: str, debug: bool = False) -> Dict[str, Any]:
        """
        Run team asynchronously using OpenAI Agents SDK Runner.
        
        Args:
            message: User message
            debug: Whether to show debug info
            
        Returns:
            Dict with outputs and completion status
        """
        if debug:
            self.logger.info(f"Contacting {self.team.orchestrator.name}")
        
        # Initialize MCP manager and connect servers
        mcp_manager = MCPServerManager()
        all_agents = [self.team.orchestrator] + list(self.team.workers.values())
        await mcp_manager.connect_servers(all_agents)
        
        try:
            run_config = RunConfig(
                workflow_name=self.team.name or "Unknown Team",
            )

            result = await Runner.run(self.team.orchestrator, input=message, run_config=run_config)
            
            # Convert result to our expected format
            return {
                "outputs": [{"type": "completion", "content": result.final_output}],
                "agent_name": self.team.orchestrator.name,
                "is_done": True
            }
        finally:
            # Clean up MCP servers after running
            await mcp_manager.cleanup_servers(all_agents)
    
    def run_team(self, message: str, debug: bool = False) -> Dict[str, Any]:
        """Run team synchronously."""
        return asyncio.run(self.run_team_async(message, debug))
    
    async def run_team_stream(self, message: str, debug: bool = False) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Run team with streaming outputs using OpenAI Agents SDK.
        
        Args:
            message: User message
            debug: Whether to show debug info
            
        Yields:
            Dict: Stream outputs (response chunks, tool calls, handoffs, etc.)
        """
        self.logger.info(f"Contacting {self.team.orchestrator.name}")
        
        # Initialize handlers
        current_agent = self.team.orchestrator.name
        event_handler = StreamEventHandler(current_agent)
        error_handler = ErrorHandler(current_agent)
        mcp_manager = MCPServerManager()
        
        # Connect MCP servers before running
        all_agents = [self.team.orchestrator] + list(self.team.workers.values())
        await mcp_manager.connect_servers(all_agents)
        
        try:
            # Stream from orchestrator using OpenAI Agents SDK
            run_config = RunConfig(
                workflow_name=self.team.name or "Unknown Team",
            )
            
            result = Runner.run_streamed(self.team.orchestrator, input=message, run_config=run_config)
            
            self.logger.info("Starting to process streaming events...")
            
            async for event in result.stream_events():
                self.logger.debug(f"Received event: {event.type}. Item: {event}")
                
                # Use event handler to process events
                async for response in event_handler.handle_event(event):
                    # Update current agent if changed
                    if response.get('type') == 'agent_updated':
                        current_agent = response.get('agent_name', current_agent)
                        event_handler.current_agent = current_agent
                    yield response

            # Yield final completion
            yield {
                "type": "completion",
                "content": result.final_output,
                "output": result.final_output,
                "agent_name": current_agent,
                "is_done": True
            }
            
        except Exception as e:
            # Use simplified error handler
            error_response = error_handler.handle_error(e)
            yield error_response
            raise e
        finally:
            # Clean up MCP servers after streaming is complete
            await mcp_manager.cleanup_servers(all_agents)
    
    async def run_agent_until_done_async(self, agent, message: str) -> Dict[str, Any]:
        """
        Run a specific agent until completion.
        
        Args:
            agent: The agent to run
            message: Message to send
            
        Returns:
            Dict with agent outputs
        """
        result = await Runner.run(agent, input=message)
        
        return {
            "outputs": [{"type": "completion", "content": result.final_output}],
            "agent_name": agent.name,
            "is_done": True
        }
    
    async def run_single_agent_stream(self, agent_name: str, message: str, debug: bool = False) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Run a specific agent with streaming outputs using OpenAI Agents SDK.
        
        Args:
            agent_name: Name of the agent to run
            message: User message
            debug: Whether to show debug info
            
        Yields:
            Dict: Stream outputs (response chunks, tool calls, etc.)
        """
        # Get the target agent
        target_agent = self.team.get_agent(agent_name)
        if not target_agent:
            yield {
                "type": "error",
                "content": f"Agent '{agent_name}' not found in team configuration"
            }
            return
        
        self.logger.info(f"Executing single agent: {agent_name}")
        
        # Initialize handlers
        from .event_handlers import StreamEventHandler, ErrorHandler, MCPServerManager
        event_handler = StreamEventHandler(agent_name)
        error_handler = ErrorHandler(agent_name)
        mcp_manager = MCPServerManager()
        
        # Connect MCP servers for the target agent
        await mcp_manager.connect_servers([target_agent])
        
        try:
            # Stream from the target agent using OpenAI Agents SDK
            run_config = RunConfig(
                workflow_name=agent_name,
            )

            result = Runner.run_streamed(target_agent, input=message, run_config=run_config)
            
            self.logger.info(f"Starting to process streaming events for agent: {agent_name}")
            
            async for event in result.stream_events():
                self.logger.debug(f"Received event: {event.type}")
                
                # Use event handler to process events
                async for response in event_handler.handle_event(event):
                    yield response

            # Yield final completion
            yield {
                "type": "completion",
                "content": result.final_output,
                "output": result.final_output,
                "agent_name": agent_name,
                "is_done": True
            }
            
        except Exception as e:
            # Use error handler
            error_response = error_handler.handle_error(e)
            yield error_response
            raise e
        finally:
            # Clean up MCP servers
            await mcp_manager.cleanup_servers([target_agent])
    
