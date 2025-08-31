"""
AIFlow Task - Govinda Compatible Interface
"""

from typing import Optional, List, Dict, Any, Callable
from .core.task import Task as CoreTask
from .agent import Agent

class Task:
    """Govinda-compatible Task class for AIFlow."""
    
    def __init__(
        self,
        description: str,
        agent: Optional[Agent] = None,
        expected_output: Optional[str] = None,
        tools: Optional[List] = None,
        async_execution: bool = False,
        context: Optional[List['Task']] = None,
        config: Optional[Dict[str, Any]] = None,
        output_json: Optional[Dict] = None,
        output_pydantic: Optional[Any] = None,
        output_file: Optional[str] = None,
        callback: Optional[Callable] = None,
        human_input: bool = False,
        **kwargs
    ):
        """
        Initialize Task with Govinda-compatible interface.
        
        Args:
            description: Description of the task
            agent: Agent assigned to this task
            expected_output: Expected output description
            tools: List of tools available for this task
            async_execution: Whether to execute asynchronously
            context: List of tasks that provide context
            config: Task configuration
            output_json: JSON schema for output
            output_pydantic: Pydantic model for output
            output_file: File to save output to
            callback: Callback function after task completion
            human_input: Whether human input is required
        """
        self.description = description
        self.agent = agent
        self.expected_output = expected_output or "Task completion confirmation"
        self.tools = tools or []
        self.async_execution = async_execution
        self.context = context or []
        self.config = config or {}
        self.output_json = output_json
        self.output_pydantic = output_pydantic
        self.output_file = output_file
        self.callback = callback
        self.human_input = human_input
        
        # Create internal CoreTask
        dependencies = []
        if self.context:
            dependencies = [task.id for task in self.context if hasattr(task, 'id')]
        
        self._core_task = CoreTask(
            description=description,
            expected_output=self.expected_output,
            agent_name=agent.name if agent else None,
            dependencies=dependencies,
            config=self.config
        )
        
        # Store additional properties
        self.id = self._core_task.id
        self.status = "pending"
        self.result = None
        self.output = None
    
    def execute_sync(self, context: Optional[str] = None) -> str:
        """Execute task synchronously (for compatibility)."""
        import asyncio
        return asyncio.run(self.execute_async(context))
    
    async def execute_async(self, context: Optional[str] = None) -> str:
        """Execute task asynchronously."""
        if not self.agent:
            raise ValueError("Task must have an agent assigned")
        
        try:
            self.status = "running"
            
            # Build context from dependent tasks
            task_context = context or ""
            if self.context:
                context_parts = []
                for ctx_task in self.context:
                    if hasattr(ctx_task, 'result') and ctx_task.result:
                        context_parts.append(f"Context from {ctx_task.description[:50]}...: {ctx_task.result}")
                if context_parts:
                    task_context = "\n".join(context_parts)
            
            # Execute using the agent's core agent
            result = await self.agent._core_agent.execute_task(
                self._core_task,
                context=task_context
            )
            
            if result.get("success"):
                self.result = result.get("content", "")
                self.output = self.result
                self.status = "completed"
                
                # Save to file if specified
                if self.output_file:
                    self._save_output_to_file()
                
                # Execute callback if provided
                if self.callback:
                    self.callback(self)
                
                return self.result
            else:
                self.status = "failed"
                error_msg = result.get("error", "Task execution failed")
                raise Exception(error_msg)
                
        except Exception as e:
            self.status = "failed"
            self.result = f"Error: {str(e)}"
            raise e
    
    def _save_output_to_file(self):
        """Save task output to specified file."""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(self.result)
        except Exception as e:
            print(f"Warning: Could not save output to {self.output_file}: {e}")
    
    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == "completed"
    
    @property
    def is_failed(self) -> bool:
        """Check if task failed."""
        return self.status == "failed"
    
    @property
    def is_running(self) -> bool:
        """Check if task is running."""
        return self.status == "running"
    
    def __str__(self):
        return f"Task(description='{self.description[:50]}...', status='{self.status}')"
    
    def __repr__(self):
        return self.__str__()
