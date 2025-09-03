"""Prompt viewer for visualizing system prompts generated for agents."""

import yaml
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text

from .tool_manager import ToolManager
from .orchestrator_prompts import (
    build_orchestrator_system_prompt,
    build_specialized_agent_system_prompt
)


class PromptViewer:
    """Viewer for agent system prompts."""
    
    def __init__(self):
        """Initialize the prompt viewer."""
        self.console = Console()
        self.tool_manager = ToolManager()
    
    def load_team_config(self, config_path: str) -> Dict[str, Any]:
        """Load team configuration from YAML file.
        
        Args:
            config_path: Path to the YAML configuration file
            
        Returns:
            Team configuration dictionary
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Team configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def find_agent_config(self, team_config: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
        """Find agent configuration by name.
        
        Args:
            team_config: Team configuration dictionary
            agent_name: Name of the agent to find
            
        Returns:
            Agent configuration dictionary
            
        Raises:
            ValueError: If agent is not found
        """
        if 'agents' not in team_config:
            raise ValueError("Team configuration must contain 'agents' section")
        
        for agent_config in team_config['agents']:
            if agent_config['name'] == agent_name:
                return agent_config
        
        raise ValueError(f"Agent '{agent_name}' not found in team configuration")
    
    def get_tool_descriptions(self, agent_tools: List[str]) -> List[str]:
        """Get tool descriptions for the agent.
        
        Args:
            agent_tools: List of tool names for the agent
            
        Returns:
            List of tool description strings
        """
        if not agent_tools:
            return []
        
        tool_descriptions = []
        for tool_name in agent_tools:
            try:
                tool_instance = self.tool_manager.create_tool_instance(tool_name)
                tool_info = self.tool_manager.get_tool_info(tool_instance, tool_name)
                tool_descriptions.append(tool_info)
            except Exception as e:
                tool_descriptions.append(f"Tool: {tool_name}\nError: Failed to load tool - {e}")
        
        return tool_descriptions
    
    def view_agent_prompt(self, config_path: str, agent_name: str) -> str:
        """View the system prompt for a specific agent.
        
        Args:
            config_path: Path to the team configuration file
            agent_name: Name of the agent to view
            
        Returns:
            Formatted prompt information
        """
        # Load team configuration
        team_config = self.load_team_config(config_path)
        
        # Load tool definitions
        self.tool_manager.load_tools(team_config)
        
        # Find agent configuration
        agent_config = self.find_agent_config(team_config, agent_name)
        
        # Extract agent details
        name = agent_config['name']
        instructions = agent_config['instructions']
        is_orchestrator = agent_config.get('orchestrator', False)
        agent_tools = agent_config.get('tools', [])
        
        # Generate system prompt components
        if is_orchestrator:
            prompt_components = build_orchestrator_system_prompt(
                name, instructions, team_config, agent_tools, self.tool_manager
            )
        else:
            prompt_components = build_specialized_agent_system_prompt(
                name, instructions, agent_tools, self.tool_manager
            )
        
        # Format the output
        output_lines = []
        
        # Agent information
        output_lines.append(f"Agent Name: {name}")
        output_lines.append(f"Type: {'Orchestrator' if is_orchestrator else 'Specialized Agent'}")
        if agent_tools:
            output_lines.append(f"Tools: {', '.join(agent_tools)}")
        else:
            output_lines.append("Tools: None")
        output_lines.append("")
        
        # Background section
        output_lines.append("=" * 60)
        output_lines.append("BACKGROUND")
        output_lines.append("=" * 60)
        for line in prompt_components["background"]:
            output_lines.append(line)
        output_lines.append("")
        
        # Steps section
        output_lines.append("=" * 60)
        output_lines.append("STEPS")
        output_lines.append("=" * 60)
        for i, step in enumerate(prompt_components["steps"], 1):
            output_lines.append(f"{i}. {step}")
        output_lines.append("")
        
        # Output instructions section
        output_lines.append("=" * 60)
        output_lines.append("OUTPUT INSTRUCTIONS")
        output_lines.append("=" * 60)
        for line in prompt_components["output_instructions"]:
            output_lines.append(line)
        
        return "\n".join(output_lines)
    
    def view_agent_prompt_section(self, config_path: str, agent_name: str, section: str) -> str:
        """View a specific section of the system prompt for an agent.
        
        Args:
            config_path: Path to the team configuration file
            agent_name: Name of the agent to view
            section: Section to view (background, steps, output, tools, all)
            
        Returns:
            Formatted section information
        """
        # Load team configuration
        team_config = self.load_team_config(config_path)
        
        # Load tool definitions
        self.tool_manager.load_tools(team_config)
        
        # Find agent configuration
        agent_config = self.find_agent_config(team_config, agent_name)
        
        # Extract agent details
        name = agent_config['name']
        instructions = agent_config['instructions']
        is_orchestrator = agent_config.get('orchestrator', False)
        agent_tools = agent_config.get('tools', [])
        
        # Generate system prompt components
        if is_orchestrator:
            prompt_components = build_orchestrator_system_prompt(
                name, instructions, team_config, agent_tools, self.tool_manager
            )
        else:
            prompt_components = build_specialized_agent_system_prompt(
                name, instructions, agent_tools, self.tool_manager
            )
        
        # Return the requested section
        if section == "background":
            return "\n".join(prompt_components["background"])
        elif section == "steps":
            steps = []
            for i, step in enumerate(prompt_components["steps"], 1):
                steps.append(f"{i}. {step}")
            return "\n".join(steps)
        elif section == "output":
            return "\n".join(prompt_components["output_instructions"])
        elif section == "tools":
            # Extract only the tools section from background
            background_lines = prompt_components["background"]
            tools_section = []
            in_tools_section = False
            
            for i, line in enumerate(background_lines):
                if "AVAILABLE TOOLS:" in line:
                    in_tools_section = True
                    tools_section.append(line)
                elif in_tools_section:
                    if "TOOL USAGE INSTRUCTIONS:" in line:
                        tools_section.append(line)
                        # Add the next few lines for usage instructions
                        for j in range(i + 1, min(i + 4, len(background_lines))):
                            if background_lines[j].strip() and not background_lines[j].startswith("="):
                                tools_section.append(background_lines[j])
                        break
                    else:
                        tools_section.append(line)
            
            return "\n".join(tools_section) if tools_section else "No tools available for this agent."
        elif section == "all":
            # Return all sections
            output_lines = []
            
            # Background section
            output_lines.append("=" * 60)
            output_lines.append("BACKGROUND")
            output_lines.append("=" * 60)
            for line in prompt_components["background"]:
                output_lines.append(line)
            output_lines.append("")
            
            # Steps section
            output_lines.append("=" * 60)
            output_lines.append("STEPS")
            output_lines.append("=" * 60)
            for i, step in enumerate(prompt_components["steps"], 1):
                output_lines.append(f"{i}. {step}")
            output_lines.append("")
            
            # Output instructions section
            output_lines.append("=" * 60)
            output_lines.append("OUTPUT INSTRUCTIONS")
            output_lines.append("=" * 60)
            for line in prompt_components["output_instructions"]:
                output_lines.append(line)
            
            return "\n".join(output_lines)
        else:
            raise ValueError(f"Unknown section: {section}")
    
    def view_all_agents(self, config_path: str) -> None:
        """View system prompts for all agents in the team.
        
        Args:
            config_path: Path to the team configuration file
        """
        team_config = self.load_team_config(config_path)
        
        if 'agents' not in team_config:
            self.console.print("[red]No agents found in team configuration[/red]")
            return
        
        self.console.print(f"\n[bold blue]Team Configuration: {config_path}[/bold blue]\n")
        
        for agent_config in team_config['agents']:
            agent_name = agent_config['name']
            
            try:
                prompt_info = self.view_agent_prompt(config_path, agent_name)
                
                # Create a panel for each agent
                panel = Panel(
                    prompt_info,
                    title=f"[bold green]{agent_name}[/bold green]",
                    border_style="blue",
                    expand=False
                )
                
                self.console.print(panel)
                self.console.print()  # Add spacing between agents
                
            except Exception as e:
                self.console.print(f"[red]Error viewing prompt for {agent_name}: {e}[/red]")
    
    def list_agents(self, config_path: str) -> None:
        """List all agents in the team configuration.
        
        Args:
            config_path: Path to the team configuration file
        """
        team_config = self.load_team_config(config_path)
        
        if 'agents' not in team_config:
            self.console.print("[red]No agents found in team configuration[/red]")
            return
        
        self.console.print(f"\n[bold blue]Available Agents in {config_path}:[/bold blue]\n")
        
        for agent_config in team_config['agents']:
            name = agent_config['name']
            is_orchestrator = agent_config.get('orchestrator', False)
            agent_tools = agent_config.get('tools', [])
            
            agent_type = "Orchestrator" if is_orchestrator else "Specialized Agent"
            tools_info = f" (Tools: {', '.join(agent_tools)})" if agent_tools else " (No tools)"
            
            self.console.print(f"  • [bold]{name}[/bold] - {agent_type}{tools_info}")
        
        self.console.print()
