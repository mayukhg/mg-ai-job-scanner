# src/analyzer/a2a_messaging.py
# =====================================================================
# mg-ai-job-scanner — Agent-to-Agent (A2A) Messaging Architecture
# =====================================================================

import uuid
import datetime
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

logger = logging.getLogger("a2a.messaging")

class AgentMessage:
    """Standardized event envelope exchanged between CIE agents."""
    def __init__(self, event_type: str, sender_id: str, payload: Dict[str, Any], recipient_id: str = "broadcast"):
        self.message_id = f"msg_{uuid.uuid4().hex[:8]}"
        self.event_type = event_type
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.payload = payload
        self.timestamp = datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "event_type": self.event_type,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "payload": self.payload,
            "timestamp": self.timestamp
        }

class AgentEventBus:
    """Coordinates routing of AgentMessage envelopes to registered CIE agents."""
    def __init__(self):
        self._subscribers: Dict[str, List[Any]] = {}
        self._agents: Dict[str, Any] = {}

    def register_agent(self, agent: Any):
        """Registers a physical agent instance for direct message routing."""
        self._agents[agent.agent_id] = agent
        logger.info(f"Registered agent '{agent.agent_id}' to Event Bus.")

    def subscribe(self, event_type: str, agent: Any):
        """Subscribes an agent to specific broadcast event types."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if agent not in self._subscribers[event_type]:
            self._subscribers[event_type].append(agent)
            logger.info(f"Agent '{agent.agent_id}' subscribed to event: {event_type}")

    def send_direct(self, message: AgentMessage):
        """Routes a message directly to a specific target recipient agent."""
        recipient = self._agents.get(message.recipient_id)
        if recipient:
            logger.info(f"[A2A DIRECT] {message.sender_id} -> {message.recipient_id} | Event: {message.event_type}")
            recipient.on_message(message)
        else:
            logger.warning(f"Failed direct route: Recipient agent '{message.recipient_id}' not online.")

    def publish(self, message: AgentMessage):
        """Broadcasts a message to all agents subscribed to this event type."""
        subscribers = self._subscribers.get(message.event_type, [])
        if not subscribers:
            logger.debug(f"Broadcast event '{message.event_type}' has no active subscribers.")
            return
            
        logger.info(f"[A2A BROADCAST] {message.sender_id} -> Subscribers | Event: {message.event_type}")
        for sub in subscribers:
            if sub.agent_id != message.sender_id:  # Avoid self-routing loop
                sub.on_message(message)

class BaseAgent(ABC):
    """Abstract baseline class equipping CIE agents with A2A communication capabilities."""
    def __init__(self, agent_id: str, event_bus: AgentEventBus):
        self.agent_id = agent_id
        self.event_bus = event_bus
        self.event_bus.register_agent(self)

    def send_message(self, recipient_id: str, event_type: str, payload: Dict[str, Any]):
        """Sends a direct, point-to-point message to another agent."""
        msg = AgentMessage(event_type, self.agent_id, payload, recipient_id)
        self.event_bus.send_direct(msg)

    def publish_event(self, event_type: str, payload: Dict[str, Any]):
        """Broadcasts an event envelope to all subscribed agents."""
        msg = AgentMessage(event_type, self.agent_id, payload)
        self.event_bus.publish(msg)

    @abstractmethod
    def on_message(self, message: AgentMessage):
        """Abstract execution handler triggered upon receiving an AgentMessage."""
        pass
