"""
Real Team implementation for AIFlow multi-agent orchestrator.

Provides the core Team class that orchestrates multiple agents and tasks.
"""

import asyncio
import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

from .agent import Agent
from .task import Task, TaskStatus, TaskResult
from .performance_monitor import PerformanceMonitor
from .result_validator import ResultValidationSystem
from ..interfaces.terminal_interface import TerminalInterface
from ..interfaces.intervention import HumanIntervention, AgentConversation
from ..tools.mcp_adapter import MCPServerAdapter, StdioServerParameters

logger = logging.getLogger(__name__)


class TeamStatus(Enum):
    """Team execution status enumeration."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TeamMetrics:
    """Team execution metrics and statistics."""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_execution_time: float = 0.0
    total_tokens_used: int = 0
    average_task_time: float = 0.0
    agents_used: int = 0


class Team:
    """
    Core Team class for AIFlow multi-agent orchestrator.
    
    A Team manages multiple agents and coordinates task execution.
    """
    
    def __init__(
        self,
        agents: List[Agent],
        tasks: List[Task],
        session_name: Optional[str] = None,
        parallel_execution: bool = False,
        max_concurrent_tasks: int = 3,
        save_work_log: bool = False,
        enable_human_intervention: bool = True,
        enable_agent_conversations: bool = True,
        mcp_server_params: Optional[List[Any]] = None,
        **kwargs
    ):
        """Initialize a Team."""
        self.id = str(uuid.uuid4())
        self.session_name = session_name or f"team_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.created_at = datetime.now()
        
        # Team composition
        self.agents = {agent.id: agent for agent in agents}
        self.tasks = {task.id: task for task in tasks}
        
        # Execution configuration
        self.parallel_execution = parallel_execution
        self.max_concurrent_tasks = max_concurrent_tasks
        
        # Team state
        self.status = TeamStatus.IDLE
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.current_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []
        
        # Results and metrics
        self.results: Dict[str, TaskResult] = {}
        self.metrics = TeamMetrics()
        self.execution_log: List[Dict[str, Any]] = []
        
        # Human intervention and agent conversation systems
        self.human_intervention = HumanIntervention(enabled=enable_human_intervention)
        self.agent_conversation = AgentConversation()

        # Performance monitoring and validation systems
        self.performance_monitor = PerformanceMonitor(session_name=self.session_name)
        self.result_validator = ResultValidationSystem()

        # MCP server management
        self.mcp_server_params = mcp_server_params or []
        self.mcp_adapters: List[MCPServerAdapter] = []
        self.mcp_tools: List[Any] = []

        # Register agents for conversations
        for agent in self.agents.values():
            self.agent_conversation.register_agent(agent.id, agent)

        # Terminal interface for display
        self.terminal_interface = TerminalInterface(
            team_name=self.session_name,
            agents=list(self.agents.values()),
            tasks=list(self.tasks.values()),
            save_work_log=save_work_log
        )
        
        # Async coordination
        self._execution_lock = asyncio.Lock()
        self._task_semaphore = asyncio.Semaphore(max_concurrent_tasks)
        
        # Validate team configuration
        self._validate_team()
    
    def _validate_team(self):
        """Validate team configuration and task dependencies."""
        # Check that all tasks have valid agents
        for task in self.tasks.values():
            if task.agent.id not in self.agents:
                raise ValueError(f"Task {task.id} references unknown agent {task.agent.id}")
        
        # Check for circular dependencies
        self._check_circular_dependencies()
    
    def _check_circular_dependencies(self):
        """Check for circular dependencies in task graph."""
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = self.tasks[task_id]
            for dep_task in task.depends_on:
                if dep_task.id not in visited:
                    if has_cycle(dep_task.id):
                        return True
                elif dep_task.id in rec_stack:
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        for task_id in self.tasks:
            if task_id not in visited:
                if has_cycle(task_id):
                    raise ValueError("Circular dependency detected in task graph")
    
    async def async_go(
        self,
        stream: bool = True,
        save_session: bool = True
    ) -> Dict[str, Any]:
        """Execute the team's tasks asynchronously."""
        async with self._execution_lock:
            if self.status != TeamStatus.IDLE:
                raise ValueError(f"Team is not in idle status: {self.status.value}")
            
            self.status = TeamStatus.RUNNING
            self.start_time = datetime.now()
            
            try:
                # Initialize systems
                if stream:
                    await self.terminal_interface.start()

                # Start human intervention monitoring
                self.human_intervention.start_monitoring()

                # Execute tasks
                if self.parallel_execution:
                    await self._execute_parallel()
                else:
                    await self._execute_sequential()
                
                self.status = TeamStatus.COMPLETED
                self.end_time = datetime.now()
                
                # Generate final results
                results = await self._generate_results()
                
                # Generate output.md if requested
                if save_session:
                    await self._generate_output_file(results)
                
                return results
                
            except Exception as e:
                self.status = TeamStatus.FAILED
                self.end_time = datetime.now()
                
                error_result = {
                    "success": False,
                    "error": str(e),
                    "partial_results": {tid: result.__dict__ for tid, result in self.results.items()},
                    "metrics": self._calculate_metrics()
                }
                
                raise e
                
            finally:
                # Cleanup
                self.human_intervention.stop_monitoring()
                if stream:
                    await self.terminal_interface.stop()
    
    async def _execute_sequential(self):
        """Execute tasks sequentially based on dependencies."""
        remaining_tasks = set(self.tasks.keys())
        
        while remaining_tasks:
            # Find tasks that can be executed
            ready_tasks = []
            for task_id in remaining_tasks:
                task = self.tasks[task_id]
                if all(dep.status == TaskStatus.COMPLETED for dep in task.depends_on):
                    ready_tasks.append(task_id)
            
            if not ready_tasks:
                failed_deps = any(
                    any(dep.status == TaskStatus.FAILED for dep in self.tasks[tid].depends_on)
                    for tid in remaining_tasks
                )
                if failed_deps:
                    raise Exception("Cannot proceed due to failed task dependencies")
                else:
                    raise Exception("No ready tasks found - possible circular dependency")
            
            # Execute the first ready task
            task_id = ready_tasks[0]
            await self._execute_single_task(task_id)
            remaining_tasks.remove(task_id)
    
    async def _execute_parallel(self):
        """Execute tasks in parallel respecting dependencies."""
        remaining_tasks = set(self.tasks.keys())
        running_tasks = {}
        
        while remaining_tasks or running_tasks:
            # Start new tasks that are ready
            ready_tasks = []
            for task_id in remaining_tasks:
                task = self.tasks[task_id]
                if all(dep.status == TaskStatus.COMPLETED for dep in task.depends_on):
                    ready_tasks.append(task_id)
            
            # Start tasks up to the concurrency limit
            while ready_tasks and len(running_tasks) < self.max_concurrent_tasks:
                task_id = ready_tasks.pop(0)
                remaining_tasks.remove(task_id)
                
                # Start task execution
                task_coroutine = self._execute_single_task(task_id)
                running_tasks[task_id] = asyncio.create_task(task_coroutine)
            
            # Wait for at least one task to complete
            if running_tasks:
                done, pending = await asyncio.wait(
                    running_tasks.values(),
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Process completed tasks
                for task_future in done:
                    # Find which task completed
                    completed_task_id = None
                    for tid, future in running_tasks.items():
                        if future == task_future:
                            completed_task_id = tid
                            break
                    
                    if completed_task_id:
                        del running_tasks[completed_task_id]
                        
                        # Handle task result
                        try:
                            await task_future
                        except Exception as e:
                            self.failed_tasks.append(completed_task_id)
                            if self._should_fail_team(completed_task_id):
                                raise e

    async def _execute_single_task(self, task_id: str):
        """Execute a single task with monitoring, human intervention, and agent conversations."""
        task = self.tasks[task_id]
        self.current_tasks[task_id] = task

        # Start performance monitoring
        self.performance_monitor.start_task(task_id, task.agent.name)

        try:
            # Update terminal display
            await self.terminal_interface.update_task_status(task, "running")

            # Check for human intervention before starting
            intervention = await self.human_intervention.check_intervention(
                task.agent.name, task.description
            )

            # Check for pending human input from terminal
            human_input = self.terminal_interface.get_pending_human_input()
            if human_input:
                intervention = human_input

            # Create enhanced stream callback for real-time updates
            async def stream_callback(chunk: str):
                await self.terminal_interface.stream_update(task.agent.id, chunk)

            # Prepare task context with intervention and conversation capabilities
            task_context = {
                "human_intervention": intervention,
                "agent_conversation_system": self.agent_conversation,
                "available_agents": {aid: agent.name for aid, agent in self.agents.items()},
                "conversation_history": self.agent_conversation.get_conversation_log()
            }

            # Execute the task with enhanced context
            result = await task.execute(
                stream_callback=stream_callback,
                context=task_context
            )

            # Process any agent messages from the result
            if hasattr(result, 'metadata') and result.metadata.get("agent_messages"):
                for msg in result.metadata["agent_messages"]:
                    try:
                        response = await self.send_agent_message(
                            task.agent.id,
                            msg["to_agent_id"],
                            msg["message"]
                        )
                        # Log the conversation
                        if response:
                            await self.terminal_interface.add_agent_conversation(
                                task.agent.id,
                                msg["to_agent_id"],
                                msg["message"],
                                response
                            )
                    except Exception as e:
                        # Log error but don't fail the task
                        self.execution_log.append({
                            "timestamp": datetime.now(),
                            "event": "agent_conversation_error",
                            "task_id": task_id,
                            "error": str(e)
                        })

            # Validate result before storing
            result_dict = {
                "success": result.success,
                "content": result.content,
                "metadata": result.metadata
            }

            # Determine result type for validation
            result_type = "general"
            if "web_search" in str(result.content).lower():
                result_type = "web_search"
            elif "file" in str(result.metadata).lower():
                result_type = "file_operation"
            elif "analysis" in str(result.content).lower():
                result_type = "data_analysis"

            # Validate result
            is_valid, validation_reason = self.result_validator.validate_result(result_dict, result_type)
            if not is_valid:
                # Mark as failed if validation fails
                result.success = False
                result.error = f"Validation failed: {validation_reason}"
                self.failed_tasks.append(task_id)
                await self.terminal_interface.update_task_status(task, "failed")

                # Record failed validation in performance monitor
                self.performance_monitor.fail_task(task_id, f"Validation failed: {validation_reason}")
            else:
                # Store successful result
                self.results[task_id] = result
                self.completed_tasks.append(task_id)

                # Update display
                await self.terminal_interface.update_task_status(task, "completed")

                # Record successful completion in performance monitor
                self.performance_monitor.complete_task(
                    task_id,
                    result_dict,
                    tokens_used=result.tokens_used,
                    tool_calls=getattr(result, 'tool_calls', 0)
                )

            # Log execution
            self.execution_log.append({
                "timestamp": datetime.now(),
                "event": "task_completed" if is_valid else "task_validation_failed",
                "task_id": task_id,
                "agent_name": task.agent.name,
                "execution_time": result.execution_time,
                "tokens_used": result.tokens_used,
                "validation_passed": is_valid,
                "validation_reason": validation_reason
            })

        except Exception as e:
            # Handle task failure
            self.failed_tasks.append(task_id)
            await self.terminal_interface.update_task_status(task, "failed")

            # Record failure in performance monitor
            self.performance_monitor.fail_task(task_id, str(e))

            self.execution_log.append({
                "timestamp": datetime.now(),
                "event": "task_failed",
                "task_id": task_id,
                "agent_name": task.agent.name,
                "error": str(e)
            })

            raise e

        finally:
            # Remove from current tasks
            if task_id in self.current_tasks:
                del self.current_tasks[task_id]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics for the team."""
        return self.performance_monitor.get_performance_summary()

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary for all results."""
        return self.result_validator.get_validation_summary()

    def save_performance_report(self, filepath: str = None) -> str:
        """Save detailed performance report to file."""
        if not filepath:
            filepath = f"team_performance_{self.session_name}.json"

        report = {
            "team_info": {
                "team_id": self.id,
                "session_name": self.session_name,
                "created_at": self.created_at.isoformat(),
                "agents": [{"id": agent.id, "name": agent.name} for agent in self.agents.values()],
                "tasks": [{"id": task.id, "description": task.description} for task in self.tasks.values()]
            },
            "performance_metrics": self.get_performance_metrics(),
            "validation_summary": self.get_validation_summary(),
            "execution_log": self.execution_log
        }

        import json
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return filepath

    async def connect_mcp_servers(self):
        """Connect to all configured MCP servers."""
        for server_params in self.mcp_server_params:
            try:
                adapter = MCPServerAdapter(server_params)
                await adapter.connect()
                self.mcp_adapters.append(adapter)

                # Add tools from this adapter
                for tool in adapter:
                    self.mcp_tools.append(tool)

                print(f"✅ Connected to MCP server: {len(adapter)} tools loaded")

            except Exception as e:
                print(f"❌ Failed to connect to MCP server: {e}")

    async def disconnect_mcp_servers(self):
        """Disconnect from all MCP servers."""
        for adapter in self.mcp_adapters:
            try:
                await adapter.disconnect()
            except Exception as e:
                print(f"Warning: Error disconnecting MCP server: {e}")

        self.mcp_adapters.clear()
        self.mcp_tools.clear()

    def get_mcp_tools(self, *tool_names: str) -> List[Any]:
        """
        Get MCP tools for agents.

        Args:
            *tool_names: Optional tool names to filter. If empty, returns all tools.

        Returns:
            List of MCP tools
        """
        if not tool_names:
            return self.mcp_tools.copy()

        filtered_tools = []
        for tool in self.mcp_tools:
            if tool.name in tool_names:
                filtered_tools.append(tool)

        return filtered_tools

    def _should_fail_team(self, failed_task_id: str) -> bool:
        """Determine if a failed task should cause the entire team to fail."""
        failed_task = self.tasks[failed_task_id]

        for task in self.tasks.values():
            if failed_task in task.depends_on and task.status == TaskStatus.PENDING:
                return True

        return False

    async def _generate_results(self) -> Dict[str, Any]:
        """Generate comprehensive execution results."""
        execution_time = (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0

        return {
            "success": self.status == TeamStatus.COMPLETED,
            "session_name": self.session_name,
            "execution_time": execution_time,
            "metrics": self._calculate_metrics(),
            "task_results": {tid: result.__dict__ for tid, result in self.results.items()},
            "agent_metrics": {aid: agent.get_status() for aid, agent in self.agents.items()},
            "execution_log": self.execution_log
        }

    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate team execution metrics."""
        self.metrics.total_tasks = len(self.tasks)
        self.metrics.completed_tasks = len(self.completed_tasks)
        self.metrics.failed_tasks = len(self.failed_tasks)
        self.metrics.agents_used = len(self.agents)

        if self.results:
            self.metrics.total_tokens_used = sum(r.tokens_used for r in self.results.values())
            self.metrics.total_execution_time = sum(r.execution_time for r in self.results.values())
            self.metrics.average_task_time = self.metrics.total_execution_time / len(self.results)

        return self.metrics.__dict__

    async def _generate_output_file(self, results: Dict[str, Any]):
        """Generate results.md file with final output and execution summary."""
        # Extract the final deliverable from task results
        final_output = self._extract_final_deliverable(results)

        output_content = f"""# AIFlow Execution Results
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Session**: {self.session_name}
**Duration**: {results['execution_time']:.2f}s
**Status**: {'✅ SUCCESS' if results['success'] else '❌ FAILED'}

## Final Output

{final_output}

## Executive Summary
Team execution {'completed successfully' if results['success'] else 'failed'} with {len(self.agents)} agents and {len(self.tasks)} tasks.

## Agent Performance
"""

        for agent_id, agent_metrics in results['agent_metrics'].items():
            agent = self.agents[agent_id]
            output_content += f"- **{agent.name}**: {agent_metrics['metrics']['tasks_completed']} tasks, {agent_metrics['metrics']['total_tokens_used']} tokens\n"

        output_content += f"""
## Task Results
"""

        for task_id, task_result in results['task_results'].items():
            task = self.tasks[task_id]
            output_content += f"""
### {task.description}...
- **Status**: {task_result['success']}
- **Agent**: {task_result['agent_name']}
- **Execution Time**: {task_result['execution_time']:.2f}s
- **Tokens Used**: {task_result['tokens_used']}

**Result**:
{task_result['content']}...

"""

        # Save to results.md
        output_file = Path("results.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)

        logger.info(f"Final results saved to {output_file}")

        # Also save raw final output to a separate file if it's substantial
        if len(final_output.strip()) > 100:
            final_output_file = Path(f"{self.session_name}_final_output.txt")
            with open(final_output_file, 'w', encoding='utf-8') as f:
                f.write(final_output)
            logger.info(f"Final output also saved to {final_output_file}")

    def _extract_final_deliverable(self, results: Dict[str, Any]) -> str:
        """Extract the final deliverable content from task results."""
        if not results.get('task_results'):
            return "No task results available."

        # Find the last completed task or the task with the most substantial output
        final_content = ""
        max_content_length = 0

        for task_id, task_result in results['task_results'].items():
            if isinstance(task_result, dict) and 'content' in task_result:
                content = str(task_result['content']).strip()
                if len(content) > max_content_length:
                    max_content_length = len(content)
                    final_content = content

        # If no substantial content found, create a summary
        if not final_content or len(final_content) < 50:
            task_summaries = []
            for task_id, task_result in results['task_results'].items():
                if isinstance(task_result, dict):
                    summary = f"Task {task_id}: {task_result.get('content', 'No content')[:100]}..."
                    task_summaries.append(summary)

            final_content = "## Task Execution Summary\n\n" + "\n\n".join(task_summaries)

        return final_content

    async def cleanup(self):
        """Cleanup team resources and remove database files."""
        for agent in self.agents.values():
            await agent.cleanup()
            # Remove database files if memory is enabled
            if hasattr(agent, 'memory_manager') and agent.memory_manager:
                try:
                    await agent.memory_manager.remove_database()
                except Exception:
                    pass  # Ignore cleanup errors

        await self.terminal_interface.cleanup()

    def get_status(self) -> Dict[str, Any]:
        """Get current team status and progress."""
        return {
            "id": self.id,
            "session_name": self.session_name,
            "status": self.status.value,
            "progress": {
                "total_tasks": len(self.tasks),
                "completed": len(self.completed_tasks),
                "failed": len(self.failed_tasks),
                "running": len(self.current_tasks)
            },
            "agents": [agent.get_status() for agent in self.agents.values()],
            "execution_time": (
                (datetime.now() - self.start_time).total_seconds()
                if self.start_time
                else 0
            )
        }

    async def send_agent_message(self, from_agent_id: str, to_agent_id: str, message: str) -> Optional[str]:
        """Send a message from one agent to another."""
        response = await self.agent_conversation.send_message(
            from_agent_id, to_agent_id, message
        )

        # Log the conversation in terminal interface
        if response:
            await self.terminal_interface.add_agent_conversation(
                from_agent_id, to_agent_id, message, response
            )

        return response

    def get_agent_conversations(self) -> List[Dict]:
        """Get all agent-to-agent conversations."""
        return self.agent_conversation.get_conversation_log()

    def get_human_interventions(self) -> List[Dict]:
        """Get all human interventions."""
        return self.human_intervention.get_intervention_history()

    async def request_human_approval(self, agent_name: str, task_description: str) -> bool:
        """Request human approval for a task."""
        return await self.human_intervention.request_approval(agent_name, task_description)

    def __repr__(self) -> str:
        return f"Team(name='{self.session_name}', agents={len(self.agents)}, tasks={len(self.tasks)}, status='{self.status.value}')"
