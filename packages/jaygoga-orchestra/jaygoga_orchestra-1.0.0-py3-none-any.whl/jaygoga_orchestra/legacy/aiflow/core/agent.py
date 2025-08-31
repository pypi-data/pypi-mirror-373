"""
Real Agent implementation for AIFlow multi-agent orchestrator.

Provides the core Agent class with real LLM integration and memory management.
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass

from ..providers.llm_providers import get_provider, LLMResponse
from ..storage.memory import MemoryManager
from ..tools.base_tool import BaseTool


@dataclass
class AgentConfig:
    """Configuration for Agent behavior."""
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 60
    memory_enabled: bool = True
    max_memory_context: int = 15000
    retry_attempts: int = 3
    retry_delay: float = 1.0


class Agent:
    """
    Core Agent class for AIFlow multi-agent orchestrator.
    
    An Agent represents an AI entity with specific capabilities and LLM provider.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        llm: Optional[Dict[str, str]] = None,
        llm_provider: Optional[str] = None,  # Backward compatibility
        api_key: Optional[str] = None,       # Backward compatibility
        memory_enabled: bool = True,
        tools: Optional[List[BaseTool]] = None,
        **kwargs
    ):
        """
        Initialize an Agent.

        Args:
            name: Unique name for the agent
            description: Description of agent's role
            llm: LLM configuration dict with keys:
                - model_provider: "openai", "google", or "anthropic"
                - model_name: specific model name (e.g., "gpt-4o", "gemini-2.0-flash-exp")
                - api_key: API key (optional, can use environment variables)
            llm_provider: (Deprecated) LLM provider name for backward compatibility
            api_key: (Deprecated) API key for backward compatibility
            memory_enabled: Enable memory system
            tools: List of BaseTool instances available to the agent
            **kwargs: Additional configuration
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_at = datetime.now()
        
        # Configuration
        self.config = AgentConfig(**kwargs)
        
        # Initialize LLM provider with new format
        try:
            if llm:
                # New format: llm = {"model_provider": "google", "model_name": "gemini-2.0-flash-exp", "api_key": "..."}
                model_name = llm.get("model_name", "gemini-2.0-flash-exp")
                llm_api_key = llm.get("api_key", None)

                # Use the model name directly (provider is determined by model name)
                self.llm_provider = get_provider(model_name, api_key=llm_api_key)
            else:
                # Backward compatibility: use old format
                model_string = llm_provider or "gemini-2.0-flash-exp"
                self.llm_provider = get_provider(model_string, api_key=api_key)
        except Exception as e:
            provider_info = llm if llm else llm_provider
            raise ValueError(f"Failed to initialize LLM provider '{provider_info}': {str(e)}")
        
        # Initialize memory system
        self.memory_manager = MemoryManager(
            agent_id=self.id,
            enabled=memory_enabled,
            max_context=self.config.max_memory_context
        ) if memory_enabled else None
        
        # Agent state
        self.status = "idle"
        self.current_task = None
        self.tools = tools or []
        self.tool_registry = {tool.name: tool for tool in self.tools} if self.tools else {}
        self.metrics = {
            "tasks_completed": 0,
            "total_tokens_used": 0,
            "average_response_time": 0.0,
            "error_count": 0
        }
        
        # Thread safety
        self._execution_lock = asyncio.Lock()
    
    async def execute_task(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """Execute a task with the agent."""
        async with self._execution_lock:
            self.status = "working"
            start_time = datetime.now()
            
            try:
                # Get memory context if enabled
                memory_context = ""
                if self.memory_manager:
                    memory_context = await self.memory_manager.get_context()

                # Handle human intervention if present
                enhanced_task = task_description
                if context and context.get("human_intervention"):
                    enhanced_task = f"{task_description}\n\nHuman Input: {context['human_intervention']}"

                # Add agent conversation capabilities to context
                conversation_context = ""
                if context and context.get("agent_conversation_system"):
                    available_agents = context.get("available_agents", {})
                    conversation_context = f"""
You can communicate with other agents in this team:
Available agents: {', '.join(available_agents.values())}

To send a message to another agent, include in your response:
AGENT_MESSAGE: [agent_name] | [your_message]

Recent conversations: {context.get("conversation_history", [])}
"""

                # Build complete prompt with tool information
                prompt = self._build_prompt(enhanced_task, context, memory_context, conversation_context)
                
                # Execute with LLM using new factory system
                llm_config = getattr(self.config, 'llm', {}) if hasattr(self.config, 'llm') else {}
                model_name = llm_config.get("model_name", "gpt-4o-mini")

                try:
                    from ..llm.factory import create_llm_client

                    # Create appropriate LLM client
                    llm_client = create_llm_client(model_name)

                    if stream_callback:
                        # Stream generation
                        content_parts = []
                        async for chunk in llm_client.stream_generate(
                            prompt=prompt,
                            temperature=llm_config.get("temperature", self.config.temperature),
                            max_tokens=llm_config.get("max_tokens", self.config.max_tokens),
                            system_prompt=self._build_system_prompt()
                        ):
                            content_parts.append(chunk)
                            stream_callback(chunk)

                        # Create result object
                        class StreamResult:
                            def __init__(self, content):
                                self.content = content

                        result = StreamResult("".join(content_parts))
                    else:
                        # Regular generation
                        llm_response = await llm_client.generate(
                            prompt=prompt,
                            temperature=llm_config.get("temperature", self.config.temperature),
                            max_tokens=llm_config.get("max_tokens", self.config.max_tokens),
                            system_prompt=self._build_system_prompt()
                        )

                        # Create result object compatible with existing code
                        class LLMResult:
                            def __init__(self, content):
                                self.content = content

                        result = LLMResult(llm_response.content)

                except Exception as e:
                    # Fallback to default behavior
                    if stream_callback:
                        result = await self.llm_provider.stream_generate(
                            prompt=prompt,
                            temperature=self.config.temperature,
                            max_tokens=self.config.max_tokens,
                            stream_callback=stream_callback
                        )
                    else:
                        result = await self.llm_provider.generate(
                            prompt=prompt,
                            temperature=self.config.temperature,
                            max_tokens=self.config.max_tokens
                        )
                
                # Process tool calls if present in response
                processed_content = result.content
                agent_messages = []

                # Check for tool calls in the response
                if self.tools and "TOOL_CALL:" in result.content:
                    processed_content = await self._process_tool_calls(result.content, stream_callback)

                # Process agent conversations if present in response

                if "AGENT_MESSAGE:" in result.content and context and context.get("agent_conversation_system"):
                    lines = result.content.split('\n')
                    filtered_lines = []

                    for line in lines:
                        if line.strip().startswith("AGENT_MESSAGE:"):
                            try:
                                message_part = line.split("AGENT_MESSAGE:")[1].strip()
                                if " | " in message_part:
                                    target_agent, message = message_part.split(" | ", 1)
                                    target_agent = target_agent.strip()
                                    message = message.strip()

                                    # Find target agent ID
                                    available_agents = context.get("available_agents", {})
                                    target_agent_id = None
                                    for aid, aname in available_agents.items():
                                        if aname.lower() == target_agent.lower():
                                            target_agent_id = aid
                                            break

                                    if target_agent_id:
                                        agent_messages.append({
                                            "to_agent_id": target_agent_id,
                                            "message": message
                                        })
                            except:
                                filtered_lines.append(line)
                        else:
                            filtered_lines.append(line)

                    processed_content = '\n'.join(filtered_lines)

                # Store in memory if enabled
                if self.memory_manager:
                    await self.memory_manager.store_interaction(
                        prompt=task_description,
                        response=processed_content,
                        context=context
                    )

                # Update metrics
                execution_time = (datetime.now() - start_time).total_seconds()
                self._update_metrics(result, execution_time)

                self.status = "idle"
                return {
                    "success": True,
                    "content": processed_content,
                    "agent_messages": agent_messages,
                    "metadata": {
                        "agent_id": self.id,
                        "agent_name": self.name,
                        "execution_time": execution_time,
                        "tokens_used": result.tokens_used,
                        "provider_used": result.provider
                    }
                }
                
            except Exception as e:
                self.status = "error"
                self.metrics["error_count"] += 1
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return {
                    "success": False,
                    "error": str(e),
                    "metadata": {
                        "agent_id": self.id,
                        "agent_name": self.name,
                        "execution_time": execution_time
                    }
                }

    def _build_system_prompt(self) -> str:
        """Build system prompt for the agent."""
        system_prompt = f"""You are {self.name}, a {self.role}.

Your goal: {self.goal}
Your background: {self.backstory}

You are a professional AI agent working as part of a team. Always provide high-quality, detailed responses that fulfill the task requirements. Be thorough, accurate, and helpful in your responses."""

        return system_prompt

    def _build_prompt(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]],
        memory_context: str,
        conversation_context: str = ""
    ) -> str:
        """Build the complete prompt for the LLM."""
        # Build tool information
        tool_info = ""
        if self.tools:
            tool_info = "Available tools:\n"
            for tool in self.tools:
                tool_info += f"- {tool.name}: {tool.description}\n"
            tool_info += "\nTo use a tool, include in your response: TOOL_CALL: tool_name(parameter=value)\n"

        prompt_parts = [
            f"You are {self.name}.",
            f"Role: {self.description}" if self.description else "",
            tool_info if self.tools else "",
            "",
            "Previous context:" if memory_context else "",
            memory_context,
            "",
            "Agent Communication:" if conversation_context else "",
            conversation_context,
            "",
            "Additional context:" if context else "",
            str(context) if context and not context.get("agent_conversation_system") else "",
            "",
            "Task:",
            task_description
        ]

        return "\n".join(filter(None, prompt_parts))

    async def _process_tool_calls(self, content: str, stream_callback=None) -> str:
        """Process tool calls in the agent's response."""
        import re

        # Find tool calls in the format: TOOL_CALL: tool_name(param=value)
        tool_pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
        matches = re.findall(tool_pattern, content)

        processed_content = content

        for tool_name, params_str in matches:
            if tool_name in self.tool_registry:
                try:
                    # Parse parameters
                    params = {}
                    if params_str.strip():
                        # Simple parameter parsing - in production use proper parser
                        for param in params_str.split(','):
                            if '=' in param:
                                key, value = param.split('=', 1)
                                params[key.strip()] = value.strip().strip('"\'')

                    # Execute tool
                    if stream_callback:
                        stream_callback(f"\n🔧 Executing tool: {tool_name}")

                    tool_result = await self.tool_registry[tool_name].execute(**params)

                    # Format result for inclusion in response
                    if tool_result.get('success'):
                        if tool_name == 'web_search' and 'results' in tool_result:
                            # Special formatting for web search results
                            formatted_results = self.tool_registry[tool_name].format_results_for_llm(tool_result['results'])
                            tool_output = f"\n\n--- Tool Result: {tool_name} ---\n{formatted_results}\n--- End Tool Result ---\n"
                        else:
                            tool_output = f"\n\n--- Tool Result: {tool_name} ---\n{tool_result}\n--- End Tool Result ---\n"
                    else:
                        tool_output = f"\n\n--- Tool Error: {tool_name} ---\n{tool_result.get('error', 'Unknown error')}\n--- End Tool Error ---\n"

                    # Replace the tool call with the result
                    tool_call_text = f"TOOL_CALL: {tool_name}({params_str})"
                    processed_content = processed_content.replace(tool_call_text, tool_output)

                    if stream_callback:
                        stream_callback(f"✅ Tool {tool_name} completed")

                except Exception as e:
                    error_output = f"\n\n--- Tool Error: {tool_name} ---\nError: {str(e)}\n--- End Tool Error ---\n"
                    tool_call_text = f"TOOL_CALL: {tool_name}({params_str})"
                    processed_content = processed_content.replace(tool_call_text, error_output)

                    if stream_callback:
                        stream_callback(f"❌ Tool {tool_name} failed: {str(e)}")

        return processed_content
    
    def _update_metrics(self, result: LLMResponse, execution_time: float):
        """Update agent performance metrics."""
        self.metrics["tasks_completed"] += 1
        self.metrics["total_tokens_used"] += result.tokens_used
        
        # Update average response time
        current_avg = self.metrics["average_response_time"]
        task_count = self.metrics["tasks_completed"]
        self.metrics["average_response_time"] = (
            (current_avg * (task_count - 1) + execution_time) / task_count
        )
    
    async def get_memory_summary(self) -> Optional[str]:
        """Get a summary of the agent's memory."""
        if not self.memory_manager:
            return None
        return await self.memory_manager.get_summary()
    
    async def clear_memory(self):
        """Clear the agent's memory."""
        if self.memory_manager:
            await self.memory_manager.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "current_task": self.current_task,
            "metrics": self.metrics.copy(),
            "provider": self.llm_provider.provider_name,
            "model": self.llm_provider.model,
            "tools": self.tools
        }
    
    async def cleanup(self):
        """Cleanup agent resources."""
        if self.memory_manager:
            await self.memory_manager.cleanup()
    
    def __repr__(self) -> str:
        return f"Agent(name='{self.name}', status='{self.status}', provider='{self.llm_provider.provider_name}')"
