"""
OpenAI Delegate Agent Tool - Using OpenAI Agents SDK FunctionTool class
"""

import logging
import asyncio
from typing import Any, Optional
from pydantic import BaseModel, Field
from agents import RunContextWrapper, FunctionTool


class DelegateAgentArgs(BaseModel):
    """Arguments for the delegate agent tool."""
    target_agent: str = Field(..., description="Name of the agent to delegate the task to")
    message: str = Field(..., description="The message or task to delegate to the target agent")


class DelegateAgentTool:
    """Configurable Delegate Agent Tool that can be used in YAML configurations."""
    
    def __init__(self, tool_name: str = "delegate_agent", 
                 tool_description: str = "Delegate a task to another agent in the team"):
        """Initialize the delegate agent tool.
        
        Args:
            tool_name: Name of the tool
            tool_description: Description of the tool
        """
        self.tool_name = tool_name
        self.tool_description = tool_description
        self.team = None
        self.team_executor = None
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        
        # Create the FunctionTool
        self.tool = FunctionTool(
            name=self.tool_name,
            description=self.tool_description,
            params_json_schema=DelegateAgentArgs.model_json_schema(),
            on_invoke_tool=self._run_delegate_agent
        )
    
    def set_team_dependencies(self, team, team_executor):
        """Set the team and team executor references."""
        self.team = team
        self.team_executor = team_executor
        
    async def _run_delegate_agent(self, ctx: RunContextWrapper[Any], args: str) -> str:
        """
        Delegate a task to another agent in the team.
        
        Args:
            ctx: Run context wrapper
            args: JSON string containing DelegateAgentArgs
            
        Returns:
            Delegation result as string
        """
        try:
            # Parse arguments
            parsed_args = DelegateAgentArgs.model_validate_json(args)
            
            if not self.team:
                return "Error: Team not available for delegation"
            
            if not self.team_executor:
                return "Error: Team executor not available for delegation"
            
            self.logger.info(f"🤝 DELEGATION STARTED - Target Agent: '{parsed_args.target_agent}' | Message: '{parsed_args.message[:100]}{'...' if len(parsed_args.message) > 100 else ''}'")
            
            # Get the target agent from the team
            target_gnosari_agent = self.team.get_agent(parsed_args.target_agent)
            if not target_gnosari_agent:
                available_agents = ', '.join(self.team.list_agents())
                return f"Error: Agent '{parsed_args.target_agent}' not found in the team. Available agents: {available_agents}"
            
            # Log the delegation
            self.logger.info(f"Contacting Agent {parsed_args.target_agent}")
            
            # Use the team executor's run_agent_until_done_async method
            result = await self.team_executor.run_agent_until_done_async(target_gnosari_agent, parsed_args.message)

            
            self.logger.info(f"Delegation of Agent Result '{result}'")
            # Extract response content from outputs
            response_content = ""
            reasoning_content = ""
            
            if isinstance(result, dict) and "outputs" in result:
                for output in result["outputs"]:
                    if output.get("type") == "response":
                        response_content += output.get("content", "")
                    elif output.get("type") == "reasoning":
                        reasoning_content += str(output.get("content", ""))
                    elif output.get("type") == "completion":
                        response_content = output.get("content", "")
            else:
                # Fallback for old format
                response_content = str(result)
            
            # Log the delegated agent response
            self.logger.info(f"[{parsed_args.target_agent}] Response: {response_content}")
            if reasoning_content:
                self.logger.info(f"[{parsed_args.target_agent}] Reasoning: {reasoning_content}")

            # Create response text
            if reasoning_content:
                response_text = f"Reasoning: {reasoning_content}\nResponse: {response_content}"
            else:
                response_text = response_content
            
            # Log successful delegation
            response_preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
            self.logger.info(f"✅ DELEGATION SUCCESSFUL - Agent '{parsed_args.target_agent}' responded with {len(response_text)} characters")
            self.logger.info(f"📄 Response preview: {response_preview}")
            
            return response_text
            
        except Exception as e:
            error_msg = f"Failed to delegate to agent '{parsed_args.target_agent}': {str(e)}"
            self.logger.error(f"❌ DELEGATION FAILED - {error_msg}")
            return error_msg
    
    def get_tool(self) -> FunctionTool:
        """Get the FunctionTool instance.
        
        Returns:
            FunctionTool instance
        """
        return self.tool


# No global variables needed - use direct instantiation or tool_manager for dynamic loading

def set_team_dependencies(team, team_executor):
    """Legacy compatibility function - team_builder now handles dependencies directly."""
    # This function is kept only for any remaining legacy code that might call it
    # The team_builder now sets dependencies directly on tool instances
    pass
