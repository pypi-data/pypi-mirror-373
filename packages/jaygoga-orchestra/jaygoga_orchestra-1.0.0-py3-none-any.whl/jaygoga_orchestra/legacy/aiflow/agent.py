"""
AIFlow Agent - Govinda Compatible Interface
"""

import os
from typing import List, Optional, Dict, Any
from .core.agent import Agent as CoreAgent

class Agent:
    """Govinda-compatible Agent class for AIFlow."""
    
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        verbose: bool = True,
        allow_delegation: bool = False,
        tools: Optional[List] = None,
        llm: Optional[str] = None,
        max_iter: int = 10,
        memory: bool = True,
        step_callback: Optional[callable] = None,
        system_template: Optional[str] = None,
        prompt_template: Optional[str] = None,
        response_template: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Agent with Govinda-compatible interface.
        
        Args:
            role: The role of the agent
            goal: The goal of the agent
            backstory: The backstory of the agent
            verbose: Whether to print verbose output
            allow_delegation: Whether to allow delegation to other agents
            tools: List of tools available to the agent
            llm: LLM model to use (auto-detected from environment)
            max_iter: Maximum iterations for task execution
            memory: Whether to use memory
            step_callback: Callback function for each step
            system_template: Custom system template
            prompt_template: Custom prompt template
            response_template: Custom response template
        """
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose
        self.allow_delegation = allow_delegation
        self.tools = tools or []
        self.max_iter = max_iter
        self.memory = memory
        self.step_callback = step_callback
        self.system_template = system_template
        self.prompt_template = prompt_template
        self.response_template = response_template
        
        # Auto-detect LLM from environment
        self.llm = llm or self._detect_llm()
        
        # Create internal CoreAgent
        self._core_agent = CoreAgent(
            name=role.replace(' ', '_').lower(),
            role=role,
            goal=goal,
            backstory=backstory,
            config={
                "llm": {
                    "model_name": self.llm,
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 2000)
                },
                "verbose": verbose,
                "memory": memory,
                "tools": tools
            }
        )
    
    def _detect_llm(self) -> str:
        """Auto-detect LLM based on available API keys."""
        if os.getenv("OPENAI_API_KEY"):
            return "gpt-4o-mini"
        elif os.getenv("ANTHROPIC_API_KEY"):
            return "claude-3-5-sonnet-20241022"
        elif os.getenv("GOOGLE_API_KEY"):
            return "gemini-2.5-flash"
        elif os.getenv("GROQ_API_KEY"):
            return "llama-3.1-70b-versatile"
        else:
            # Default to OpenAI (user will need to set API key)
            return "gpt-4o-mini"
    
    @property
    def id(self):
        """Get agent ID."""
        return self._core_agent.id
    
    @property
    def name(self):
        """Get agent name."""
        return self._core_agent.name
    
    def __str__(self):
        return f"Agent(role='{self.role}', goal='{self.goal[:50]}...')"
    
    def __repr__(self):
        return self.__str__()
