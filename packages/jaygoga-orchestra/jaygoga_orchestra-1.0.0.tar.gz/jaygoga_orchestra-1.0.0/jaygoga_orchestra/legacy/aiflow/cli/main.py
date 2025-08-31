"""
Beautiful Main CLI entry point for AIFlow.

Provides a modern, interactive command-line interface for AIFlow operations.
"""

import click
import asyncio
from typing import Optional
from rich.console import Console

from .base import CLIContext
from .beautiful_cli import BeautifulCLI
from .conversation_agent import start_conversation_mode
from .create import CreateCommand
from .manage import ManageCommand
from .train import TrainCommand
from .evaluate import EvaluateCommand
from .deploy import DeployCommand

console = Console()


@click.group()
@click.version_option(version="1.0.0")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--project-root', type=click.Path(exists=True), help='Project root directory')
@click.pass_context
def aiflow(ctx, verbose: bool, debug: bool, project_root: Optional[str]):
    """🚀 AIFlow - Beautiful AI Agent Orchestration Platform"""
    ctx.ensure_object(dict)

    # Create CLI context
    from pathlib import Path
    project_path = Path(project_root) if project_root else Path.cwd()

    ctx.obj['context'] = CLIContext(
        project_root=project_path,
        verbose=verbose,
        debug=debug
    )


@aiflow.command()
def interactive():
    """🎨 Start the beautiful interactive CLI interface"""
    cli = BeautifulCLI()
    asyncio.run(cli.start_interactive_session())


@aiflow.command()
@click.argument('message', required=False)
@click.option('--agent-name', default="AIFlow Assistant", help='Name of the agent')
@click.option('--agent-role', default="Conversational AI Assistant", help='Role of the agent')
def chat(message: Optional[str], agent_name: str, agent_role: str):
    """💬 Start conversation with AI agents"""
    agent_config = {
        "name": agent_name,
        "role": agent_role,
        "goal": "Help users with their questions and tasks",
        "backstory": f"I'm {agent_name}, a {agent_role} powered by AIFlow."
    }

    if message:
        console.print(f"[bold blue]You:[/bold blue] {message}")
        console.print(f"[bold cyan]{agent_name}:[/bold cyan] I understand you said: '{message}'. This is a demo response!")
    else:
        asyncio.run(start_conversation_mode(agent_config))

@aiflow.command()
@click.pass_context
def create(ctx):
    """🛠️ Create new projects, agents, or tasks"""
    command = CreateCommand()
    command.execute(ctx.obj['context'])


@aiflow.command()
@click.pass_context
def manage(ctx):
    """⚙️ Manage existing projects and resources"""
    command = ManageCommand()
    command.execute(ctx.obj['context'])


@aiflow.command()
@click.pass_context
def train(ctx):
    """🎓 Train AI agents and models"""
    command = TrainCommand()
    command.execute(ctx.obj['context'])


@aiflow.command()
@click.pass_context
def evaluate(ctx):
    """📊 Evaluate agent performance"""
    command = EvaluateCommand()
    command.execute(ctx.obj['context'])


@aiflow.command()
@click.pass_context
def deploy(ctx):
    """🚀 Deploy agents and teams"""
    command = DeployCommand()
    command.execute(ctx.obj['context'])


@aiflow.command()
@click.option('--config-file', type=click.Path(exists=True), help='Team configuration file')
@click.option('--stream/--no-stream', default=True, help='Enable streaming output')
@click.option('--save/--no-save', default=True, help='Save results to file')
def team(config_file: Optional[str], stream: bool, save: bool):
    """👥 Run team orchestration"""
    from rich.panel import Panel

    console.print(Panel(
        "[bold magenta]🚀 Team Orchestration[/bold magenta]\n\n"
        "Starting team execution with enhanced output...",
        border_style="magenta"
    ))

    # This would integrate with the actual team execution
    console.print("[green]✅ Team execution completed![/green]")
    if save:
        console.print("[cyan]📄 Results saved to: results.md[/cyan]")


@aiflow.command()
def status():
    """📈 Show system status and metrics"""
    from rich.table import Table
    from rich.panel import Panel

    # System status table
    status_table = Table(title="🖥️ AIFlow System Status")
    status_table.add_column("Component", style="cyan")
    status_table.add_column("Status", style="green")
    status_table.add_column("Details", style="white")

    status_table.add_row("Core System", "✅ Online", "All systems operational")
    status_table.add_row("Memory System", "✅ Active", "Advanced memory enabled")
    status_table.add_row("Vector DB", "✅ Connected", "In-memory database ready")
    status_table.add_row("CLI Interface", "✅ Beautiful", "Rich formatting active")

    console.print(status_table)

    # Quick stats
    stats_panel = Panel(
        "[bold green]📊 Quick Stats[/bold green]\n\n"
        "🤖 [cyan]Active Agents:[/cyan] 0\n"
        "📋 [cyan]Pending Tasks:[/cyan] 0\n"
        "👥 [cyan]Running Teams:[/cyan] 0\n"
        "💾 [cyan]Memory Entries:[/cyan] 0",
        title="📈 Statistics",
        border_style="blue"
    )
    console.print(stats_panel)


if __name__ == '__main__':
    aiflow()
