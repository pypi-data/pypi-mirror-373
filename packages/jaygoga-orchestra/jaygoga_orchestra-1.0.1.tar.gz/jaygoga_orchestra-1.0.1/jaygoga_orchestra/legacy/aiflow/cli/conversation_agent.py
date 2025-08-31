"""
Conversation Agent Interface for AIFlow
Beautiful interactive conversation system with AI agents.
"""

import asyncio
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.columns import Columns
from datetime import datetime
import json

from ..core.agent import Agent
from ..memory.manager import AdvancedMemoryManager
from ..memory.base import MemoryConfig

console = Console()

class ConversationAgent:
    """Beautiful conversation interface for AI agents."""
    
    def __init__(self, agent_config: Optional[Dict[str, Any]] = None):
        self.console = Console()
        self.agent_config = agent_config or {}
        self.conversation_history = []
        self.current_agent = None
        self.memory_manager = None
        self.session_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    async def initialize(self):
        """Initialize the conversation agent with memory."""
        # Initialize memory manager
        memory_config = MemoryConfig(enable_persistence=True)
        self.memory_manager = AdvancedMemoryManager(memory_config)
        await self.memory_manager.connect()
        
        # Create default agent if none provided
        if not self.current_agent:
            self.current_agent = Agent(
                name=self.agent_config.get("name", "AIFlow Assistant"),
                role=self.agent_config.get("role", "Conversational AI Assistant"),
                goal=self.agent_config.get("goal", "Help users with their questions and tasks"),
                backstory=self.agent_config.get("backstory", 
                    "I'm an advanced AI assistant powered by AIFlow, designed to have natural "
                    "conversations and help you accomplish your goals efficiently.")
            )
    
    async def start_conversation(self):
        """Start the main conversation loop."""
        await self.initialize()
        
        self.show_conversation_header()
        self.show_agent_introduction()
        
        while True:
            try:
                user_input = await self.get_user_input()
                
                if self.is_exit_command(user_input):
                    await self.end_conversation()
                    break
                    
                if self.is_special_command(user_input):
                    await self.handle_special_command(user_input)
                    continue
                
                # Process user message
                await self.process_user_message(user_input)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]💡 Use '/exit' to end conversation gracefully.[/yellow]")
            except Exception as e:
                self.console.print(f"[red]❌ Error: {e}[/red]")
    
    def show_conversation_header(self):
        """Display beautiful conversation header."""
        header = Panel(
            "[bold cyan]💬 AIFlow Conversation Mode[/bold cyan]\n\n"
            "🤖 You're now chatting with an AI agent\n"
            "💡 [dim]Special commands: /help, /memory, /clear, /save, /exit[/dim]",
            title="🚀 Conversation Started",
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(header)
        self.console.print()
    
    def show_agent_introduction(self):
        """Show agent introduction."""
        if self.current_agent:
            intro_panel = Panel(
                f"[bold green]Hello! I'm {self.current_agent.name}[/bold green]\n\n"
                f"🎯 [cyan]Role:[/cyan] {self.current_agent.role}\n"
                f"🚀 [cyan]Goal:[/cyan] {self.current_agent.goal}\n\n"
                f"[dim]{self.current_agent.backstory}[/dim]\n\n"
                "[yellow]How can I help you today?[/yellow]",
                title=f"🤖 {self.current_agent.name}",
                border_style="green",
                padding=(1, 2)
            )
            self.console.print(intro_panel)
            self.console.print()
    
    async def get_user_input(self) -> str:
        """Get user input with beautiful prompt."""
        return Prompt.ask(
            "[bold blue]You[/bold blue] [dim]>[/dim]",
            default=""
        )
    
    def is_exit_command(self, user_input: str) -> bool:
        """Check if user wants to exit."""
        return user_input.lower().strip() in ['/exit', '/quit', '/bye', 'exit', 'quit', 'bye']
    
    def is_special_command(self, user_input: str) -> bool:
        """Check if input is a special command."""
        return user_input.strip().startswith('/')
    
    async def handle_special_command(self, command: str):
        """Handle special conversation commands."""
        cmd = command.strip().lower()
        
        if cmd == '/help':
            self.show_help()
        elif cmd == '/memory':
            await self.show_memory_status()
        elif cmd == '/clear':
            await self.clear_conversation()
        elif cmd == '/save':
            await self.save_conversation()
        elif cmd == '/agent':
            await self.show_agent_details()
        elif cmd == '/history':
            self.show_conversation_history()
        else:
            self.console.print(f"[red]Unknown command: {cmd}[/red]")
            self.console.print("[dim]Type '/help' for available commands.[/dim]")
    
    async def process_user_message(self, user_input: str):
        """Process user message and generate AI response."""
        # Add to conversation history
        self.conversation_history.append({
            "timestamp": datetime.now(),
            "type": "user",
            "content": user_input
        })
        
        # Store in memory
        if self.memory_manager:
            await self.memory_manager.add_interaction(
                content=user_input,
                agent_id=self.current_agent.id if self.current_agent else "default",
                session_id=self.session_id
            )
        
        # Show thinking animation
        with self.console.status("[bold green]🤔 AI is thinking...", spinner="dots"):
            # Simulate AI processing (replace with actual agent call)
            await asyncio.sleep(1.5)
            
            # Get context from memory
            context = ""
            if self.memory_manager:
                recent_memories = await self.memory_manager.get_recent_context(
                    agent_id=self.current_agent.id if self.current_agent else "default",
                    session_id=self.session_id,
                    limit=5
                )
                if recent_memories:
                    context = f"Recent context: {' '.join(recent_memories[:2])}"
            
            # Generate response (this would be replaced with actual agent execution)
            response = await self.generate_ai_response(user_input, context)
        
        # Display AI response
        self.display_ai_response(response)
        
        # Add to conversation history
        self.conversation_history.append({
            "timestamp": datetime.now(),
            "type": "assistant",
            "content": response
        })
        
        # Store AI response in memory
        if self.memory_manager:
            await self.memory_manager.add_interaction(
                content=f"Assistant: {response}",
                agent_id=self.current_agent.id if self.current_agent else "default",
                session_id=self.session_id
            )
    
    async def generate_ai_response(self, user_input: str, context: str = "") -> str:
        """Generate AI response (placeholder - replace with actual agent execution)."""
        # This is a placeholder. In real implementation, this would:
        # 1. Use the actual agent to process the input
        # 2. Consider the conversation context
        # 3. Generate appropriate response
        
        responses = [
            f"I understand you're asking about: '{user_input}'. Let me help you with that!",
            f"That's an interesting question about '{user_input}'. Here's what I think...",
            f"Based on your message '{user_input}', I can provide some insights.",
            f"Great question! Regarding '{user_input}', here's my perspective...",
        ]
        
        import random
        base_response = random.choice(responses)
        
        if context:
            base_response += f"\n\nConsidering our previous conversation, I can add that this relates to what we discussed earlier."
        
        return base_response
    
    def display_ai_response(self, response: str):
        """Display AI response beautifully."""
        response_panel = Panel(
            response,
            title=f"🤖 {self.current_agent.name if self.current_agent else 'AI Assistant'}",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(response_panel)
        self.console.print()
    
    def show_help(self):
        """Show conversation help."""
        help_table = Table(title="💬 Conversation Commands")
        help_table.add_column("Command", style="cyan", width=12)
        help_table.add_column("Description", style="white")
        
        help_table.add_row("/help", "Show this help message")
        help_table.add_row("/memory", "Show memory status")
        help_table.add_row("/clear", "Clear conversation history")
        help_table.add_row("/save", "Save conversation to file")
        help_table.add_row("/agent", "Show agent details")
        help_table.add_row("/history", "Show conversation history")
        help_table.add_row("/exit", "End conversation")
        
        self.console.print(help_table)
        self.console.print()
    
    async def show_memory_status(self):
        """Show memory system status."""
        if not self.memory_manager:
            self.console.print("[yellow]Memory system not initialized.[/yellow]")
            return
        
        # Get memory statistics
        try:
            memories = await self.memory_manager.retrieve_memories(
                query="conversation",
                agent_id=self.current_agent.id if self.current_agent else "default",
                limit=10
            )
            
            memory_panel = Panel(
                f"[bold green]🧠 Memory Status[/bold green]\n\n"
                f"📊 [cyan]Total memories:[/cyan] {len(memories)}\n"
                f"🔄 [cyan]Session ID:[/cyan] {self.session_id}\n"
                f"💭 [cyan]Recent interactions:[/cyan] {len(self.conversation_history)}\n\n"
                "[dim]Memory helps me remember our conversation context.[/dim]",
                title="🧠 Memory System",
                border_style="magenta"
            )
            self.console.print(memory_panel)
            
        except Exception as e:
            self.console.print(f"[red]Error accessing memory: {e}[/red]")
    
    async def clear_conversation(self):
        """Clear conversation history."""
        if Confirm.ask("[bold yellow]Clear conversation history?[/bold yellow]"):
            self.conversation_history.clear()
            self.console.clear()
            self.show_conversation_header()
            self.console.print("[green]✅ Conversation history cleared.[/green]")
        else:
            self.console.print("[dim]Conversation history kept.[/dim]")
    
    async def save_conversation(self):
        """Save conversation to file."""
        if not self.conversation_history:
            self.console.print("[yellow]No conversation to save.[/yellow]")
            return
        
        filename = f"conversation_{self.session_id}.json"
        
        conversation_data = {
            "session_id": self.session_id,
            "agent": {
                "name": self.current_agent.name if self.current_agent else "Unknown",
                "role": self.current_agent.role if self.current_agent else "Unknown"
            },
            "started_at": self.conversation_history[0]["timestamp"].isoformat() if self.conversation_history else None,
            "messages": [
                {
                    "timestamp": msg["timestamp"].isoformat(),
                    "type": msg["type"],
                    "content": msg["content"]
                }
                for msg in self.conversation_history
            ]
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            
            self.console.print(f"[green]✅ Conversation saved to: {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Error saving conversation: {e}[/red]")
    
    async def show_agent_details(self):
        """Show detailed agent information."""
        if not self.current_agent:
            self.console.print("[yellow]No agent loaded.[/yellow]")
            return
        
        agent_table = Table(title=f"🤖 {self.current_agent.name} Details")
        agent_table.add_column("Property", style="cyan")
        agent_table.add_column("Value", style="white")
        
        agent_table.add_row("Name", self.current_agent.name)
        agent_table.add_row("Role", self.current_agent.role)
        agent_table.add_row("Goal", self.current_agent.goal)
        agent_table.add_row("ID", self.current_agent.id)
        
        self.console.print(agent_table)
    
    def show_conversation_history(self):
        """Show conversation history."""
        if not self.conversation_history:
            self.console.print("[yellow]No conversation history.[/yellow]")
            return
        
        history_panel = Panel(
            f"[bold cyan]📜 Conversation History[/bold cyan]\n\n"
            f"Total messages: {len(self.conversation_history)}\n"
            f"Session: {self.session_id}",
            title="📜 History",
            border_style="blue"
        )
        self.console.print(history_panel)
        
        # Show recent messages
        recent_messages = self.conversation_history[-5:] if len(self.conversation_history) > 5 else self.conversation_history
        
        for msg in recent_messages:
            timestamp = msg["timestamp"].strftime("%H:%M:%S")
            if msg["type"] == "user":
                self.console.print(f"[dim]{timestamp}[/dim] [bold blue]You:[/bold blue] {msg['content'][:100]}...")
            else:
                self.console.print(f"[dim]{timestamp}[/dim] [bold cyan]AI:[/bold cyan] {msg['content'][:100]}...")
    
    async def end_conversation(self):
        """End conversation gracefully."""
        if self.conversation_history:
            save_prompt = Confirm.ask("[bold yellow]Save conversation before exiting?[/bold yellow]")
            if save_prompt:
                await self.save_conversation()
        
        # Cleanup
        if self.memory_manager:
            await self.memory_manager.disconnect()
        
        goodbye_panel = Panel(
            "[bold green]Thank you for the conversation![/bold green]\n\n"
            "🤖 It was great chatting with you!\n"
            "💫 Come back anytime for more AI assistance.\n\n"
            "[dim]Conversation ended gracefully. 👋[/dim]",
            title="👋 Goodbye",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(Align.center(goodbye_panel))


# Standalone conversation launcher
async def start_conversation_mode(agent_config: Optional[Dict[str, Any]] = None):
    """Start a standalone conversation session."""
    conv_agent = ConversationAgent(agent_config)
    await conv_agent.start_conversation()


if __name__ == "__main__":
    # Example usage
    asyncio.run(start_conversation_mode())
