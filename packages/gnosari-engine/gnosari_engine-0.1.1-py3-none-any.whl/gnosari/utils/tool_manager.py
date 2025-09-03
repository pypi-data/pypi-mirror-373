import logging
from typing import Dict, List, Any, Optional
from ..schemas.base import BaseTool

# Legacy imports removed - now using OpenAI Agents SDK compatible tools


class ToolManager:
    """Manages tool creation, injection, and information for agents."""
    
    def __init__(self, knowledge_manager=None):
        """Initialize the tool manager.
        
        Args:
            knowledge_manager: Optional knowledge manager instance for knowledge tools
        """
        self.available_tools: Dict[str, Dict[str, Any]] = {}
        self.agents_tools: Dict[str, Dict[str, BaseTool]] = {}
        self.knowledge_manager = knowledge_manager
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        
        # Auto-register core tools that are always available
        self._register_core_tools()
    
    def _register_core_tools(self) -> None:
        """Register core tools that are always available."""
        # Register delegate_agent tool for orchestrators (now using FunctionTool class)
        self.available_tools['delegate_agent'] = {
            'module': 'gnosari.tools.delegate_agent',
            'class': 'DelegateAgentTool',
            'args': {}
        }
        self.logger.debug("Auto-registered delegate_agent core tool")
    
    def load_tools(self, config: Dict[str, Any]) -> None:
        """Load tool definitions from the team configuration.
        
        Args:
            config: Team configuration dictionary
        """
        if 'tools' not in config:
            self.logger.debug("No tools defined in team configuration")
            return
        
        for tool_config in config['tools']:
            tool_name = tool_config['name']
            self.available_tools[tool_name] = tool_config
            self.logger.debug(f"Loaded tool definition: {tool_name}")
        
        # Register knowledge_query tool if knowledge bases are defined
        if 'knowledge' in config and self.knowledge_manager is not None:
            self.available_tools['knowledge_query'] = {
                'module': 'gnosari.tools.knowledge_query',
                'class': 'KnowledgeQueryTool',
                'args': {
                    'knowledge_manager': self.knowledge_manager
                }
            }
            self.logger.debug("Registered knowledge_query tool")
    
    def create_tool_instance(self, tool_name: str) -> BaseTool:
        """Create a tool instance from the tool definition.
        
        Args:
            tool_name: Name of the tool to create
            
        Returns:
            Tool instance
        """
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not found in available tools")
        
        tool_config = self.available_tools[tool_name]
        module_name = tool_config['module']
        class_name = tool_config['class']
        args = tool_config.get('args', {})
        
        # Import the module for regular tools
        try:
            module = __import__(module_name, fromlist=[class_name])
            tool_class = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Failed to import tool class {class_name} from {module_name}: {e}")
        
        # Create tool instance with args
        try:
            if args and args != "pass":
                # Check if the tool class expects a config object
                if hasattr(tool_class, '__init__'):
                    import inspect
                    sig = inspect.signature(tool_class.__init__)
                    params = list(sig.parameters.keys())
                    
                    # If the first parameter is 'config' (after self), create config object
                    if len(params) > 1 and params[1] == 'config':
                        # Try to find the config class
                        config_class_name = f"{class_name}Config"
                        if hasattr(module, config_class_name):
                            config_class = getattr(module, config_class_name)
                            config_instance = config_class(**args)
                            tool_instance = tool_class(config_instance)
                        else:
                            # Fallback: pass args as config dict
                            tool_instance = tool_class(args)
                    else:
                        tool_instance = tool_class(**args)
                else:
                    tool_instance = tool_class(**args)
            else:
                tool_instance = tool_class()
            return tool_instance
        except Exception as e:
            raise ValueError(f"Failed to create tool instance for {tool_name}: {e}")
    
    def inject_tools_for_agent(self, agent_name: str, agent_tools: List[str]) -> None:
        """Inject tools for a specific agent.

        Args:
            agent_name: Name of the agent
            agent_tools: List of tool names to inject
        """
        if not agent_tools:
            return

        self.agents_tools[agent_name] = {}

        for tool_name in agent_tools:
            try:
                tool_instance = self.create_tool_instance(tool_name)
                self.agents_tools[agent_name][tool_name] = tool_instance

                self.logger.debug(f"Added tool '{tool_name}' to agent '{agent_name}'")
            except Exception as e:
                self.logger.warning(f"Failed to add tool '{tool_name}' to agent '{agent_name}': {e}")
    
    def get_tool_info(self, tool_instance: BaseTool, tool_name: str) -> str:
        """Get formatted tool information for system prompt injection.
        
        Args:
            tool_instance: The tool instance
            tool_name: The name of the tool
            
        Returns:
            Formatted tool information string
        """
        try:
            # Get input schema information
            input_schema = tool_instance.input_schema
            input_fields = []
            
            if hasattr(input_schema, 'model_json_schema'):
                # Fallback to Pydantic schema
                schema = input_schema.model_json_schema()
                if 'properties' in schema:
                    for field_name, field_info in schema['properties'].items():
                        field_type = self._format_field_type(field_info)
                        field_desc = field_info.get('description', 'No description')
                        required = field_name in schema.get('required', [])
                        required_text = " (required)" if required else " (optional)"
                        input_fields.append(f"  - {field_name}: {field_type}{required_text} - {field_desc}")
            
            # Get tool name from config or instance
            if hasattr(tool_instance, 'config') and hasattr(tool_instance.config, 'tool_name'):
                actual_tool_name = tool_instance.config.tool_name
            elif hasattr(tool_instance, 'tool_name'):
                actual_tool_name = tool_instance.tool_name
            else:
                actual_tool_name = tool_name
            
            # Get tool description from config or instance
            if hasattr(tool_instance, 'config') and hasattr(tool_instance.config, 'tool_description'):
                tool_description = tool_instance.config.tool_description
            elif hasattr(tool_instance, 'tool_description'):
                tool_description = tool_instance.tool_description
            else:
                tool_description = "No description available"
            
            # Format the tool information
            tool_info = f"Tool: {actual_tool_name}"
            tool_info += f"\nDescription: {tool_description}"
            if input_fields:
                tool_info += f"\nParameters:"
                tool_info += "\n" + "\n".join(input_fields)
            
            return tool_info
            
        except Exception as e:
            self.logger.warning(f"Failed to get tool info for {tool_name}: {e}")
            return f"Tool: {tool_name}\nDescription: Tool information unavailable"
    
    def _format_field_type(self, field_info: Dict[str, Any]) -> str:
        """Format field type information for better readability.
        
        Args:
            field_info: Field information from schema
            
        Returns:
            Formatted type string
        """
        field_type = field_info.get('type', 'unknown')
        
        if field_type == 'array':
            items = field_info.get('items', {})
            if items.get('type') == 'object':
                # Array of objects - try to describe the structure
                properties = items.get('properties', {})
                if properties:
                    prop_descriptions = []
                    for prop_name, prop_info in properties.items():
                        prop_type = self._format_nested_type(prop_info)
                        prop_descriptions.append(f"{prop_name} ({prop_type})")
                    
                    return f"array of objects with fields: {', '.join(prop_descriptions)}"
                else:
                    return "array of objects"
            elif items.get('type'):
                nested_type = self._format_nested_type(items)
                return f"array of {nested_type}"
            else:
                return "array"
        elif field_type == 'object':
            properties = field_info.get('properties', {})
            if properties:
                prop_descriptions = []
                for prop_name, prop_info in properties.items():
                    prop_type = self._format_nested_type(prop_info)
                    prop_descriptions.append(f"{prop_name} ({prop_type})")
                return f"object with fields: {', '.join(prop_descriptions)}"
            else:
                return "object"
        else:
            return field_type
    
    def _format_nested_type(self, field_info: Dict[str, Any]) -> str:
        """Format nested field type information.
        
        Args:
            field_info: Field information from schema
            
        Returns:
            Formatted type string
        """
        field_type = field_info.get('type', 'unknown')
        
        if field_type == 'array':
            items = field_info.get('items', {})
            if items.get('type'):
                return f"array of {items['type']}"
            else:
                return "array"
        else:
            return field_type
    
    def execute_agent_tool(self, agent_name: str, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool for a specific agent.
        
        Args:
            agent_name: Name of the agent
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            
        Returns:
            Tool execution result
        """
        if agent_name not in self.agents_tools:
            raise ValueError(f"Agent '{agent_name}' has no tools")
        
        if tool_name not in self.agents_tools[agent_name]:
            raise ValueError(f"Tool '{tool_name}' not found for agent '{agent_name}'")
        
        tool = self.agents_tools[agent_name][tool_name]
        
        # Get the tool's input schema
        input_schema = tool.input_schema
        
        # Create input instance
        tool_input_instance = input_schema(**tool_input)
        
        # Execute the tool
        result = tool.run(tool_input_instance)
        
        return result
    
    def update_delegate_tools(self, agents: Dict[str, Any], debug: bool = False) -> None:
        """Update delegate tools with team agents reference.
        
        Args:
            agents: Dictionary of built agents
            debug: Whether to show debug information
        """
        for agent_name, agent_tools in self.agents_tools.items():
            for tool_name, tool in agent_tools.items():
                if hasattr(tool, 'team_agents'):
                    tool.team_agents = agents
                    if debug:
                        self.logger.debug(f"Updated {tool_name} for {agent_name} with team agents: {list(agents.keys())}")
    
    def get_agent_tools(self, agent_name: str) -> Dict[str, BaseTool]:
        """Get tools for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Dictionary of tools for the agent
        """
        return self.agents_tools.get(agent_name, {})
    
    def has_tools(self, agent_name: str) -> bool:
        """Check if an agent has any tools.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if agent has tools, False otherwise
        """
        return agent_name in self.agents_tools and len(self.agents_tools[agent_name]) > 0
