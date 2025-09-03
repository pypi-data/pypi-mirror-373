import asyncio
from typing import Dict, Any, Optional, List
from fastmcp import Client


class MCPClient:
    """
    A class-based MCP client that supports multiple servers and provides
    convenient methods for interacting with MCP servers.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, server_name: Optional[str] = None):
        """
        Initialize the MCP client.
        
        Args:
            config: Configuration dictionary with MCP servers
            server_name: Specific server name to use from config (if config is provided)
        """
        self.config = config or {}
        self.server_name = server_name
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Setup the underlying FastMCP client based on configuration."""
        try:
            if self.config and "mcpServers" in self.config:
                if self.server_name:
                    if self.server_name not in self.config["mcpServers"]:
                        raise ValueError(f"Server '{self.server_name}' not found in config")
                    server_config = self.config["mcpServers"][self.server_name]
                    # For HTTP servers, pass the URL directly
                    if "url" in server_config:
                        self.client = Client(server_config["url"])
                    else:
                        self.client = Client(server_config)
                else:
                    # Use the first server if no specific server is specified
                    first_server = next(iter(self.config["mcpServers"].values()))
                    if "url" in first_server:
                        self.client = Client(first_server["url"])
                    else:
                        self.client = Client(first_server)
            else:
                # Default to localhost if no config provided
                self.client = Client("http://localhost:58204")
        except Exception as e:
            # If client setup fails, store the error for later handling
            self.client = None
            self._setup_error = str(e)
    
    async def __aenter__(self):
        """Async context manager entry."""
        if self.client:
            try:
                await self.client.__aenter__()
            except Exception as e:
                # If async context fails, raise the error
                raise RuntimeError(f"Client failed to connect: {e}")
        elif hasattr(self, '_setup_error'):
            # If setup failed, raise the original error
            raise RuntimeError(f"Client setup failed: {self._setup_error}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            try:
                await self.client.__aexit__(exc_type, exc_val, exc_tb)
            except Exception:
                # Ignore cleanup errors
                pass
    
    async def ping(self) -> bool:
        """
        Ping the MCP server to check connectivity.
        
        Returns:
            bool: True if ping successful, False otherwise
        """
        try:
            await self.client.ping()
            return True
        except Exception:
            return False
    
    async def list_tools(self) -> List[Any]:
        """
        List all available tools from the MCP server.
        
        Returns:
            List[Any]: List of available tools (Tool objects)
            
        Raises:
            RuntimeError: If connection to MCP server fails
        """
        try:
            tools = await self.client.list_tools()
            return tools
        except GeneratorExit as e:
            # Handle connection interruption gracefully
            error_msg = f"MCP server connection was interrupted (GeneratorExit): {e}"
            print(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg)
        except ConnectionError as e:
            # Handle connection errors
            error_msg = f"MCP server connection error: {e}"
            print(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg)
        except TimeoutError as e:
            # Handle timeout errors
            error_msg = f"MCP server connection timeout: {e}"
            print(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg)
        except Exception as e:
            # Handle all other errors
            error_msg = f"Failed to connect to MCP server: {e}"
            print(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg)
    
    def tools_to_dict(self, tools: List[Any]) -> List[Dict[str, Any]]:
        """
        Convert Tool objects to dictionaries for easier manipulation.
        
        Args:
            tools: List of Tool objects
            
        Returns:
            List[Dict[str, Any]]: List of tool dictionaries
        """
        result = []
        for tool in tools:
            try:
                # Safely extract tool attributes, handling both properties and methods
                tool_dict = {}
                
                # Handle name - could be property or method
                name_attr = getattr(tool, 'name', None)
                if callable(name_attr):
                    tool_dict["name"] = name_attr()
                else:
                    tool_dict["name"] = name_attr
                
                # Handle title - could be property or method
                title_attr = getattr(tool, 'title', None)
                if callable(title_attr):
                    tool_dict["title"] = title_attr()
                else:
                    tool_dict["title"] = title_attr
                
                # Handle description - could be property or method
                desc_attr = getattr(tool, 'description', None)
                if callable(desc_attr):
                    tool_dict["description"] = desc_attr()
                else:
                    tool_dict["description"] = desc_attr
                
                # Handle inputSchema - could be property or method
                input_schema_attr = getattr(tool, 'inputSchema', None)
                if callable(input_schema_attr):
                    tool_dict["inputSchema"] = input_schema_attr()
                else:
                    tool_dict["inputSchema"] = input_schema_attr
                
                # Handle outputSchema - could be property or method
                output_schema_attr = getattr(tool, 'outputSchema', None)
                if callable(output_schema_attr):
                    tool_dict["outputSchema"] = output_schema_attr()
                else:
                    tool_dict["outputSchema"] = output_schema_attr
                
                # Handle annotations - could be property or method
                annotations_attr = getattr(tool, 'annotations', None)
                if callable(annotations_attr):
                    tool_dict["annotations"] = annotations_attr()
                else:
                    tool_dict["annotations"] = annotations_attr
                
                # Handle meta - could be property or method
                meta_attr = getattr(tool, 'meta', None)
                if callable(meta_attr):
                    tool_dict["meta"] = meta_attr()
                else:
                    tool_dict["meta"] = meta_attr
                
                result.append(tool_dict)
                
            except Exception as e:
                # If we can't convert a tool, log the error and skip it
                print(f"Warning: Could not convert tool to dict: {e}")
                # Try to get at least the name
                try:
                    name_attr = getattr(tool, 'name', None)
                    if callable(name_attr):
                        name = name_attr()
                    else:
                        name = name_attr
                    result.append({"name": name, "error": f"Conversion failed: {e}"})
                except:
                    result.append({"name": "unknown", "error": f"Conversion failed: {e}"})
        
        return result
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """
        List all available resources from the MCP server.
        
        Returns:
            List[Dict[str, Any]]: List of available resources
        """
        try:
            resources = await self.client.list_resources()
            return resources
        except Exception as e:
            print(f"Error listing resources: {e}")
            return []
    
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """
        List all available prompts from the MCP server.
        
        Returns:
            List[Dict[str, Any]]: List of available prompts
        """
        try:
            prompts = await self.client.list_prompts()
            return prompts
        except Exception as e:
            print(f"Error listing prompts: {e}")
            return []
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a specific tool with the given parameters.
        
        Args:
            tool_name: Name of the tool to call
            parameters: Parameters to pass to the tool
            
        Returns:
            Dict[str, Any]: Result from the tool execution
        """
        try:
            result = await self.client.call_tool(tool_name, parameters)
            return result
        except GeneratorExit as e:
            # Handle connection interruption gracefully
            error_msg = f"MCP server connection was interrupted while calling tool '{tool_name}': {e}"
            print(f"ERROR: {error_msg}")
            return {"error": error_msg}
        except ConnectionError as e:
            # Handle connection errors
            error_msg = f"MCP server connection error while calling tool '{tool_name}': {e}"
            print(f"ERROR: {error_msg}")
            return {"error": error_msg}
        except TimeoutError as e:
            # Handle timeout errors
            error_msg = f"MCP server connection timeout while calling tool '{tool_name}': {e}"
            print(f"ERROR: {error_msg}")
            return {"error": error_msg}
        except Exception as e:
            # Handle all other errors
            error_msg = f"Error calling tool '{tool_name}': {e}"
            print(f"ERROR: {error_msg}")
            return {"error": error_msg}


# Example usage functions
async def example_single_server():
    """Example usage with a single HTTP server."""
    client = MCPClient()
    
    async with client:
        # Check connectivity
        if await client.ping():
            print("Server is reachable")
        
        # List available operations
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()
        
        print(f"Available tools: {tools}")
        print(f"Available resources: {resources}")
        print(f"Available prompts: {prompts}")
        
        # Show tool details
        if tools:
            print("\nTool details:")
            for i, tool in enumerate(tools):
                print(f"  {i+1}. {tool.name}: {tool.description}")
            
            # Convert to dictionaries if needed
            tools_dict = client.tools_to_dict(tools)
            print(f"\nTools as dictionaries: {tools_dict}")
            
            # Execute a tool if available
            first_tool = tools[0]
            tool_name = first_tool.name
            print(f"\nExecuting tool: {tool_name}")
            
            # Get tool parameters from inputSchema
            if hasattr(first_tool, 'inputSchema') and first_tool.inputSchema:
                required_params = first_tool.inputSchema.get('required', [])
                properties = first_tool.inputSchema.get('properties', {})
                
                # Create sample parameters based on the tool's schema
                sample_params = {}
                for param_name, param_info in properties.items():
                    if param_name in required_params:
                        if param_info.get('type') == 'string':
                            sample_params[param_name] = "sample_value"
                        elif param_info.get('type') == 'number':
                            sample_params[param_name] = 10
                        else:
                            sample_params[param_name] = None
                
                result = await client.call_tool(tool_name, sample_params)
                print(f"Tool result: {result}")
            else:
                result = await client.call_tool(tool_name, {})
                print(f"Tool result: {result}")


async def example_multi_server():
    """Example usage with multiple servers configuration."""
    config = {
        "mcpServers": {
            "weather": {"url": "https://weather-api.example.com/mcp"},
            "assistant": {"url": "https://assistant-api.example.com/mcp"}
        }
    }
    
    # Use weather server
    weather_client = MCPClient(config, "weather")
    async with weather_client:
        tools = await weather_client.list_tools()
        print(f"Weather server tools: {tools}")
    
    # Use assistant server
    assistant_client = MCPClient(config, "assistant")
    async with assistant_client:
        tools = await assistant_client.list_tools()
        print(f"Assistant server tools: {tools}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_single_server())