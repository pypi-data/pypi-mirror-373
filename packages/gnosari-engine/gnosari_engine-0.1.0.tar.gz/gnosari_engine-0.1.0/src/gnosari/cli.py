from __future__ import annotations

# Suppress warnings before any imports
import warnings
import os
warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", message=".*deprecated.*")
warnings.filterwarnings("ignore", message=".*Support for class-based.*")
os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning"

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import NoReturn
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.syntax import Syntax

from .engine.team_builder import TeamBuilder
from .engine.team_runner import TeamRunner


async def run_single_agent_stream(executor: TeamRunner, agent_name: str, message: str, debug: bool = False):
    """Run single agent with streaming response using Rich console and provide execution summary."""
    console = Console()
    
    # Track execution steps for final summary
    execution_steps = []
    tools_used = set()
    final_response = ""
    current_agent_response = ""
    
    def add_step(step_type: str, details: str, timestamp: str = None):
        """Add a step to the execution tracking."""
        if timestamp is None:
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        execution_steps.append({
            "timestamp": timestamp,
            "type": step_type,
            "agent": agent_name,
            "details": details
        })
    
    # Clear screen and show header
    console.clear()
    console.print("🚀 [bold blue]GNOSARI SINGLE AGENT EXECUTION[/bold blue]", style="bold")
    console.print("=" * 80, style="dim")
    console.print(f"🤖 [blue]Agent:[/blue] {agent_name}")
    console.print(f"📝 [blue]Message:[/blue] {message}")
    console.print("=" * 80, style="dim")
    console.print()
    
    # Suppress ChromaDB warnings during execution
    import warnings
    warnings.filterwarnings("ignore", message=".*Add of existing embedding ID.*")
    warnings.filterwarnings("ignore", message=".*Accessing the 'model_fields' attribute.*")
    
    if debug:
        # For debug mode, print raw JSON output and formatted messages
        console.print("🐛 [bold red]DEBUG MODE[/bold red]", style="bold")
        console.print("─" * 80, style="dim")
        
        event_count = 0
        async for output in executor.run_single_agent_stream(agent_name, message, debug):
            event_count += 1
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            
            # Print event header
            console.print(f"\n📡 [bold cyan]EVENT #{event_count}[/bold cyan]", style="bold")
            console.print(f"⏰ [dim]{timestamp}[/dim]")
            
            # Print raw JSON for debugging
            json_output = json.dumps(output, indent=2, default=str)
            syntax = Syntax(json_output, "json", theme="monokai", line_numbers=False)
            console.print(syntax)
            
            # Show formatted output for readability
            event_type = output.get("type", "unknown")
            
            if event_type == "response":
                content = output.get('content', '')
                console.print(f"💬 [bold green]RESPONSE[/bold green] from [bold]{agent_name}[/bold]: [green]{content}[/green]")
                current_agent_response += content
                if not hasattr(console, '_response_started'):
                    add_step("response", f"Started generating response", timestamp)
                    console._response_started = True
            elif event_type == "tool_call":
                tool_name = output.get("tool_name", output.get("name", "unknown"))
                tool_input = output.get("tool_input", output.get("input", {}))
                console.print(f"🔧 [bold yellow]TOOL CALL[/bold yellow] by [bold]{agent_name}[/bold]: [yellow]{tool_name}[/yellow]")
                console.print(f"📥 Input: [dim]{tool_input}[/dim]")
                add_step("tool_call", f"Called tool: {tool_name}", timestamp)
                tools_used.add(tool_name)
            elif event_type == "tool_result":
                content = output.get('content', '')
                preview = content[:200] + "..." if len(str(content)) > 200 else content
                console.print(f"🔨 [bold cyan]TOOL RESULT[/bold cyan] for [bold]{agent_name}[/bold]: [cyan]{preview}[/cyan]")
                add_step("tool_result", f"Tool result: {preview}", timestamp)
            elif event_type == "completion":
                content = output.get('content', '')
                console.print(f"✅ [bold green]COMPLETION[/bold green] from [bold]{agent_name}[/bold]: [green]{content}[/green]")
                add_step("completion", f"Completed execution", timestamp)
                final_response = current_agent_response
            elif event_type == "error":
                content = output.get('content', '')
                console.print(f"❌ [bold red]ERROR[/bold red]: [red]{content}[/red]")
                return
            elif output.get("is_done"):
                console.print(f"🎯 [bold green]DONE![/bold green] Agent execution completed.")
                break
            
            console.print("─" * 80, style="dim")
    else:
        # Use Live display for streaming response
        console.print("📡 [bold cyan]STREAMING RESPONSE[/bold cyan]", style="bold")
        console.print("─" * 80, style="dim")
        
        with Live("", refresh_per_second=10, auto_refresh=True) as live:
            live.update(Text.assemble(("⏳ Initializing...", "dim")))
            current_response = ""
            event_count = 0
            
            # Suppress logging during streaming
            import logging
            logging.getLogger().setLevel(logging.ERROR)
            
            async for output in executor.run_single_agent_stream(agent_name, message, debug):
                event_count += 1
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                event_type = output.get("type", "unknown")
                
                # Handle different output types
                if event_type == "response":
                    content = output.get("content", "")
                    current_response += content
                    current_agent_response += content
                    display_text = Text.assemble(
                        (f"[{agent_name}] ", "bold blue"), 
                        (current_response, "green")
                    )
                    live.update(display_text)
                    if not hasattr(live, '_response_started'):
                        add_step("response", f"Started generating response", timestamp)
                        live._response_started = True
                elif event_type == "tool_call":
                    tool_name = output.get("tool_name", output.get("name", "unknown"))
                    display_text = Text.assemble(
                        (f"[{agent_name}] ", "bold blue"),
                        (f"🔧 Calling {tool_name}...", "yellow")
                    )
                    live.update(display_text)
                    add_step("tool_call", f"Called tool: {tool_name}", timestamp)
                    tools_used.add(tool_name)
                elif event_type == "tool_result":
                    display_text = Text.assemble(
                        (f"[{agent_name}] ", "bold blue"),
                        ("🔨 Tool completed", "cyan")
                    )
                    live.update(display_text)
                    add_step("tool_result", "Tool execution completed", timestamp)
                elif event_type == "completion":
                    current_response = output.get("content", "")
                    display_text = Text.assemble(
                        (f"[{agent_name}] ", "bold blue"), 
                        (current_response, "green")
                    )
                    live.update(display_text)
                    add_step("completion", "Completed execution", timestamp)
                    final_response = current_agent_response
                elif event_type == "error":
                    content = output.get('content', '')
                    display_text = Text.assemble(
                        (f"[{agent_name}] ", "bold red"),
                        (f"❌ Error: {content}", "red")
                    )
                    live.update(display_text)
                    return
                elif output.get("is_done"):
                    break
    
    # Print final newline after streaming
    console.print()
    
    # Print execution summary
    console.print("\n" + "="*80)
    console.print("🎯 [bold cyan]EXECUTION SUMMARY[/bold cyan]")
    console.print("="*80)
    
    # Summary statistics
    console.print(f"📊 [bold]Statistics:[/bold]")
    console.print(f"   • Total steps: {len(execution_steps)}")
    console.print(f"   • Agent: {agent_name}")
    console.print(f"   • Tools used: {len(tools_used)} ({', '.join(sorted(tools_used)) if tools_used else 'None'})")
    
    # Execution timeline
    console.print(f"\n⏱️  [bold]Execution Timeline:[/bold]")
    for i, step in enumerate(execution_steps, 1):
        step_type_emoji = {
            "response": "💬",
            "tool_call": "🔧", 
            "tool_result": "🔨",
            "completion": "✅"
        }.get(step["type"], "📝")
        
        console.print(f"   {i:2d}. [{step['timestamp']}] {step_type_emoji} {step['agent']}: {step['details']}")
    
    # Final response
    if final_response:
        console.print(f"\n💬 [bold]Final Response:[/bold]")
        console.print(f"   {final_response}")
    
    console.print("="*80)


async def run_team_stream(executor: TeamRunner, message: str, debug: bool = False):
    """Run team with streaming response using Rich console and provide execution summary."""
    console = Console()
    
    # Track execution steps for final summary
    execution_steps = []
    agents_involved = set()
    tools_used = set()
    handoffs = []
    final_response = ""
    current_agent_response = ""
    
    def add_step(step_type: str, agent: str, details: str, timestamp: str = None):
        """Add a step to the execution tracking."""
        if timestamp is None:
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        execution_steps.append({
            "timestamp": timestamp,
            "type": step_type,
            "agent": agent,
            "details": details
        })
        agents_involved.add(agent)
    
    # Clear screen and show header
    console.clear()
    console.print("🚀 [bold blue]GNOSARI TEAM EXECUTION[/bold blue]", style="bold")
    console.print("=" * 80, style="dim")
    console.print(f"📝 [blue]Message:[/blue] {message}")
    console.print("=" * 80, style="dim")
    console.print()
    
    # Suppress ChromaDB warnings during execution
    import warnings
    warnings.filterwarnings("ignore", message=".*Add of existing embedding ID.*")
    warnings.filterwarnings("ignore", message=".*Accessing the 'model_fields' attribute.*")
    
    if debug:
        # For debug mode, print raw JSON output and formatted messages
        console.print("🐛 [bold red]DEBUG MODE[/bold red]", style="bold")
        console.print("─" * 80, style="dim")
        
        event_count = 0
        async for output in executor.run_team_stream(message, debug):
            event_count += 1
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            
            # Print event header
            console.print(f"\n📡 [bold cyan]EVENT #{event_count}[/bold cyan]", style="bold")
            console.print(f"⏰ [dim]{timestamp}[/dim]")
            
            # Print raw JSON for debugging (like WebSocket)
            json_output = json.dumps(output, indent=2, default=str)
            syntax = Syntax(json_output, "json", theme="monokai", line_numbers=False)
            console.print(syntax)
            
            # Show formatted output for readability
            event_type = output.get("type", "unknown")
            agent_name = output.get("agent_name", "Unknown Agent")
            
            if event_type == "response":
                content = output.get('content', '')
                console.print(f"💬 [bold green]RESPONSE[/bold green] from [bold]{agent_name}[/bold]: [green]{content}[/green]")
                current_agent_response += content  # Track actual response content
                # Only add step for first response chunk to avoid spam
                if not hasattr(console, '_response_started'):
                    add_step("response", agent_name, f"Started generating response", timestamp)
                    console._response_started = True
            elif event_type == "tool_call":
                tool_name = output.get("tool_name", output.get("name", "unknown"))
                tool_input = output.get("tool_input", output.get("input", {}))
                console.print(f"🔧 [bold yellow]TOOL CALL[/bold yellow] by [bold]{agent_name}[/bold]: [yellow]{tool_name}[/yellow]")
                console.print(f"📥 Input: [dim]{tool_input}[/dim]")
                add_step("tool_call", agent_name, f"Called tool: {tool_name}", timestamp)
                tools_used.add(tool_name)
            elif event_type == "tool_result":
                content = output.get('content', '')
                preview = content[:200] + "..." if len(str(content)) > 200 else content
                console.print(f"🔨 [bold cyan]TOOL RESULT[/bold cyan] for [bold]{agent_name}[/bold]: [cyan]{preview}[/cyan]")
                add_step("tool_result", agent_name, f"Tool result: {preview}", timestamp)
            elif event_type == "completion":
                content = output.get('content', '')
                console.print(f"✅ [bold green]COMPLETION[/bold green] from [bold]{agent_name}[/bold]: [green]{content}[/green]")
                add_step("completion", agent_name, f"Completed execution", timestamp)
                final_response = current_agent_response  # Use actual response content, not completion message
                # Reset response tracking for next agent
                if hasattr(console, '_response_started'):
                    delattr(console, '_response_started')
                current_agent_response = ""  # Reset for next agent
            elif event_type == "handoff":
                target_agent = output.get("agent_name", "Unknown")
                escalation_data = output.get("escalation")
                
                if escalation_data:
                    reason = escalation_data.get("reason", "Unknown")
                    from_agent = escalation_data.get("from_agent", "Unknown")
                    context = escalation_data.get("context")
                    
                    console.print(f"🤝 [bold magenta]HANDOFF ESCALATION[/bold magenta]")
                    console.print(f"   📤 From: [bold]{from_agent}[/bold]")
                    console.print(f"   📥 To: [bold]{target_agent}[/bold]")
                    console.print(f"   📋 Reason: [yellow]{reason}[/yellow]")
                    if context:
                        console.print(f"   📝 Context: [dim]{context}[/dim]")
                    
                    handoffs.append({
                        "from": from_agent,
                        "to": target_agent,
                        "reason": reason,
                        "context": context
                    })
                    add_step("handoff", from_agent, f"Handed off to {target_agent} (Reason: {reason})", timestamp)
                    # Reset response tracking for new agent
                    if hasattr(console, '_response_started'):
                        delattr(console, '_response_started')
                    current_agent_response = ""  # Reset for next agent
                else:
                    console.print(f"🤝 [bold magenta]HANDOFF[/bold magenta] to [bold]{target_agent}[/bold]")
                    add_step("handoff", agent_name, f"Handed off to {target_agent}", timestamp)
                    # Reset response tracking for new agent
                    if hasattr(console, '_response_started'):
                        delattr(console, '_response_started')
                    current_agent_response = ""  # Reset for next agent
            elif output.get("is_done"):
                console.print(f"🎯 [bold green]DONE![/bold green] Final response completed.")
                break
            
            console.print("─" * 80, style="dim")
    else:
        # Use Live display to show streaming response with better formatting
        console.print("📡 [bold cyan]STREAMING EVENTS[/bold cyan]", style="bold")
        console.print("─" * 80, style="dim")
        
        with Live("", refresh_per_second=10, auto_refresh=True) as live:
            # Show initial status
            live.update(Text.assemble(("⏳ Initializing...", "dim")))
            current_response = ""
            current_agent = "Team"
            event_count = 0
            
            # Suppress logging during streaming
            import logging
            logging.getLogger().setLevel(logging.ERROR)
            
            async for output in executor.run_team_stream(message, debug):
                event_count += 1
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                event_type = output.get("type", "unknown")
                agent_name = output.get("agent_name", current_agent)
                
                # Update current agent if it changed
                if agent_name != current_agent:
                    current_agent = agent_name
                
                # Handle different output types
                if event_type == "response":
                    content = output.get("content", "")
                    current_response += content
                    current_agent_response += content  # Track actual response content
                    display_text = Text.assemble(
                        (f"[{current_agent}] ", "bold blue"), 
                        (current_response, "green")
                    )
                    live.update(display_text)
                    # Only add step for first response chunk to avoid spam
                    if not hasattr(live, '_response_started'):
                        add_step("response", agent_name, f"Started generating response", timestamp)
                        live._response_started = True
                elif event_type == "tool_call":
                    tool_name = output.get("tool_name", output.get("name", "unknown"))
                    display_text = Text.assemble(
                        (f"[{current_agent}] ", "bold blue"),
                        (f"🔧 Calling {tool_name}...", "yellow")
                    )
                    live.update(display_text)
                    add_step("tool_call", agent_name, f"Called tool: {tool_name}", timestamp)
                    tools_used.add(tool_name)
                elif event_type == "tool_result":
                    display_text = Text.assemble(
                        (f"[{current_agent}] ", "bold blue"),
                        ("🔨 Tool completed", "cyan")
                    )
                    live.update(display_text)
                    add_step("tool_result", agent_name, "Tool execution completed", timestamp)
                elif event_type == "completion":
                    current_response = output.get("content", "")
                    display_text = Text.assemble(
                        (f"[{current_agent}] ", "bold blue"), 
                        (current_response, "green")
                    )
                    live.update(display_text)
                    add_step("completion", agent_name, "Completed execution", timestamp)
                    final_response = current_agent_response  # Use actual response content, not completion message
                    # Reset response tracking for next agent
                    if hasattr(live, '_response_started'):
                        delattr(live, '_response_started')
                    current_agent_response = ""  # Reset for next agent
                elif event_type == "handoff":
                    target_agent = output.get("agent_name", "Unknown")
                    escalation_data = output.get("escalation")
                    
                    if escalation_data:
                        reason = escalation_data.get("reason", "Unknown")
                        display_text = Text.assemble(
                            (f"[{current_agent}] ", "bold blue"),
                            (f"🤝 Escalating to {target_agent} ({reason})...", "magenta")
                        )
                        handoffs.append({
                            "from": escalation_data.get("from_agent", current_agent),
                            "to": target_agent,
                            "reason": reason,
                            "context": escalation_data.get("context")
                        })
                        add_step("handoff", current_agent, f"Handed off to {target_agent} (Reason: {reason})", timestamp)
                    else:
                        display_text = Text.assemble(
                            (f"[{current_agent}] ", "bold blue"),
                            (f"🤝 Handing off to {target_agent}...", "magenta")
                        )
                        add_step("handoff", current_agent, f"Handed off to {target_agent}", timestamp)
                    live.update(display_text)
                    # Reset response tracking for new agent
                    if hasattr(live, '_response_started'):
                        delattr(live, '_response_started')
                    current_agent_response = ""  # Reset for next agent
                elif output.get("is_done"):
                    break
    
    # Print final newline after streaming
    console.print()
    
    # Print execution summary
    console.print("\n" + "="*80)
    console.print("🎯 [bold cyan]EXECUTION SUMMARY[/bold cyan]")
    console.print("="*80)
    
    # Summary statistics
    console.print(f"📊 [bold]Statistics:[/bold]")
    console.print(f"   • Total steps: {len(execution_steps)}")
    console.print(f"   • Agents involved: {len(agents_involved)} ({', '.join(sorted(agents_involved))})")
    console.print(f"   • Tools used: {len(tools_used)} ({', '.join(sorted(tools_used)) if tools_used else 'None'})")
    console.print(f"   • Handoffs: {len(handoffs)}")
    
    # Execution timeline
    console.print(f"\n⏱️  [bold]Execution Timeline:[/bold]")
    for i, step in enumerate(execution_steps, 1):
        step_type_emoji = {
            "response": "💬",
            "tool_call": "🔧", 
            "tool_result": "🔨",
            "completion": "✅",
            "handoff": "🤝"
        }.get(step["type"], "📝")
        
        console.print(f"   {i:2d}. [{step['timestamp']}] {step_type_emoji} {step['agent']}: {step['details']}")
    
    # Handoff details
    if handoffs:
        console.print(f"\n🤝 [bold]Handoff Details:[/bold]")
        for i, handoff in enumerate(handoffs, 1):
            console.print(f"   {i}. {handoff['from']} → {handoff['to']}")
            console.print(f"      Reason: {handoff['reason']}")
            if handoff.get('context'):
                console.print(f"      Context: {handoff['context'][:100]}...")
    
    # Final response
    if final_response:
        console.print(f"\n💬 [bold]Final Response:[/bold]")
        console.print(f"   {final_response}")
    
    console.print("="*80)


def setup_logging():
    """Setup logging configuration based on environment variables."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True  # Force reconfiguration even if logging was already configured
    )
    
    # Also set the level for specific loggers that might be created before basicConfig
    logging.getLogger().setLevel(getattr(logging, log_level, logging.INFO))
    
    # Ensure gnosari loggers use the configured level
    for logger_name in ['gnosari', 'gnosari.agents', 'gnosari.tools', 'gnosari.engine']:
        logging.getLogger(logger_name).setLevel(getattr(logging, log_level, logging.INFO))


def load_environment():
    """Load environment variables from .env file if it exists."""
    # Look for .env file in current directory and parent directories
    current_dir = Path.cwd()
    env_file = None
    
    # Check current directory and up to 3 parent directories
    for i in range(4):
        check_dir = current_dir / ("../" * i) if i > 0 else current_dir
        potential_env = check_dir / ".env"
        if potential_env.exists():
            env_file = potential_env
            break
    
    if env_file:
        print(f"Loading environment from: {env_file}")
        load_dotenv(env_file)
    else:
        # Try to load from current directory anyway (python-dotenv will handle it gracefully)
        load_dotenv()


def main() -> NoReturn:
    """Entrypoint for the gnosari CLI."""
    # Load environment variables from .env file
    load_environment()
    
    # Setup logging
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Gnosari Teams - Multi-Agent AI Team Runner",
        epilog="Use 'gnosari --help' for more information."
    )
    
    # Main arguments for team run
    parser.add_argument("--config", "-c", required=True, help="Path to team configuration YAML file")
    parser.add_argument("--message", "-m", required=True, help="Message to send to the team")
    parser.add_argument("--agent", "-a", help="Run only a specific agent from the team (by name)")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4o"), help="Model to use (default: gpt-4o)")
    parser.add_argument("--temperature", type=float, default=float(os.getenv("OPENAI_TEMPERATURE", "1")), help="Model temperature (default: 1.0)")
    parser.add_argument("--stream", action="store_true", help="Stream the response in real-time")
    parser.add_argument("--debug", action="store_true", help="Show debug information with raw JSON output")
    
    args = parser.parse_args()
    
    # Get API key from args or environment
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key is required. Set it with --api-key, OPENAI_API_KEY environment variable, or in .env file.")
        sys.exit(1)
    
    # Create OpenAI team orchestrator and run team
    async def run_team_async():
        try:
            builder = TeamBuilder(
                api_key=api_key,
                model=args.model,
                temperature=args.temperature
            )
            
            # Build the team
            print(f"Building team from configuration: {args.config}")
            team = await builder.build_team(args.config, debug=args.debug)
            print(f"Team built successfully with {len(team.all_agents)} agents:")
            for name in team.list_agents():
                agent = team.get_agent(name)
                if agent and hasattr(agent, 'model'):
                    model = agent.model
                    print(f"  - {name} (Model: {model})")
                else:
                    print(f"  - {name}")
            
            # Create executor and execute
            runner = TeamRunner(team)
            
            if args.agent:
                # Validate agent exists
                target_agent = team.get_agent(args.agent)
                if not target_agent:
                    available_agents = ", ".join(team.list_agents())
                    print(f"Error: Agent '{args.agent}' not found in team configuration.")
                    print(f"Available agents: {available_agents}")
                    sys.exit(1)
                
                # Run single agent
                if args.stream:
                    print(f"\nRunning agent '{args.agent}' with streaming...")
                    await run_single_agent_stream(runner, args.agent, args.message, args.debug)
                else:
                    print(f"\nRunning agent '{args.agent}' with message: {args.message}")
                    result = await runner.run_agent_until_done_async(
                        target_agent, args.message
                    )
                    
                    # Extract and display response
                    if isinstance(result, dict) and "outputs" in result:
                        for output in result["outputs"]:
                            if output.get("type") == "completion":
                                print(f"\nAgent Response:")
                                print(output.get("content", ""))
                                break
                    else:
                        print(f"Unexpected result format: {type(result)}")
                        print(result)
            elif args.stream:
                # Run with streaming
                print(f"\nRunning team with streaming...")
                await run_team_stream(runner, args.message, args.debug)
            else:
                # Run without streaming
                print(f"\nRunning team with message: {args.message}")
                result = await runner.run_team_async(args.message, args.debug)
                print(f"\nTeam Response:")
                
                # Extract response content from OpenAI Runner result
                if hasattr(result, 'final_output'):
                    print(result.final_output)
                elif isinstance(result, dict) and "outputs" in result:
                    response_content = ""
                    
                    for output in result["outputs"]:
                        if output.get("type") == "completion":
                            response_content = output.get("content", "")
                            break
                    
                    if response_content:
                        print(response_content)
                    else:
                        print("No response content found")
                else:
                    print(f"Unexpected result format: {type(result)}")
                    print(result)
                
        except Exception as e:
            print(f"Error running team: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    # Run the async function
    asyncio.run(run_team_async())
    
    raise SystemExit(0)