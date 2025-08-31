"""
Performance Monitoring System for AIFlow.

Tracks real execution metrics, prevents hallucination, and validates results.
NO SIMULATION - Only real performance data.
"""

import time
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TaskMetrics:
    """Real task execution metrics."""
    task_id: str
    agent_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = False
    tokens_used: int = 0
    memory_usage: int = 0
    tool_calls: int = 0
    result_size: int = 0
    error_message: Optional[str] = None
    validation_passed: bool = False


@dataclass
class AgentMetrics:
    """Real agent performance metrics."""
    agent_id: str
    agent_name: str
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    total_tokens_used: int = 0
    average_response_time: float = 0.0
    success_rate: float = 0.0
    last_activity: Optional[float] = None


@dataclass
class TeamMetrics:
    """Real team performance metrics."""
    team_id: str
    session_name: str
    start_time: float
    end_time: Optional[float] = None
    total_duration: Optional[float] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    agents_used: int = 0
    total_tokens_used: int = 0
    peak_memory_usage: int = 0
    success_rate: float = 0.0
    files_created: List[str] = None
    api_calls_made: int = 0
    cache_hits: int = 0


class ResultValidator:
    """Validates results to prevent hallucination and simulation."""
    
    @staticmethod
    def is_real_output(result: Any) -> tuple[bool, str]:
        """
        Check if result is real output or simulation.
        
        Returns:
            (is_valid, reason)
        """
        # Check for simulation indicators
        sim_keywords = [
            'simulation', 'mock', 'placeholder', 'example', 'demo', 
            'fake', 'simulated', 'test data', 'sample', 'dummy'
        ]
        
        result_str = str(result).lower()
        
        # Check for simulation keywords
        for keyword in sim_keywords:
            if keyword in result_str:
                return False, f"Simulation detected: contains '{keyword}'"
        
        # Check for fake URLs
        fake_url_patterns = ['example.com', 'test.com', 'demo.com', 'placeholder.com']
        for pattern in fake_url_patterns:
            if pattern in result_str:
                return False, f"Fake URL detected: {pattern}"
        
        # Check for insufficient content
        if not result or len(str(result).strip()) < 10:
            return False, "No substantial output generated"
        
        # Check for generic responses
        generic_patterns = [
            'task completed successfully',
            'operation finished',
            'process complete',
            'done',
            'finished'
        ]
        
        if any(pattern in result_str for pattern in generic_patterns) and len(result_str) < 50:
            return False, "Generic response detected - likely simulation"
        
        return True, "Valid real output"
    
    @staticmethod
    def validate_file_operation(result: Dict[str, Any]) -> tuple[bool, str]:
        """Validate file operation results."""
        if not result.get('success'):
            return True, "Failed operation is valid"
        
        filepath = result.get('filepath')
        if not filepath:
            return False, "No filepath in file operation result"
        
        # Check if file actually exists for read/write operations
        operation = result.get('operation')
        if operation in ['write', 'read'] and not Path(filepath).exists():
            return False, f"File operation claimed success but file doesn't exist: {filepath}"
        
        # Check file size consistency
        if 'file_size' in result:
            actual_size = Path(filepath).stat().st_size if Path(filepath).exists() else 0
            claimed_size = result['file_size']
            if abs(actual_size - claimed_size) > 100:  # Allow small differences
                return False, f"File size mismatch: claimed {claimed_size}, actual {actual_size}"
        
        return True, "Valid file operation"
    
    @staticmethod
    def validate_web_search(result: Dict[str, Any]) -> tuple[bool, str]:
        """Validate web search results."""
        if not result.get('success'):
            return True, "Failed search is valid"
        
        results = result.get('results', [])
        if not results:
            return True, "Empty results are valid"
        
        # Check for fake URLs and demo data
        for item in results:
            url = item.get('url', '')
            source = item.get('source', '')
            
            if 'demo' in source.lower() or 'example.com' in url:
                return False, f"Demo/fake data detected in search results: {url}"
        
        return True, "Valid web search results"


class PerformanceMonitor:
    """
    Professional performance monitoring system.
    
    Tracks real execution metrics and prevents hallucination.
    """
    
    def __init__(self, session_name: str = None):
        """Initialize performance monitor."""
        self.session_name = session_name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = time.time()
        
        # Metrics storage
        self.task_metrics: Dict[str, TaskMetrics] = {}
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.team_metrics: Optional[TeamMetrics] = None
        
        # Validation
        self.validator = ResultValidator()
        
        # Performance tracking
        self.api_calls = 0
        self.cache_hits = 0
        self.files_created = []
        self.peak_memory = 0
    
    def start_task(self, task_id: str, agent_name: str) -> None:
        """Start tracking a task."""
        self.task_metrics[task_id] = TaskMetrics(
            task_id=task_id,
            agent_name=agent_name,
            start_time=time.time()
        )
    
    def complete_task(self, task_id: str, result: Dict[str, Any], 
                     tokens_used: int = 0, tool_calls: int = 0) -> None:
        """Complete task tracking with validation."""
        if task_id not in self.task_metrics:
            raise ValueError(f"Task {task_id} not found in metrics")
        
        metrics = self.task_metrics[task_id]
        metrics.end_time = time.time()
        metrics.duration = metrics.end_time - metrics.start_time
        metrics.success = result.get('success', False)
        metrics.tokens_used = tokens_used
        metrics.tool_calls = tool_calls
        metrics.result_size = len(str(result))
        
        # Validate result
        is_valid, reason = self.validator.is_real_output(result)
        metrics.validation_passed = is_valid
        
        if not is_valid:
            metrics.error_message = f"Validation failed: {reason}"
            metrics.success = False
        
        # Update agent metrics
        self._update_agent_metrics(metrics.agent_name, metrics)
    
    def fail_task(self, task_id: str, error: str) -> None:
        """Mark task as failed."""
        if task_id not in self.task_metrics:
            return
        
        metrics = self.task_metrics[task_id]
        metrics.end_time = time.time()
        metrics.duration = metrics.end_time - metrics.start_time
        metrics.success = False
        metrics.error_message = error
        metrics.validation_passed = True  # Failures are valid
        
        # Update agent metrics
        self._update_agent_metrics(metrics.agent_name, metrics)
    
    def _update_agent_metrics(self, agent_name: str, task_metrics: TaskMetrics) -> None:
        """Update agent performance metrics."""
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = AgentMetrics(
                agent_id=agent_name,  # Simplified for now
                agent_name=agent_name
            )
        
        agent = self.agent_metrics[agent_name]
        
        if task_metrics.success:
            agent.tasks_completed += 1
        else:
            agent.tasks_failed += 1
        
        agent.total_execution_time += task_metrics.duration or 0
        agent.total_tokens_used += task_metrics.tokens_used
        agent.last_activity = task_metrics.end_time
        
        # Calculate success rate
        total_tasks = agent.tasks_completed + agent.tasks_failed
        agent.success_rate = agent.tasks_completed / total_tasks if total_tasks > 0 else 0
        
        # Calculate average response time
        agent.average_response_time = agent.total_execution_time / total_tasks if total_tasks > 0 else 0
    
    def record_api_call(self) -> None:
        """Record an API call."""
        self.api_calls += 1
    
    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        self.cache_hits += 1
    
    def record_file_created(self, filepath: str) -> None:
        """Record a file creation."""
        self.files_created.append(filepath)
    
    def update_memory_usage(self, memory_bytes: int) -> None:
        """Update peak memory usage."""
        if memory_bytes > self.peak_memory:
            self.peak_memory = memory_bytes
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        current_time = time.time()
        total_duration = current_time - self.start_time
        
        # Calculate overall metrics
        total_tasks = len(self.task_metrics)
        completed_tasks = sum(1 for m in self.task_metrics.values() if m.success)
        failed_tasks = total_tasks - completed_tasks
        
        summary = {
            "session_name": self.session_name,
            "execution_summary": {
                "total_duration_seconds": round(total_duration, 2),
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(current_time).isoformat(),
                "status": "completed"
            },
            "task_metrics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
                "average_task_duration": sum(m.duration or 0 for m in self.task_metrics.values()) / total_tasks if total_tasks > 0 else 0
            },
            "resource_usage": {
                "total_tokens_used": sum(m.tokens_used for m in self.task_metrics.values()),
                "total_tool_calls": sum(m.tool_calls for m in self.task_metrics.values()),
                "api_calls_made": self.api_calls,
                "cache_hits": self.cache_hits,
                "peak_memory_usage_bytes": self.peak_memory
            },
            "files_generated": self.files_created,
            "agent_performance": {
                name: asdict(metrics) for name, metrics in self.agent_metrics.items()
            },
            "validation_summary": {
                "total_validations": total_tasks,
                "passed_validations": sum(1 for m in self.task_metrics.values() if m.validation_passed),
                "failed_validations": sum(1 for m in self.task_metrics.values() if not m.validation_passed),
                "validation_rate": sum(1 for m in self.task_metrics.values() if m.validation_passed) / total_tasks if total_tasks > 0 else 0
            }
        }
        
        return summary
    
    def save_metrics(self, filepath: str = None) -> str:
        """Save performance metrics to file."""
        if not filepath:
            filepath = f"performance_metrics_{self.session_name}.json"
        
        summary = self.get_performance_summary()
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return filepath
    
    def get_real_time_status(self) -> Dict[str, Any]:
        """Get real-time performance status."""
        active_tasks = [m for m in self.task_metrics.values() if m.end_time is None]
        
        return {
            "session_name": self.session_name,
            "uptime_seconds": round(time.time() - self.start_time, 2),
            "active_tasks": len(active_tasks),
            "completed_tasks": len([m for m in self.task_metrics.values() if m.success]),
            "failed_tasks": len([m for m in self.task_metrics.values() if not m.success and m.end_time is not None]),
            "current_memory_usage": self.peak_memory,
            "api_calls_made": self.api_calls,
            "files_created_count": len(self.files_created)
        }
