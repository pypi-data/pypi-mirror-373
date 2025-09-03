"""Tool prompt generation for agent system prompts."""

from typing import List, Dict, Any


def get_tools_definition(agent_tools: List[str], tool_manager) -> List[str]:
    """Generate tool definitions for system prompt injection.
    
    Args:
        agent_tools: List of tool names for the agent
        tool_manager: Tool manager instance for getting tool information
        
    Returns:
        List of strings containing tool definitions and usage instructions
    """
    if not agent_tools or not tool_manager:
        return []
    
    tool_sections = []
    
    # # Add tool descriptions
    # tool_descriptions = []
    # for tool_name in agent_tools:
    #     try:
    #         # Get tool instance from the tool manager
    #         tool_instance = tool_manager.create_tool_instance(tool_name)
    #         tool_info = tool_manager.get_tool_info(tool_instance, tool_name)
    #         tool_descriptions.append(tool_info)
    #     except Exception:
    #         # If tool not found, add a placeholder
    #         tool_descriptions.append(f"Tool: {tool_name}\nDescription: Tool information unavailable")
    #
    # if tool_descriptions:
    #     tool_sections.append("")
    #     tool_sections.append("AVAILABLE TOOLS:")
    #     tool_sections.extend(tool_descriptions)
    #     tool_sections.append("")
    #     tool_sections.append("TOOL USAGE INSTRUCTIONS:")
    #     tool_sections.append("- To use a tool, set execute_tool to the tool name and input parameters")
    #     tool_sections.append("- Set is_done to false when using tools, true when finished")
    #     tool_sections.append("- Tools will be executed automatically and results provided to you")
    #     tool_sections.append("CRITICAL:")
    #     tool_sections.append("- DO NOT USE tools that don't exist in your system")
    #     tool_sections.append("- Call functions sequentially")

    return tool_sections



