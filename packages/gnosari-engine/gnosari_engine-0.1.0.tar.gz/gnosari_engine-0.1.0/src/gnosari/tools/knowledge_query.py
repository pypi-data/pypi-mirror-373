"""
OpenAI Knowledge Query Tool - Using OpenAI Agents SDK FunctionTool class
"""

import logging
import asyncio
from typing import Any
from pydantic import BaseModel, Field
from agents import RunContextWrapper, FunctionTool


class KnowledgeQueryArgs(BaseModel):
    """Arguments for the knowledge query tool."""
    query: str = Field(..., description="The search query to find relevant information in the knowledge base")
    knowledge_name: str = Field(..., description="The name of the knowledge base to query")


class KnowledgeQueryTool:
    """Configurable Knowledge Query Tool that can be used in YAML configurations."""
    
    def __init__(self, knowledge_manager=None, tool_name: str = "knowledge_query", 
                 tool_description: str = "Query a knowledge base for relevant information"):
        """Initialize the knowledge query tool.
        
        Args:
            knowledge_manager: Knowledge manager instance
            tool_name: Name of the tool
            tool_description: Description of the tool
        """
        self.knowledge_manager = knowledge_manager
        self.tool_name = tool_name
        self.tool_description = tool_description
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        
        # Create the FunctionTool
        self.tool = FunctionTool(
            name=self.tool_name,
            description=self.tool_description,
            params_json_schema=KnowledgeQueryArgs.model_json_schema(),
            on_invoke_tool=self._run_knowledge_query
        )
    
    def set_knowledge_manager(self, knowledge_manager):
        """Set the knowledge manager reference."""
        self.knowledge_manager = knowledge_manager
        
    async def _run_knowledge_query(self, ctx: RunContextWrapper[Any], args: str) -> str:
        """
        Query a knowledge base for relevant information.
        
        Args:
            ctx: Run context wrapper
            args: JSON string containing KnowledgeQueryArgs
            
        Returns:
            Knowledge query result as string
        """
        try:
            # Parse arguments
            parsed_args = KnowledgeQueryArgs.model_validate_json(args)
            
            if not self.knowledge_manager:
                return "Error: Knowledge manager not available"
            
            self.logger.info(f"🔍 KNOWLEDGE QUERY STARTED - Query: '{parsed_args.query}' | Knowledge Base: '{parsed_args.knowledge_name}'")
            
            # Check if knowledge base exists
            if parsed_args.knowledge_name not in self.knowledge_manager.list_knowledge_bases():
                return f"Error: Knowledge base '{parsed_args.knowledge_name}' not found. Available bases: {self.knowledge_manager.list_knowledge_bases()}"
            
            # Perform the query (run synchronous code in executor)
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.knowledge_manager.query_knowledge, 
                parsed_args.knowledge_name, 
                parsed_args.query
            )
            
            # Log successful result
            result_preview = result[:200] + "..." if len(result) > 200 else result
            self.logger.info(f"✅ KNOWLEDGE QUERY SUCCESSFUL - Retrieved {len(result)} characters")
            self.logger.info(f"📄 Result preview: {result_preview}")
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to query knowledge base '{parsed_args.knowledge_name}': {str(e)}"
            self.logger.error(f"❌ KNOWLEDGE QUERY FAILED - {error_msg}")
            return error_msg
    
    def get_tool(self) -> FunctionTool:
        """Get the FunctionTool instance.
        
        Returns:
            FunctionTool instance
        """
        return self.tool


# No global variables needed - use direct instantiation or tool_manager for dynamic loading
