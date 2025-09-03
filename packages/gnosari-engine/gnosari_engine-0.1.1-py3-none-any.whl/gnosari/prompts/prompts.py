"""Core prompt building functions and constants for the Gnosari framework."""

from typing import Dict, List, Any
from .tool_prompts import get_tools_definition

# Prompt constants for team runner
TOOL_EXECUTION_RESULT_PROMPT = "Tool execution completed successfully."
TOOL_EXECUTION_ERROR_PROMPT = "Tool execution failed with error."
TOOL_NOT_AVAILABLE_PROMPT = "Requested tool is not available."
CONTINUE_PROCESSING_PROMPT = "Continue processing the request."
ORCHESTRATION_PLANNING_PROMPT = "Planning orchestration strategy."
FEEDBACK_LOOP_PROMPT = "Processing feedback and updating strategy."


def build_orchestrator_system_prompt(name: str, instructions: str, team_config: Dict[str, Any], agent_tools: List[str] = None, tool_manager = None, agent_config: Dict[str, Any] = None, knowledge_descriptions: Dict[str, str] = None) -> Dict[str, List[str]]:
    """Build system prompt components for an orchestrator agent.
    
    Args:
        name: Orchestrator agent name
        instructions: Orchestrator instructions
        team_config: Team configuration dictionary
        agent_tools: List of tool names for this agent
        tool_manager: Tool manager instance for getting tool descriptions
        
    Returns:
        Dictionary with 'background', 'steps', and 'output_instructions' lists
    """
    # Load tool definitions if tool_manager is provided
    if tool_manager and team_config and 'tools' in team_config:
        tool_manager.load_tools(team_config)
    # Get available agents for delegation
    available_agents = []
    agent_descriptions = []
    
    if team_config and 'agents' in team_config:
        for agent_config in team_config['agents']:
            agent_name = agent_config['name']
            if agent_name != name:
                available_agents.append(agent_name)
                agent_instructions = agent_config['instructions']
                agent_descriptions.append(f"- {agent_name}: {agent_instructions}")
    
    background = [
        f"You are {name}, an autonomous agent.",
        f"Available agents for delegation:",
        *agent_descriptions,
        "",
    ]
    
    # Add knowledge base information if agent has knowledge access
    if agent_config and 'knowledge' in agent_config:
        knowledge_names = agent_config['knowledge']
        if knowledge_names:
            background.append("KNOWLEDGE BASES:")
            background.append("You have access to the following knowledge bases:")
            for kb_name in knowledge_names:
                if knowledge_descriptions and kb_name in knowledge_descriptions:
                    description = knowledge_descriptions[kb_name]
                    background.append(f"- {kb_name}: {description}")
                else:
                    background.append(f"- {kb_name}")
            background.append("")
            background.append("To query these knowledge bases, use the knowledge_query tool with the exact knowledge base name.")
            background.append("")
    
    # Inject tools for this agent first
    if agent_tools and tool_manager:
        tool_manager.inject_tools_for_agent(name, agent_tools)
    
    # Get tool information and add to background
    tool_sections = get_tools_definition(agent_tools, tool_manager)
    background.extend(tool_sections)
    
    steps = [
        instructions
    ]
    
    output_instructions = [
        "Respond naturally to the user's request. If you need to delegate tasks to other agents, use the available tools.",
        "You can use tools to delegate tasks to other agents when needed."
    ]
    
    return {
        "background": background,
        "steps": steps,
        "output_instructions": output_instructions
    }

def build_specialized_agent_system_prompt(name: str, instructions: str, agent_tools: List[str] = None, tool_manager = None, agent_config: Dict[str, Any] = None, knowledge_descriptions: Dict[str, str] = None) -> Dict[str, List[str]]:
    """Build system prompt components for a specialized agent.
    
    Args:
        name: Agent name
        instructions: Agent instructions
        agent_tools: List of tool names for this agent
        tool_manager: Tool manager instance for getting tool descriptions
        
    Returns:
        Dictionary with 'background', 'steps', and 'output_instructions' lists
    """
    background = [
        f"You are {name}, an autonomous specialized agent. You are given tasks and you have to execute them using the available tools.",
        "",
        "IMPORTANT: Analyze each request and use tools.",
        ""
    ]
    
    # Add knowledge base information if agent has knowledge access
    if agent_config and 'knowledge' in agent_config:
        knowledge_names = agent_config['knowledge']
        if knowledge_names:
            background.append("KNOWLEDGE BASES:")
            background.append("You have access to the following knowledge bases:")
            for kb_name in knowledge_names:
                if knowledge_descriptions and kb_name in knowledge_descriptions:
                    description = knowledge_descriptions[kb_name]
                    background.append(f"- {kb_name}: {description}")
                else:
                    background.append(f"- {kb_name}")
            background.append("")
            background.append("IMPORTANT: ALWAYS use the knowledge_query tool to search your knowledge bases when answering questions.")
            background.append("To query these knowledge bases, use the knowledge_query tool with the exact knowledge base name.")
            background.append("Do not provide generic answers - always search your knowledge first.")
            background.append("")
    
    # Inject tools for this agent first
    if agent_tools and tool_manager:
        tool_manager.inject_tools_for_agent(name, agent_tools)
    
    # Get tool information and add to background
    tool_sections = get_tools_definition(agent_tools, tool_manager)
    background.extend(tool_sections)
    
    steps = [
        instructions
    ]
    
    output_instructions = [
        "Respond naturally to the user's request using the available tools when needed.",
    ]
    
    return {
        "background": background,
        "steps": steps,
        "output_instructions": output_instructions
    }
