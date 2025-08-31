"""
Beautiful CLI for AIFlow - Inspired by Govinda
A modern, interactive command-line interface for AI agent orchestration.
"""

import click
import asyncio
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from pathlib import Path
import json
import time
from datetime import datetime

from ..core.agent import Agent
from ..core.task import Task
from ..core.team import Team
from .base import CLIContext

console = Console()

# Beautiful ASCII Art Banner
AIFLOW_BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     █████╗ ██╗███████╗██╗      ██████╗ ██╗    ██╗            ║
║    ██╔══██╗██║██╔════╝██║     ██╔═══██╗██║    ██║            ║
║    ███████║██║█████╗  ██║     ██║   ██║██║ █╗ ██║            ║
║    ██╔══██║██║██╔══╝  ██║     ██║   ██║██║███╗██║            ║
║    ██║  ██║██║██║     ███████╗╚██████╔╝╚███╔███╔╝            ║
║    ╚═╝  ╚═╝╚═╝╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝             ║
║                                                               ║
║           🤖 AI Agent Orchestration Platform 🚀               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""

class BeautifulCLI:
    """Beautiful CLI interface for AIFlow."""
    
    def __init__(self):
        self.console = Console()
        self.context = None
        self.current_session = None
        
    def show_banner(self):
        """Display the beautiful AIFlow banner."""
        banner_text = Text(AIFLOW_BANNER, style="bold cyan")
        self.console.print(Align.center(banner_text))
        self.console.print()
        
    def show_welcome(self):
        """Show welcome message with available commands."""
        welcome_panel = Panel(
            "[bold green]Welcome to AIFlow![/bold green]\n\n"
            "🎯 [cyan]Available Commands:[/cyan]\n"
            "  • [yellow]chat[/yellow]     - Start interactive conversation with AI agents\n"
            "  • [yellow]task[/yellow]     - Create and manage tasks\n"
            "  • [yellow]team[/yellow]     - Orchestrate multiple agents\n"
            "  • [yellow]create[/yellow]   - Create new projects, agents, or tasks\n"
            "  • [yellow]status[/yellow]   - View system status and metrics\n"
            "  • [yellow]help[/yellow]     - Show detailed help\n"
            "  • [yellow]exit[/yellow]     - Exit AIFlow\n\n"
            "💡 [dim]Type a command to get started![/dim]",
            title="🚀 AIFlow Command Center",
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(welcome_panel)
        self.console.print()

    async def start_interactive_session(self):
        """Start the main interactive CLI session."""
        self.show_banner()
        self.show_welcome()
        
        while True:
            try:
                # Beautiful prompt
                command = Prompt.ask(
                    "[bold cyan]aiflow[/bold cyan] [dim]>[/dim]",
                    default="help"
                )
                
                if command.lower() in ['exit', 'quit', 'bye']:
                    self.show_goodbye()
                    break
                    
                await self.handle_command(command)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' to quit gracefully.[/yellow]")
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

    async def handle_command(self, command: str):
        """Handle user commands with beautiful output."""
        parts = command.strip().split()
        if not parts:
            return
            
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == "chat":
            await self.start_chat_session(args)
        elif cmd == "task":
            await self.handle_task_command(args)
        elif cmd == "team":
            await self.handle_team_command(args)
        elif cmd == "create":
            await self.handle_create_command(args)
        elif cmd == "status":
            await self.show_status()
        elif cmd == "help":
            self.show_help(args)
        else:
            self.console.print(f"[red]Unknown command: {cmd}[/red]")
            self.console.print("[dim]Type 'help' for available commands.[/dim]")

    async def start_chat_session(self, args: List[str]):
        """Start an interactive chat session with AI agents."""
        self.console.print(Panel(
            "[bold green]🤖 Starting AI Chat Session[/bold green]\n\n"
            "You can now chat with AI agents. Type your message and press Enter.\n"
            "Commands: [yellow]/exit[/yellow] to end, [yellow]/clear[/yellow] to clear history",
            title="💬 Chat Mode",
            border_style="green"
        ))
        
        # Create a simple agent for demonstration
        agent = Agent(
            name="AIFlow Assistant",
            role="Helpful AI Assistant",
            goal="Assist users with their questions and tasks",
            backstory="I'm an AI assistant built with AIFlow to help you accomplish your goals."
        )
        
        chat_history = []
        
        while True:
            try:
                user_input = Prompt.ask("[bold blue]You[/bold blue]")
                
                if user_input.lower() in ['/exit', '/quit']:
                    break
                elif user_input.lower() == '/clear':
                    chat_history.clear()
                    self.console.clear()
                    continue
                
                # Show thinking animation
                with self.console.status("[bold green]AI is thinking...", spinner="dots"):
                    # Simulate AI response (replace with actual agent call)
                    await asyncio.sleep(1)
                    response = f"I understand you said: '{user_input}'. This is a demo response from AIFlow!"
                
                # Display response beautifully
                response_panel = Panel(
                    response,
                    title="🤖 AIFlow Assistant",
                    border_style="cyan",
                    padding=(1, 2)
                )
                self.console.print(response_panel)
                
                chat_history.append({"user": user_input, "assistant": response})
                
            except KeyboardInterrupt:
                break
        
        self.console.print("[green]Chat session ended.[/green]")

    async def handle_task_command(self, args: List[str]):
        """Handle task-related commands."""
        if not args:
            self.show_task_help()
            return
            
        subcommand = args[0].lower()
        
        if subcommand == "create":
            await self.create_task_interactive()
        elif subcommand == "list":
            await self.list_tasks()
        elif subcommand == "run":
            task_id = args[1] if len(args) > 1 else None
            await self.run_task(task_id)
        else:
            self.console.print(f"[red]Unknown task command: {subcommand}[/red]")

    async def create_task_interactive(self):
        """Interactive task creation with beautiful prompts."""
        self.console.print(Panel(
            "[bold cyan]📋 Task Creation Wizard[/bold cyan]\n\n"
            "Let's create a new task step by step!",
            border_style="cyan"
        ))
        
        # Collect task details
        description = Prompt.ask("[bold]Task Description[/bold]")
        expected_output = Prompt.ask("[bold]Expected Output[/bold]")
        agent_name = Prompt.ask("[bold]Agent Name[/bold]", default="Default Agent")
        
        # Create task
        task_data = {
            "description": description,
            "expected_output": expected_output,
            "agent_name": agent_name,
            "created_at": datetime.now().isoformat()
        }
        
        # Show task summary
        task_table = Table(title="📋 Task Summary")
        task_table.add_column("Property", style="cyan")
        task_table.add_column("Value", style="green")
        
        task_table.add_row("Description", description)
        task_table.add_row("Expected Output", expected_output)
        task_table.add_row("Agent", agent_name)
        task_table.add_row("Created", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        self.console.print(task_table)
        
        if Confirm.ask("[bold]Create this task?[/bold]"):
            # Save task (implement actual saving logic)
            self.console.print("[green]✅ Task created successfully![/green]")
        else:
            self.console.print("[yellow]Task creation cancelled.[/yellow]")

    async def handle_team_command(self, args: List[str]):
        """Handle team orchestration commands."""
        if not args:
            self.show_team_help()
            return
            
        subcommand = args[0].lower()
        
        if subcommand == "run":
            await self.run_team_interactive()
        elif subcommand == "create":
            await self.create_team_interactive()
        elif subcommand == "status":
            await self.show_team_status()
        else:
            self.console.print(f"[red]Unknown team command: {subcommand}[/red]")

    async def run_team_interactive(self):
        """Run a team with beautiful progress tracking."""
        self.console.print(Panel(
            "[bold magenta]🚀 Team Execution[/bold magenta]\n\n"
            "Starting team orchestration...",
            border_style="magenta"
        ))
        
        # Create progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            # Simulate team execution steps
            task1 = progress.add_task("[cyan]Initializing agents...", total=100)
            task2 = progress.add_task("[green]Executing tasks...", total=100)
            task3 = progress.add_task("[yellow]Generating results...", total=100)
            
            # Simulate progress
            for i in range(100):
                await asyncio.sleep(0.02)
                progress.update(task1, advance=1)
                if i > 30:
                    progress.update(task2, advance=1)
                if i > 60:
                    progress.update(task3, advance=1)
        
        # Show completion
        self.console.print(Panel(
            "[bold green]✅ Team execution completed successfully![/bold green]\n\n"
            "📄 Results saved to: [cyan]results.md[/cyan]\n"
            "📊 Performance report: [cyan]team_performance.json[/cyan]",
            title="🎉 Success",
            border_style="green"
        ))

    def show_help(self, args: List[str]):
        """Show beautiful help information."""
        if not args:
            help_table = Table(title="🔧 AIFlow Commands")
            help_table.add_column("Command", style="cyan", width=12)
            help_table.add_column("Description", style="white")
            help_table.add_column("Example", style="dim")
            
            help_table.add_row("chat", "Interactive AI conversation", "chat")
            help_table.add_row("task create", "Create a new task", "task create")
            help_table.add_row("task run", "Execute a task", "task run <id>")
            help_table.add_row("team run", "Run team orchestration", "team run")
            help_table.add_row("create", "Create projects/agents", "create project")
            help_table.add_row("status", "Show system status", "status")
            
            self.console.print(help_table)
        else:
            # Show specific help for commands
            command = args[0].lower()
            if command == "chat":
                self.console.print(Panel(
                    "[bold cyan]💬 Chat Command Help[/bold cyan]\n\n"
                    "Start an interactive conversation with AI agents.\n\n"
                    "[yellow]Usage:[/yellow] chat\n"
                    "[yellow]In chat:[/yellow]\n"
                    "  • Type your message and press Enter\n"
                    "  • /exit - End chat session\n"
                    "  • /clear - Clear chat history",
                    border_style="cyan"
                ))

    def show_goodbye(self):
        """Show beautiful goodbye message."""
        goodbye_panel = Panel(
            "[bold green]Thank you for using AIFlow![/bold green]\n\n"
            "🚀 Keep building amazing AI agents!\n"
            "💫 Visit us at: [link]https://github.com/aiflow[/link]\n\n"
            "[dim]See you next time! 👋[/dim]",
            title="👋 Goodbye",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(Align.center(goodbye_panel))

    def show_task_help(self):
        """Show task command help."""
        task_table = Table(title="📋 Task Commands")
        task_table.add_column("Command", style="cyan")
        task_table.add_column("Description", style="white")
        
        task_table.add_row("task create", "Create a new task interactively")
        task_table.add_row("task list", "List all tasks")
        task_table.add_row("task run <id>", "Execute a specific task")
        
        self.console.print(task_table)

    def show_team_help(self):
        """Show team command help."""
        team_table = Table(title="👥 Team Commands")
        team_table.add_column("Command", style="cyan")
        team_table.add_column("Description", style="white")
        
        team_table.add_row("team create", "Create a new team")
        team_table.add_row("team run", "Execute team orchestration")
        team_table.add_row("team status", "Show team status")
        
        self.console.print(team_table)

    async def show_status(self):
        """Show beautiful system status."""
        status_layout = Layout()
        
        # Create status panels
        system_panel = Panel(
            "[green]✅ System Online[/green]\n"
            "[cyan]🤖 Agents: 3 active[/cyan]\n"
            "[yellow]📋 Tasks: 5 pending[/yellow]\n"
            "[magenta]👥 Teams: 1 running[/magenta]",
            title="🖥️ System Status",
            border_style="green"
        )
        
        self.console.print(system_panel)


# CLI Entry Points
@click.group()
@click.version_option(version="1.0.0")
def aiflow():
    """🚀 AIFlow - Beautiful AI Agent Orchestration Platform"""
    pass

@aiflow.command()
def interactive():
    """Start the beautiful interactive CLI"""
    cli = BeautifulCLI()
    asyncio.run(cli.start_interactive_session())

@aiflow.command()
@click.argument('message', required=False)
def chat(message):
    """Quick chat with AI agents"""
    cli = BeautifulCLI()
    if message:
        console.print(f"[bold blue]You:[/bold blue] {message}")
        console.print(Panel(
            f"I understand you said: '{message}'. This is a demo response!",
            title="🤖 AIFlow Assistant",
            border_style="cyan"
        ))
    else:
        asyncio.run(cli.start_chat_session([]))

if __name__ == "__main__":
    aiflow()
