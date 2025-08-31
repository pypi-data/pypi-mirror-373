"""
Human intervention and agent conversation system for AIFlow.

Provides real-time human input capabilities and agent-to-agent communication.
"""

import asyncio
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class InterventionRequest:
    """Represents a human intervention request."""
    agent_name: str
    task_description: str
    timestamp: datetime
    intervention_type: str  # 'approval', 'guidance', 'modification'
    response: Optional[str] = None
    approved: Optional[bool] = None


class HumanIntervention:
    """
    Human intervention system for real-time guidance and approval.
    
    Allows humans to provide input, guidance, and approval during agent execution.
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize human intervention system."""
        self.enabled = enabled
        self.intervention_history: List[InterventionRequest] = []
        self.pending_requests: Dict[str, InterventionRequest] = {}
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = False
    
    def start_monitoring(self):
        """Start monitoring for intervention requests."""
        if not self.enabled:
            return
        
        self.monitoring = True
        self._stop_monitoring = False
        
        def monitor_loop():
            while not self._stop_monitoring:
                try:
                    # Check for pending requests and handle them
                    self._process_pending_requests()
                    import time; time.sleep(0.5)
                except Exception:
                    # Silently handle monitoring errors
                    continue
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring for intervention requests."""
        self._stop_monitoring = True
        self.monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
    
    async def check_intervention(
        self,
        agent_name: str,
        task_description: str
    ) -> Optional[str]:
        """Check if human intervention is needed for a task."""
        if not self.enabled:
            return None
        
        # For now, return None - intervention is handled through terminal interface
        # This can be extended to include automatic intervention triggers
        return None
    
    async def request_approval(
        self,
        agent_name: str,
        task_description: str
    ) -> bool:
        """Request human approval for a task."""
        if not self.enabled:
            return True
        
        request = InterventionRequest(
            agent_name=agent_name,
            task_description=task_description,
            timestamp=datetime.now(),
            intervention_type="approval"
        )
        
        # Add to pending requests
        request_id = f"{agent_name}_{datetime.now().timestamp()}"
        self.pending_requests[request_id] = request
        
        # Wait for response (with timeout)
        timeout = 30  # 30 seconds timeout
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout:
            if request.approved is not None:
                self.intervention_history.append(request)
                return request.approved
            await asyncio.sleep(0.5)
        
        # Timeout - default to approved
        request.approved = True
        self.intervention_history.append(request)
        return True
    
    def provide_guidance(
        self,
        agent_name: str,
        guidance: str
    ):
        """Provide guidance to an agent."""
        if not self.enabled:
            return
        
        request = InterventionRequest(
            agent_name=agent_name,
            task_description="Human guidance provided",
            timestamp=datetime.now(),
            intervention_type="guidance",
            response=guidance
        )
        
        self.intervention_history.append(request)
    
    def get_intervention_history(self) -> List[Dict[str, Any]]:
        """Get the history of all interventions."""
        return [
            {
                "agent_name": req.agent_name,
                "task_description": req.task_description,
                "timestamp": req.timestamp,
                "type": req.intervention_type,
                "response": req.response,
                "approved": req.approved
            }
            for req in self.intervention_history
        ]
    
    def _process_pending_requests(self):
        """Process pending intervention requests."""
        # This would be extended to handle UI interactions
        # For now, it's a placeholder for future implementation
        # Process any pending approval requests
        for request_id, request in list(self.pending_requests.items()):
            # Auto-approve after timeout for demo purposes
            # In a real implementation, this would check for user input
            if (datetime.now() - request.timestamp).total_seconds() > 30:
                request.approved = True
                del self.pending_requests[request_id]


class AgentConversation:
    """
    Agent-to-agent conversation system.
    
    Enables agents to communicate with each other during task execution.
    """
    
    def __init__(self):
        """Initialize agent conversation system."""
        self.agents: Dict[str, Any] = {}  # agent_id -> agent instance
        self.conversation_log: List[Dict[str, Any]] = []
        self.active_conversations: Dict[str, List[Dict]] = {}  # agent_id -> conversations
    
    def register_agent(self, agent_id: str, agent: Any):
        """Register an agent for conversations."""
        self.agents[agent_id] = agent
        self.active_conversations[agent_id] = []
    
    async def send_message(
        self,
        from_agent_id: str,
        to_agent_id: str,
        message: str
    ) -> Optional[str]:
        """Send a message from one agent to another."""
        if from_agent_id not in self.agents or to_agent_id not in self.agents:
            return None
        
        from_agent = self.agents[from_agent_id]
        to_agent = self.agents[to_agent_id]
        
        # Create conversation entry
        conversation_entry = {
            "timestamp": datetime.now(),
            "from_agent_id": from_agent_id,
            "from_agent_name": from_agent.name,
            "to_agent_id": to_agent_id,
            "to_agent_name": to_agent.name,
            "message": message,
            "response": None
        }
        
        try:
            # Generate response from target agent
            response_prompt = f"""
You are {to_agent.name}. Another agent ({from_agent.name}) is asking you:

"{message}"

Please provide a helpful response based on your expertise and role.
Keep your response concise and focused.
"""
            
            # Execute with the target agent
            result = await to_agent.execute_task(
                task_description=response_prompt,
                context={"conversation": True, "from_agent": from_agent.name}
            )
            
            if result.get("success"):
                response = result.get("content", "")
                conversation_entry["response"] = response
                
                # Log the conversation
                self.conversation_log.append(conversation_entry)
                
                # Add to active conversations for both agents
                self.active_conversations[from_agent_id].append(conversation_entry)
                self.active_conversations[to_agent_id].append(conversation_entry)
                
                return response
            
        except Exception as e:
            conversation_entry["response"] = f"Error: {str(e)}"
            self.conversation_log.append(conversation_entry)
        
        return None
    
    def get_conversation_log(self) -> List[Dict[str, Any]]:
        """Get the complete conversation log."""
        return self.conversation_log.copy()
    
    def get_agent_conversations(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get conversations for a specific agent."""
        return self.active_conversations.get(agent_id, []).copy()
    
    def clear_conversations(self):
        """Clear all conversation history."""
        self.conversation_log.clear()
        for agent_conversations in self.active_conversations.values():
            agent_conversations.clear()


# Utility functions for intervention management
async def wait_for_human_input(
    prompt: str,
    timeout: int = 30
) -> Optional[str]:
    """Wait for human input with a timeout."""
    try:
        # This would be implemented with actual UI components
        # For now, it's a placeholder
        return None
    except asyncio.TimeoutError:
        return None


def create_intervention_context(
    agent_name: str,
    task_description: str,
    available_actions: List[str]
) -> Dict[str, Any]:
    """Create context for human intervention."""
    return {
        "agent_name": agent_name,
        "task_description": task_description,
        "available_actions": available_actions,
        "timestamp": datetime.now(),
        "intervention_type": "context"
    }
