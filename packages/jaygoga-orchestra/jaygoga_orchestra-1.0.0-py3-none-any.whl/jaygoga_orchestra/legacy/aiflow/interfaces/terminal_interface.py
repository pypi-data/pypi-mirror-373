"""
Real terminal interface for AIFlow using Rich library.

Provides Govinda-style terminal display with live updates and progress tracking.
"""

import asyncio
import threading
from typing import List, Dict, Optional, Callable
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID, BarColumn, TextColumn, TimeRemainingColumn
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.prompt import Prompt

from ..core.agent import Agent
from ..core.task import Task


class TerminalInterface:
    """
    Real terminal interface using Rich library for beautiful displays.
    
    Provides Govinda-style visual interface with live updates, progress bars,
    agent status monitoring, human intervention, and work log saving.
    """
    
    def __init__(
        self,
        team_name: str,
        agents: List[Agent],
        tasks: List[Task],
        save_work_log: bool = False,
        work_log_path: Optional[str] = None
    ):
        """Initialize terminal interface."""
        self.team_name = team_name
        self.agents = {agent.id: agent for agent in agents}
        self.tasks = {task.id: task for task in tasks}
        
        # Work log configuration
        self.save_work_log = save_work_log
        self.work_log_path = work_log_path or f"work_log_{team_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        self.work_log_content: List[str] = []
        
        # Rich components
        self.console = Console()
        self.live = None
        self.progress = Progress(
            TextColumn("[bold blue]{task.description}", justify="left"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            TimeRemainingColumn(),
            console=self.console
        )
        
        # Progress tracking
        self.task_progress: Dict[str, TaskID] = {}
        self.agent_status: Dict[str, str] = {aid: "idle" for aid in self.agents.keys()}
        self.streaming_content: Dict[str, str] = {aid: "" for aid in self.agents.keys()}
        self.agent_outputs: Dict[str, List[str]] = {aid: [] for aid in self.agents.keys()}
        self.conversation_log: List[Dict] = []
        self.agent_conversations: List[Dict] = []
        
        # Human intervention
        self.human_input_enabled = True
        self.pending_human_input: Optional[str] = None
        self.input_thread: Optional[threading.Thread] = None
        self.stop_input_monitoring = False
        
        # Display state
        self.start_time = datetime.now()
        self.is_running = False
        self.current_active_agent: Optional[str] = None
    
    async def start(self):
        """Start the terminal interface."""
        self.is_running = True
        self.start_time = datetime.now()
        
        # Initialize work log
        if self.save_work_log:
            await self._initialize_work_log()
        
        # Initialize progress bars for tasks
        for task_id, task in self.tasks.items():
            progress_id = self.progress.add_task(
                description=f"{task.agent.name}: {task.description[:40]}...",
                total=100
            )
            self.task_progress[task_id] = progress_id
        
        # Start human input monitoring
        self._start_input_monitoring()
        
        # Start live display
        layout = self._create_layout()
        self.live = Live(layout, console=self.console, refresh_per_second=10)
        self.live.start()
        
        # Display initial header
        self._display_header()
    
    async def stop(self):
        """Stop the terminal interface."""
        self.is_running = False
        self.stop_input_monitoring = True
        
        if self.live:
            self.live.stop()
        
        # Stop input monitoring
        if self.input_thread and self.input_thread.is_alive():
            self.input_thread.join(timeout=1)
        
        # Save final work log
        if self.save_work_log:
            await self._finalize_work_log()
        
        # Display final summary
        self._display_summary()
    
    async def update_task_status(self, task: Task, status: str):
        """Update task status in the display."""
        if task.id in self.task_progress:
            progress_id = self.task_progress[task.id]
            if status == "running":
                self.progress.update(progress_id, advance=10)
            elif status == "completed":
                self.progress.update(progress_id, completed=100)
            elif status == "failed":
                self.progress.update(progress_id, completed=100, description=f"❌ {task.description[:40]}...")
    
    async def stream_update(self, agent_id: str, chunk: str):
        """Update streaming content for an agent."""
        if agent_id not in self.streaming_content:
            self.streaming_content[agent_id] = ""
        
        self.streaming_content[agent_id] += chunk
        self.current_active_agent = agent_id
        
        # Add to agent outputs for scrollable display
        if agent_id not in self.agent_outputs:
            self.agent_outputs[agent_id] = []
        
        # If chunk contains newlines, it's likely a complete response
        if '\n' in chunk or len(self.streaming_content[agent_id]) > 500:
            self.agent_outputs[agent_id].append(self.streaming_content[agent_id])
            self.streaming_content[agent_id] = ""
            
            # Keep only last 10 outputs per agent
            if len(self.agent_outputs[agent_id]) > 10:
                self.agent_outputs[agent_id] = self.agent_outputs[agent_id][-10:]
        
        # Log to work log if enabled
        if self.save_work_log:
            await self._log_to_work_log(f"**{self.agents[agent_id].name}**: {chunk}")
        
        # Update live display
        if self.live:
            self.live.update(self._create_layout())
    
    def _start_input_monitoring(self):
        """Start monitoring for human input in background thread."""
        if not self.human_input_enabled:
            return
            
        def input_monitor():
            while not self.stop_input_monitoring:
                try:
                    # Check for 'i' key press for intervention
                    import keyboard
                    if keyboard.is_pressed('i'):
                        self._handle_human_intervention()
                        import time
                        time.sleep(1)  # Prevent multiple triggers
                except ImportError:
                    # Fallback to simple input if keyboard module not available
                    pass
                except:
                    pass
                import time; time.sleep(0.1)
        
        self.input_thread = threading.Thread(target=input_monitor, daemon=True)
        self.input_thread.start()
    
    def _handle_human_intervention(self):
        """Handle human intervention request."""
        if self.live:
            self.live.stop()
        
        self.console.print("\n" + "="*60)
        self.console.print("🔔 [bold yellow]Human Intervention Available[/bold yellow]")
        self.console.print("="*60)
        
        options = [
            "1. Send message to current agent",
            "2. Send message to specific agent", 
            "3. Add agent conversation",
            "4. View agent outputs",
            "5. Continue execution"
        ]
        
        for option in options:
            self.console.print(f"   {option}")
        
        try:
            choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4", "5"], default="5")
            
            if choice == "1" and self.current_active_agent:
                message = Prompt.ask("Enter message for current agent")
                self.pending_human_input = f"Human input: {message}"
                asyncio.create_task(self._log_to_work_log(f"**Human Input to {self.agents[self.current_active_agent].name}**: {message}"))
                
            elif choice == "2":
                agent_names = [agent.name for agent in self.agents.values()]
                self.console.print(f"Available agents: {', '.join(agent_names)}")
                agent_name = Prompt.ask("Enter agent name")
                message = Prompt.ask("Enter message")
                
                # Find agent by name
                target_agent = None
                for agent in self.agents.values():
                    if agent.name.lower() == agent_name.lower():
                        target_agent = agent
                        break
                
                if target_agent:
                    self.pending_human_input = f"Human input for {target_agent.name}: {message}"
                    asyncio.create_task(self._log_to_work_log(f"**Human Input to {target_agent.name}**: {message}"))
                
            elif choice == "3":
                asyncio.create_task(self._handle_agent_conversation())
                
            elif choice == "4":
                self._display_agent_outputs()
        
        except KeyboardInterrupt:
            pass
        
        # Restart live display
        if self.live:
            self.live.start()
    
    def _create_layout(self) -> Layout:
        """Create the main layout for the terminal display."""
        layout = Layout()

        layout.split_column(
            Layout(self._create_header(), size=4),
            Layout(self._create_agent_table(), size=8),
            Layout(self._create_progress_panel(), size=6),
            Layout(self._create_streaming_panel(), size=18),
            Layout(self._create_intervention_panel(), size=4)
        )

        return layout
    
    def _create_header(self) -> Panel:
        """Create the header panel."""
        runtime = (datetime.now() - self.start_time).total_seconds()
        header_text = Text()
        header_text.append("🤖 AIFlow Multi-Agent Orchestrator\n", style="bold cyan")
        header_text.append(f"Session: {self.team_name} | Runtime: {runtime:.1f}s | Agents: {len(self.agents)}", style="white")
        
        return Panel(header_text, title="[bold]AIFlow Dashboard[/bold]", border_style="cyan")
    
    def _create_agent_table(self) -> Table:
        """Create the agent status table."""
        table = Table(title="Agent Status", show_header=True, header_style="bold magenta")
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Provider", style="blue")
        table.add_column("Tasks", justify="right", style="yellow")
        
        for agent in self.agents.values():
            status = self.agent_status.get(agent.id, "idle")
            status_emoji = "🟢" if status == "idle" else "🔴" if status == "working" else "⚪"
            
            table.add_row(
                agent.name,
                f"{status_emoji} {status}",
                agent.llm_provider.provider_name,
                str(agent.metrics.get("tasks_completed", 0))
            )
        
        return table
    
    def _create_progress_panel(self) -> Panel:
        """Create the progress panel."""
        return Panel(self.progress, title="[bold]Task Progress[/bold]", border_style="green")
    
    def _create_streaming_panel(self) -> Panel:
        """Create the streaming content panel with scrollable, formatted output."""
        if not self.agent_outputs or not any(self.agent_outputs.values()):
            content = Text("💭 Waiting for agent responses...\n\nPress 'i' for human intervention", style="dim white")
        else:
            # Create a text object for better control over formatting
            content = Text()
            
            # Show outputs from all agents with better formatting
            for agent_id, outputs in self.agent_outputs.items():
                agent = self.agents[agent_id]
                
                # Show current streaming content if agent is active
                if agent_id == self.current_active_agent and self.streaming_content.get(agent_id):
                    content.append(f"🔴 {agent.name} (Live)\n", style="bold red")
                    streaming_text = self.streaming_content[agent_id]
                    # Limit streaming content to last 300 characters for display
                    if len(streaming_text) > 300:
                        streaming_text = "..." + streaming_text[-300:]
                    content.append(f"{streaming_text}\n", style="cyan")
                    content.append("─" * 50 + "\n", style="dim white")
                
                # Show recent completed outputs
                if outputs:
                    content.append(f"🤖 {agent.name}\n", style="bold green")
                    
                    # Show last 2 outputs with proper formatting
                    recent_outputs = outputs[-2:] if len(outputs) > 2 else outputs
                    for i, output in enumerate(recent_outputs):
                        response_num = len(outputs) - len(recent_outputs) + i + 1
                        content.append(f"Response {response_num}: ", style="bold yellow")
                        
                        # Truncate long outputs for display
                        display_output = output
                        if len(display_output) > 200:
                            display_output = display_output[:200] + "..."
                        
                        # Format output with proper styling
                        if "```" in display_output or "def " in display_output or "class " in display_output:
                            content.append(f"{display_output}\n", style="green")
                        else:
                            content.append(f"{display_output}\n", style="white")
                        
                        content.append("─" * 30 + "\n", style="dim white")

        return Panel(
            content,
            title="[bold]🔴 Live Agent Output (Auto-scrolling)[/bold]",
            border_style="blue",
            height=18,
            padding=(0, 1)
        )
    
    def _create_intervention_panel(self) -> Panel:
        """Create the human intervention panel."""
        intervention_text = Text()
        intervention_text.append("🎯 Human Controls: ", style="bold cyan")
        intervention_text.append("Press 'i' for intervention • ", style="white")
        
        if self.pending_human_input:
            intervention_text.append(f"📝 Pending: {self.pending_human_input[:50]}...", style="yellow")
        else:
            intervention_text.append("Ready for input", style="green")
        
        # Show agent conversation count
        if self.agent_conversations:
            intervention_text.append(f" • {len(self.agent_conversations)} conversations", style="dim white")
        
        return Panel(
            intervention_text,
            title="[bold]Human Intervention[/bold]",
            border_style="yellow"
        )
    
    def get_pending_human_input(self) -> Optional[str]:
        """Get and clear pending human input."""
        input_text = self.pending_human_input
        self.pending_human_input = None
        return input_text
    
    async def add_agent_conversation(self, from_agent_id: str, to_agent_id: str, message: str, response: str):
        """Add an agent-to-agent conversation to the log."""
        conversation = {
            "timestamp": datetime.now(),
            "from_agent": self.agents[from_agent_id].name,
            "to_agent": self.agents[to_agent_id].name,
            "message": message,
            "response": response,
            "type": "agent_conversation"
        }
        
        self.agent_conversations.append(conversation)
        
        # Log to work log
        if self.save_work_log:
            await self._log_to_work_log(
                f"**Agent Conversation** {conversation['from_agent']} → {conversation['to_agent']}: {message}\n"
                f"**Response**: {response}"
            )
        
        # Update display
        if self.live:
            self.live.update(self._create_layout())
    
    async def _initialize_work_log(self):
        """Initialize the work log file."""
        header = f"""# AIFlow Work Log
**Session**: {self.team_name}  
**Started**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Agents**: {', '.join([agent.name for agent in self.agents.values()])}  
**Tasks**: {len(self.tasks)}  

---

## Execution Log

"""
        self.work_log_content.append(header)
        await self._save_work_log()
    
    async def _log_to_work_log(self, content: str):
        """Add content to work log."""
        if not self.save_work_log:
            return
            
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"**[{timestamp}]** {content}\n\n"
        self.work_log_content.append(log_entry)
        
        # Save periodically (every 10 entries)
        if len(self.work_log_content) % 10 == 0:
            await self._save_work_log()
    
    async def _finalize_work_log(self):
        """Finalize and save the complete work log."""
        if not self.save_work_log:
            return
            
        # Add final summary
        summary = f"""
---

## Session Summary
**Ended**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Duration**: {(datetime.now() - self.start_time).total_seconds():.2f}s  
**Completed Tasks**: {len([t for t in self.tasks.values() if hasattr(t, 'status') and t.status.value == "completed"])}  

### Agent Conversations
"""
        
        for conv in self.agent_conversations:
            summary += f"- **{conv['timestamp'].strftime('%H:%M:%S')}**: {conv['from_agent']} → {conv['to_agent']}: {conv['message']}\n"
        
        self.work_log_content.append(summary)
        await self._save_work_log()
    
    async def _save_work_log(self):
        """Save work log to file."""
        try:
            with open(self.work_log_path, 'w', encoding='utf-8') as f:
                f.write(''.join(self.work_log_content))
        except Exception:
            # Silently handle file write errors
            pass
    
    def _display_header(self):
        """Display initial header."""
        self.console.print(f"\n🚀 [bold cyan]AIFlow Multi-Agent Orchestrator[/bold cyan]")
        self.console.print(f"Session: [bold]{self.team_name}[/bold] | Agents: {len(self.agents)} | Tasks: {len(self.tasks)}")
        self.console.print("─" * 60)
    
    def _display_summary(self):
        """Display final summary."""
        runtime = (datetime.now() - self.start_time).total_seconds()
        self.console.print(f"\n✅ [bold green]Session Complete![/bold green]")
        self.console.print(f"Total Runtime: {runtime:.2f}s")
        self.console.print(f"Agents: {len(self.agents)} | Tasks: {len(self.tasks)}")
        if self.save_work_log:
            self.console.print(f"Work log saved: {self.work_log_path}")
        self.console.print("─" * 60)
    
    async def cleanup(self):
        """Cleanup interface resources."""
        self.stop_input_monitoring = True
        if self.input_thread and self.input_thread.is_alive():
            self.input_thread.join(timeout=1)
    
    async def _handle_agent_conversation(self):
        """Handle agent conversation setup."""
        if self.live:
            self.live.stop()

        self.console.print("\n" + "="*60)
        self.console.print("💬 [bold cyan]Agent Conversation Setup[/bold cyan]")
        self.console.print("="*60)

        agent_names = [agent.name for agent in self.agents.values()]
        self.console.print(f"Available agents: {', '.join(agent_names)}")

        # This would be extended with actual conversation setup
        self.console.print("Agent conversation feature ready!")

        if self.live:
            self.live.start()

    def _display_agent_outputs(self):
        """Display agent outputs."""
        if self.live:
            self.live.stop()

        self.console.print("\n" + "="*60)
        self.console.print("📊 [bold cyan]Agent Outputs[/bold cyan]")
        self.console.print("="*60)

        for agent_id, outputs in self.agent_outputs.items():
            agent = self.agents[agent_id]
            self.console.print(f"\n🤖 [bold]{agent.name}[/bold]:")

            if outputs:
                for i, output in enumerate(outputs[-3:], 1):  # Show last 3 outputs
                    self.console.print(f"  {i}. {output[:100]}...")
            else:
                self.console.print("  No outputs yet")

        input("Press Enter to continue...")

        if self.live:
            self.live.start()
