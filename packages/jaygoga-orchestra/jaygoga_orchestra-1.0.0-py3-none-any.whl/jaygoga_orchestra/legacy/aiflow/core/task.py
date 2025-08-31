"""
Real Task implementation for AIFlow multi-agent orchestrator.

Provides the core Task class with dependency management and execution tracking.
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Union, Any, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from .agent import Agent


class TaskStatus(Enum):
    """Task execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OutputFormat(Enum):
    """Supported output formats for task results."""
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"
    STRUCTURED_JSON = "structured_json"
    EXECUTIVE_SUMMARY = "executive_summary"


@dataclass
class TaskResult:
    """Container for task execution results."""
    task_id: str
    success: bool
    content: str
    metadata: Dict[str, Any]
    error: Optional[str] = None
    execution_time: float = 0.0
    tokens_used: int = 0
    agent_name: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class Task:
    """
    Core Task class for AIFlow multi-agent orchestrator.
    
    A Task represents a unit of work to be executed by an Agent.
    """
    
    def __init__(
        self,
        description: str,
        agent: Agent,
        output_format: Union[str, OutputFormat] = OutputFormat.TEXT,
        context_from: Optional[List['Task']] = None,
        depends_on: Optional[List['Task']] = None,
        memory_key: Optional[str] = None,
        tools: Optional[List[str]] = None,
        max_execution_time: Optional[int] = None,
        expected_output: Optional[str] = None,
        **kwargs
    ):
        """Initialize a Task."""
        self.id = str(uuid.uuid4())
        self.description = description
        self.agent = agent
        self.output_format = OutputFormat(output_format) if isinstance(output_format, str) else output_format
        self.created_at = datetime.now()
        self.expected_output = expected_output
        
        # Dependencies and context
        self.context_from = context_from or []
        self.depends_on = depends_on or []
        self.memory_key = memory_key
        
        # Execution configuration
        self.tools = tools or []
        self.max_execution_time = max_execution_time
        
        # Task state
        self.status = TaskStatus.PENDING
        self.result: Optional[TaskResult] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.context_data: Dict[str, Any] = {}
        
        # Execution tracking
        self.retry_count = 0
        self.max_retries = kwargs.get('max_retries', 3)
        self.progress = 0.0
        self.progress_message = ""
        
        # Callbacks
        self.on_start: Optional[Callable] = kwargs.get('on_start')
        self.on_complete: Optional[Callable] = kwargs.get('on_complete')
        self.on_error: Optional[Callable] = kwargs.get('on_error')
        self.on_progress: Optional[Callable] = kwargs.get('on_progress')
    
    async def execute(
        self,
        context: Optional[Dict[str, Any]] = None,
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> TaskResult:
        """Execute the task with the assigned agent."""
        if self.status != TaskStatus.PENDING:
            raise ValueError(f"Task {self.id} is not in pending status")
        
        # Check dependencies
        if not await self._check_dependencies():
            raise ValueError("Task dependencies not satisfied")
        
        self.status = TaskStatus.RUNNING
        self.start_time = datetime.now()
        
        if self.on_start:
            await self.on_start(self)
        
        try:
            # Build execution context
            execution_context = await self._build_execution_context(context)
            
            # Create progress callback
            progress_callback = self._create_progress_callback(stream_callback)
            
            # Execute with timeout if specified
            if self.max_execution_time:
                result = await asyncio.wait_for(
                    self._execute_with_agent(execution_context, progress_callback),
                    timeout=self.max_execution_time
                )
            else:
                result = await self._execute_with_agent(execution_context, progress_callback)
            
            # Process result based on output format
            processed_result = await self._process_result(result)
            
            # Store in memory if key provided
            if self.memory_key and self.agent.memory_manager:
                await self.agent.memory_manager.store_result(
                    key=self.memory_key,
                    result=processed_result.get("content", ""),
                    task_id=self.id
                )
            
            self.status = TaskStatus.COMPLETED
            self.end_time = datetime.now()
            # Include agent_messages in metadata if present
            metadata = processed_result.get("metadata", {})
            if "agent_messages" in processed_result:
                metadata["agent_messages"] = processed_result["agent_messages"]

            self.result = TaskResult(
                task_id=self.id,
                success=True,
                content=processed_result.get("content", ""),
                metadata=metadata,
                execution_time=(self.end_time - self.start_time).total_seconds(),
                tokens_used=processed_result.get("metadata", {}).get("tokens_used", 0),
                agent_name=self.agent.name
            )
            
            if self.on_complete:
                await self.on_complete(self, self.result)
            
            return self.result
            
        except asyncio.TimeoutError:
            self.status = TaskStatus.FAILED
            error_msg = f"Task timed out after {self.max_execution_time} seconds"
            self.result = TaskResult(
                task_id=self.id,
                success=False,
                content="",
                metadata={},
                error=error_msg,
                agent_name=self.agent.name
            )
            
            if self.on_error:
                await self.on_error(self, error_msg)
            
            raise TimeoutError(error_msg)
            
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.end_time = datetime.now()
            error_msg = str(e)
            
            self.result = TaskResult(
                task_id=self.id,
                success=False,
                content="",
                metadata={},
                error=error_msg,
                execution_time=(self.end_time - self.start_time).total_seconds() if self.start_time else 0,
                agent_name=self.agent.name
            )
            
            if self.on_error:
                await self.on_error(self, error_msg)
            
            # Retry logic
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                self.status = TaskStatus.PENDING
                await asyncio.sleep(2 ** self.retry_count)
                return await self.execute(context, stream_callback)
            
            raise e
    
    async def _check_dependencies(self) -> bool:
        """Check if all task dependencies are satisfied."""
        for dep_task in self.depends_on:
            if dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    async def _build_execution_context(self, additional_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build complete execution context for the task."""
        context = {
            "task_id": self.id,
            "task_description": self.description,
            "output_format": self.output_format.value,
            "tools": self.tools
        }
        
        # Add context from other tasks
        for ctx_source in self.context_from:
            if isinstance(ctx_source, Task) and ctx_source.result:
                context[f"context_from_{ctx_source.id}"] = ctx_source.result.content
        
        # Add additional context
        if additional_context:
            context.update(additional_context)
        
        return context
    
    def _create_progress_callback(self, stream_callback: Optional[Callable[[str], None]]) -> Callable:
        """Create a progress callback that updates task progress."""
        async def progress_callback(chunk: str):
            self.progress = min(self.progress + 0.1, 1.0)
            self.progress_message = f"Processing... {chunk[:50]}..."
            
            if self.on_progress:
                await self.on_progress(self, self.progress, self.progress_message)
            
            if stream_callback:
                await stream_callback(chunk)
        
        return progress_callback
    
    async def _execute_with_agent(
        self,
        context: Dict[str, Any],
        progress_callback: Callable
    ) -> Dict[str, Any]:
        """Execute the task with the assigned agent."""
        result = await self.agent.execute_task(
            task_description=self.description,
            context=context,
            stream_callback=progress_callback
        )
        return result
    
    async def _process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process the result based on the specified output format."""
        content = result.get("content", "")
        
        if self.output_format == OutputFormat.JSON:
            try:
                import json
                parsed = json.loads(content)
                result["content"] = json.dumps(parsed, indent=2)
            except:
                result["content"] = content
        
        elif self.output_format == OutputFormat.STRUCTURED_JSON:
            if not content.strip().startswith('{'):
                result["content"] = f'{{"analysis": "{content}"}}'
        
        # Add format metadata
        if "metadata" not in result:
            result["metadata"] = {}
        result["metadata"]["output_format"] = self.output_format.value
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get current task status and metadata."""
        return {
            "id": self.id,
            "description": self.description[:100] + "..." if len(self.description) > 100 else self.description,
            "status": self.status.value,
            "agent_name": self.agent.name,
            "progress": self.progress,
            "progress_message": self.progress_message,
            "output_format": self.output_format.value,
            "retry_count": self.retry_count,
            "execution_time": (
                (self.end_time - self.start_time).total_seconds() 
                if self.start_time and self.end_time 
                else (datetime.now() - self.start_time).total_seconds() 
                if self.start_time 
                else 0
            )
        }
    
    def cancel(self):
        """Cancel the task execution."""
        if self.status in [TaskStatus.PENDING]:
            self.status = TaskStatus.CANCELLED
        else:
            raise ValueError(f"Cannot cancel task in status: {self.status.value}")
    
    def __repr__(self) -> str:
        return f"Task(id='{self.id[:8]}...', status='{self.status.value}', agent='{self.agent.name}')"
