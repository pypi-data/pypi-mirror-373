"""
AIFlow Squad - Govinda Compatible Interface
"""

import asyncio
from enum import Enum
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.table import Table

from .agent import Agent
from .task import Task
from .core.team import Team as CoreTeam

console = Console()

class Process(Enum):
    """Process types for squad execution."""
    sequential = "sequential"
    hierarchical = "hierarchical"
    parallel = "parallel"

class Squad:
    """Govinda-compatible Squad class for AIFlow."""
    
    def __init__(
        self,
        agents: List[Agent],
        tasks: List[Task],
        process: Process = Process.sequential,
        verbose: int = 0,
        memory: bool = False,
        cache: bool = True,
        max_rpm: Optional[int] = None,
        language: str = "en",
        full_output: bool = False,
        step_callback: Optional[Callable] = None,
        task_callback: Optional[Callable] = None,
        share_crew: bool = False,
        output_log_file: Optional[str] = None,
        manager_llm: Optional[str] = None,
        manager_agent: Optional[Agent] = None,
        prompt_file: Optional[str] = None,
        planning: bool = False,
        **kwargs
    ):
        """
        Initialize Squad with Govinda-compatible interface.
        
        Args:
            agents: List of agents in the squad
            tasks: List of tasks to execute
            process: Execution process (sequential, hierarchical, parallel)
            verbose: Verbosity level (0=quiet, 1=normal, 2=verbose)
            memory: Whether to use memory
            cache: Whether to use caching
            max_rpm: Maximum requests per minute
            language: Language for the squad
            full_output: Whether to return full output
            step_callback: Callback for each step
            task_callback: Callback for each task
            share_crew: Whether to share squad data
            output_log_file: File to log output
            manager_llm: LLM for manager agent
            manager_agent: Manager agent for hierarchical process
            prompt_file: File containing prompts
            planning: Whether to use planning
        """
        self.agents = agents
        self.tasks = tasks
        self.process = process
        self.verbose = verbose
        self.memory = memory
        self.cache = cache
        self.max_rpm = max_rpm
        self.language = language
        self.full_output = full_output
        self.step_callback = step_callback
        self.task_callback = task_callback
        self.share_crew = share_crew
        self.output_log_file = output_log_file
        self.manager_llm = manager_llm
        self.manager_agent = manager_agent
        self.prompt_file = prompt_file
        self.planning = planning
        
        # Validate inputs
        self._validate_crew()
        
        # Create internal CoreTeam
        core_agents = [agent._core_agent for agent in agents]
        core_tasks = [task._core_task for task in tasks]
        
        self._core_team = CoreTeam(
            name="AIFlow_Crew",
            agents=core_agents,
            tasks=core_tasks,
            session_name=f"crew_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        # Execution state
        self.is_running = False
        self.results = {}
        self.execution_time = 0
    
    def _validate_crew(self):
        """Validate squad configuration."""
        if not self.agents:
            raise ValueError("Squad must have at least one agent")
        
        if not self.tasks:
            raise ValueError("Squad must have at least one task")
        
        # Assign agents to tasks if not already assigned
        for i, task in enumerate(self.tasks):
            if not task.agent:
                # Assign agent in round-robin fashion
                task.agent = self.agents[i % len(self.agents)]
                task._core_task.agent_name = task.agent.name
    
    def execute(self, inputs: Optional[Dict[str, Any]] = None) -> str:
        """
        Start the squad execution (Govinda-compatible method).
        
        Args:
            inputs: Optional inputs for the squad
            
        Returns:
            Final result as string
        """
        return asyncio.run(self.kickoff_async(inputs))
    
    async def kickoff_async(self, inputs: Optional[Dict[str, Any]] = None) -> str:
        """
        Start the squad execution asynchronously.
        
        Args:
            inputs: Optional inputs for the squad
            
        Returns:
            Final result as string
        """
        self.is_running = True
        start_time = datetime.now()
        
        try:
            if self.verbose >= 1:
                self._print_crew_start()
            
            # Execute based on process type
            if self.process == Process.sequential:
                result = await self._execute_sequential()
            elif self.process == Process.parallel:
                result = await self._execute_parallel()
            elif self.process == Process.hierarchical:
                result = await self._execute_hierarchical()
            else:
                raise ValueError(f"Unsupported process type: {self.process}")
            
            self.execution_time = (datetime.now() - start_time).total_seconds()
            
            if self.verbose >= 1:
                self._print_crew_completion()
            
            # Save output log if specified
            if self.output_log_file:
                self._save_output_log(result)
            
            return result
            
        except Exception as e:
            self.execution_time = (datetime.now() - start_time).total_seconds()
            if self.verbose >= 1:
                console.print(f"[red]❌ Squad execution failed: {e}[/red]")
            raise e
        finally:
            self.is_running = False
    
    async def _execute_sequential(self) -> str:
        """Execute tasks sequentially."""
        if self.verbose >= 2:
            console.print("[cyan]🔄 Executing tasks sequentially...[/cyan]")
        
        results = []
        context = ""
        
        for i, task in enumerate(self.tasks):
            if self.verbose >= 1:
                self._print_task_start(task, i + 1)
            
            try:
                # Execute task with accumulated context
                result = await task.execute_async(context)
                results.append(result)
                
                # Add result to context for next task
                context += f"\n\nPrevious task result: {result}"
                
                if self.verbose >= 1:
                    self._print_task_completion(task, result)
                
                # Execute task callback if provided
                if self.task_callback:
                    self.task_callback(task)
                    
            except Exception as e:
                if self.verbose >= 1:
                    console.print(f"[red]❌ Task {i+1} failed: {e}[/red]")
                raise e
        
        # Return the last task's result as the final output
        return results[-1] if results else "No tasks completed"
    
    async def _execute_parallel(self) -> str:
        """Execute tasks in parallel."""
        if self.verbose >= 2:
            console.print("[cyan]🔄 Executing tasks in parallel...[/cyan]")
        
        # Create tasks for parallel execution
        async_tasks = []
        for task in self.tasks:
            async_tasks.append(task.execute_async())
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                if self.verbose >= 1:
                    console.print(f"[red]❌ Task {i+1} failed: {result}[/red]")
                raise result
            else:
                successful_results.append(result)
                if self.verbose >= 1:
                    self._print_task_completion(self.tasks[i], result)
        
        # Combine all results
        return "\n\n".join(successful_results)
    
    async def _execute_hierarchical(self) -> str:
        """Execute tasks hierarchically with manager oversight."""
        if self.verbose >= 2:
            console.print("[cyan]🔄 Executing tasks hierarchically...[/cyan]")
        
        # For now, fall back to sequential execution
        # TODO: Implement proper hierarchical execution with manager
        return await self._execute_sequential()
    
    def _print_crew_start(self):
        """Print squad start message."""
        console.print(Panel(
            f"[bold cyan]🚀 Starting AIFlow Squad Execution[/bold cyan]\n\n"
            f"Agents: {len(self.agents)}\n"
            f"Tasks: {len(self.tasks)}\n"
            f"Process: {self.process.value}",
            title="Squad Kickoff",
            border_style="cyan"
        ))
    
    def _print_crew_completion(self):
        """Print squad completion message."""
        console.print(Panel(
            f"[bold green]✅ Squad Execution Complete![/bold green]\n\n"
            f"Execution time: {self.execution_time:.2f}s\n"
            f"Tasks completed: {len(self.tasks)}",
            title="Squad Complete",
            border_style="green"
        ))
    
    def _print_task_start(self, task: Task, task_num: int):
        """Print task start message."""
        if self.verbose >= 2:
            console.print(f"\n[yellow]📋 Task {task_num}: {task.description[:100]}...[/yellow]")
            console.print(f"[dim]Agent: {task.agent.role}[/dim]")
    
    def _print_task_completion(self, task: Task, result: str):
        """Print task completion message."""
        if self.verbose >= 2:
            console.print(f"[green]✅ Task completed[/green]")
            if len(result) > 200:
                console.print(f"[dim]Result: {result[:200]}...[/dim]")
            else:
                console.print(f"[dim]Result: {result}[/dim]")
    
    def _save_output_log(self, result: str):
        """Save output log to file."""
        try:
            log_content = f"""# AIFlow Squad Execution Log
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Execution Time: {self.execution_time:.2f}s
Process: {self.process.value}

## Agents
{chr(10).join([f"- {agent.role}: {agent.goal}" for agent in self.agents])}

## Tasks
{chr(10).join([f"- {task.description[:100]}..." for task in self.tasks])}

## Final Result
{result}
"""
            with open(self.output_log_file, 'w', encoding='utf-8') as f:
                f.write(log_content)
                
            if self.verbose >= 1:
                console.print(f"[cyan]📄 Output log saved to: {self.output_log_file}[/cyan]")
                
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not save output log: {e}[/yellow]")
    
    def __str__(self):
        return f"Squad(agents={len(self.agents)}, tasks={len(self.tasks)}, process={self.process.value})"
    
    def __repr__(self):
        return self.__str__()
