"""
Message bus for inter-agent communication.
Handles priority-based message routing and delivery.
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import asdict

from ..core.types import Message, MessageType, TaskPriority, AgentRole


logger = logging.getLogger(__name__)


class MessageBus:
    """
    Priority-based message bus for inter-agent communication.
    Supports message routing, correlation, and delivery guarantees.
    """
    
    def __init__(self, max_queue_size: int = 1000, message_retention: int = 10000):
        """Initialize the message bus."""
        self.max_queue_size = max_queue_size
        self.message_retention = message_retention
        
        # Priority queues for different message types
        self.message_queues: Dict[str, Dict[TaskPriority, deque]] = defaultdict(
            lambda: {
                TaskPriority.CRITICAL: deque(),
                TaskPriority.HIGH: deque(),
                TaskPriority.MEDIUM: deque(),
                TaskPriority.LOW: deque()
            }
        )
        
        # Registered agents and their message handlers
        self.agents: Dict[str, Callable] = {}
        
        # Message history for debugging and correlation
        self.message_history: deque = deque(maxlen=message_retention)
        
        # Pending responses tracking
        self.pending_responses: Dict[str, asyncio.Future] = {}
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "messages_failed": 0,
            "average_delivery_time": 0.0,
            "queue_sizes": defaultdict(int)
        }
        
        # Control flags
        self.running = False
        self.delivery_task: Optional[asyncio.Task] = None
        
        logger.info("Message bus initialized")
    
    async def start(self):
        """Start the message bus delivery system."""
        if self.running:
            return
        
        self.running = True
        self.delivery_task = asyncio.create_task(self._delivery_loop())
        logger.info("Message bus started")
    
    async def stop(self):
        """Stop the message bus and cleanup resources."""
        if not self.running:
            return
        
        self.running = False
        
        if self.delivery_task:
            self.delivery_task.cancel()
            try:
                await self.delivery_task
            except asyncio.CancelledError:
                pass
        
        # Cancel pending responses
        for future in self.pending_responses.values():
            if not future.done():
                future.cancel()
        
        logger.info("Message bus stopped")
    
    def register_agent(self, agent_id: str, message_handler: Callable[[Message], Any]):
        """Register an agent with its message handler."""
        self.agents[agent_id] = message_handler
        logger.info(f"Agent registered: {agent_id}")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            # Clean up any pending messages
            if agent_id in self.message_queues:
                del self.message_queues[agent_id]
            logger.info(f"Agent unregistered: {agent_id}")
    
    async def send_message(self, message: Message) -> bool:
        """
        Send a message to the specified recipient.
        Returns True if message was queued successfully.
        """
        if not self.running:
            logger.warning("Message bus not running, cannot send message")
            return False
        
        if message.recipient not in self.agents:
            logger.warning(f"Recipient {message.recipient} not registered")
            return False
        
        # Check queue size limits
        total_queued = sum(
            len(q) for q in self.message_queues[message.recipient].values()
        )
        
        if total_queued >= self.max_queue_size:
            logger.warning(f"Queue full for recipient {message.recipient}")
            return False
        
        # Add to appropriate priority queue
        self.message_queues[message.recipient][message.priority].append(message)
        
        # Record in history
        self.message_history.append({
            "message_id": message.message_id,
            "sender": message.sender,
            "recipient": message.recipient,
            "message_type": message.message_type.value,
            "priority": message.priority.value,
            "timestamp": message.timestamp,
            "status": "queued"
        })
        
        self.stats["messages_sent"] += 1
        self.stats["queue_sizes"][message.recipient] = total_queued + 1
        
        logger.debug(f"Message queued: {message.message_id} from {message.sender} to {message.recipient}")
        
        return True
    
    async def send_request(self, message: Message, timeout: float = 30.0) -> Optional[Message]:
        """
        Send a request message and wait for response.
        Returns the response message or None if timeout.
        """
        if not message.requires_response:
            message.requires_response = True
        
        # Create future for response
        response_future = asyncio.Future()
        self.pending_responses[message.message_id] = response_future
        
        # Send the message
        sent = await self.send_message(message)
        if not sent:
            del self.pending_responses[message.message_id]
            return None
        
        try:
            # Wait for response with timeout
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            logger.warning(f"Request {message.message_id} timed out")
            return None
        finally:
            # Cleanup
            if message.message_id in self.pending_responses:
                del self.pending_responses[message.message_id]
    
    async def broadcast_message(self, message: Message, exclude: Set[str] = None) -> int:
        """
        Broadcast a message to all registered agents.
        Returns the number of agents the message was sent to.
        """
        if exclude is None:
            exclude = set()
        
        sent_count = 0
        
        for agent_id in self.agents:
            if agent_id not in exclude and agent_id != message.sender:
                # Create a copy for each recipient
                broadcast_msg = Message(
                    message_type=message.message_type,
                    sender=message.sender,
                    recipient=agent_id,
                    content=message.content.copy(),
                    priority=message.priority,
                    correlation_id=message.correlation_id
                )
                
                if await self.send_message(broadcast_msg):
                    sent_count += 1
        
        logger.info(f"Broadcast message sent to {sent_count} agents")
        return sent_count
    
    async def _delivery_loop(self):
        """Main delivery loop that processes queued messages."""
        while self.running:
            try:
                delivered_any = False
                
                # Process messages for each agent
                for agent_id, handler in self.agents.items():
                    if agent_id in self.message_queues:
                        message = self._get_next_message(agent_id)
                        if message:
                            await self._deliver_message(message, handler)
                            delivered_any = True
                
                # Short sleep if no messages were delivered
                if not delivered_any:
                    await asyncio.sleep(0.01)  # 10ms
                
            except Exception as e:
                logger.error(f"Error in delivery loop: {str(e)}")
                await asyncio.sleep(0.1)
    
    def _get_next_message(self, agent_id: str) -> Optional[Message]:
        """Get the next highest priority message for an agent."""
        queues = self.message_queues[agent_id]
        
        # Check in priority order
        for priority in [TaskPriority.CRITICAL, TaskPriority.HIGH, 
                        TaskPriority.MEDIUM, TaskPriority.LOW]:
            if queues[priority]:
                return queues[priority].popleft()
        
        return None
    
    async def _deliver_message(self, message: Message, handler: Callable):
        """Deliver a message to an agent's handler."""
        start_time = time.time()
        
        try:
            # Call the agent's message handler
            if asyncio.iscoroutinefunction(handler):
                response = await handler(message)
            else:
                response = handler(message)
            
            delivery_time = time.time() - start_time
            
            # Handle response if this was a request
            if message.requires_response and message.message_id in self.pending_responses:
                future = self.pending_responses[message.message_id]
                if not future.done():
                    if isinstance(response, Message):
                        future.set_result(response)
                    else:
                        # Create response message from handler result
                        response_msg = Message(
                            message_type=MessageType.TASK_RESPONSE,
                            sender=message.recipient,
                            recipient=message.sender,
                            content={"response": response} if response else {},
                            correlation_id=message.message_id
                        )
                        future.set_result(response_msg)
            
            # Update statistics
            self.stats["messages_delivered"] += 1
            self._update_average_delivery_time(delivery_time)
            
            # Update message history
            for hist_msg in reversed(self.message_history):
                if hist_msg["message_id"] == message.message_id:
                    hist_msg["status"] = "delivered"
                    hist_msg["delivery_time"] = delivery_time
                    break
            
            logger.debug(f"Message delivered: {message.message_id} in {delivery_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Failed to deliver message {message.message_id}: {str(e)}")
            
            # Handle failed request
            if message.requires_response and message.message_id in self.pending_responses:
                future = self.pending_responses[message.message_id]
                if not future.done():
                    future.set_exception(e)
            
            self.stats["messages_failed"] += 1
            
            # Update message history
            for hist_msg in reversed(self.message_history):
                if hist_msg["message_id"] == message.message_id:
                    hist_msg["status"] = "failed"
                    hist_msg["error"] = str(e)
                    break
    
    def _update_average_delivery_time(self, delivery_time: float):
        """Update running average of delivery times."""
        current_avg = self.stats["average_delivery_time"]
        delivered_count = self.stats["messages_delivered"]
        
        if delivered_count == 1:
            self.stats["average_delivery_time"] = delivery_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.stats["average_delivery_time"] = (
                alpha * delivery_time + (1 - alpha) * current_avg
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get message bus statistics."""
        current_queue_sizes = {}
        for agent_id, queues in self.message_queues.items():
            total_size = sum(len(q) for q in queues.values())
            if total_size > 0:
                current_queue_sizes[agent_id] = total_size
        
        return {
            "running": self.running,
            "registered_agents": len(self.agents),
            "messages_sent": self.stats["messages_sent"],
            "messages_delivered": self.stats["messages_delivered"],
            "messages_failed": self.stats["messages_failed"],
            "average_delivery_time": self.stats["average_delivery_time"],
            "current_queue_sizes": current_queue_sizes,
            "pending_responses": len(self.pending_responses),
            "message_history_size": len(self.message_history)
        }
    
    def get_message_history(self, agent_id: Optional[str] = None, 
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Get message history, optionally filtered by agent."""
        history = list(self.message_history)
        
        if agent_id:
            history = [
                msg for msg in history 
                if msg["sender"] == agent_id or msg["recipient"] == agent_id
            ]
        
        return history[-limit:]
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the message bus."""
        health = {
            "status": "healthy" if self.running else "stopped",
            "registered_agents": len(self.agents),
            "total_queue_size": sum(
                sum(len(q) for q in queues.values())
                for queues in self.message_queues.values()
            ),
            "pending_responses": len(self.pending_responses),
            "statistics": self.get_statistics()
        }
        
        # Check for potential issues
        issues = []
        
        if not self.running:
            issues.append("Message bus is not running")
        
        total_queue_size = health["total_queue_size"]
        if total_queue_size > self.max_queue_size * 0.8:
            issues.append(f"Queue sizes approaching limit: {total_queue_size}/{self.max_queue_size}")
        
        if len(self.pending_responses) > 50:
            issues.append(f"High number of pending responses: {len(self.pending_responses)}")
        
        health["issues"] = issues
        health["healthy"] = len(issues) == 0 and self.running
        
        return health


# Global message bus instance
_message_bus: Optional[MessageBus] = None


def initialize_message_bus(config: Dict[str, Any] = None) -> MessageBus:
    """Initialize the global message bus."""
    global _message_bus
    
    if config is None:
        config = {}
    
    _message_bus = MessageBus(
        max_queue_size=config.get("max_queue_size", 1000),
        message_retention=config.get("message_retention", 10000)
    )
    
    return _message_bus


def get_message_bus() -> MessageBus:
    """Get the global message bus instance."""
    if _message_bus is None:
        raise RuntimeError("Message bus not initialized. Call initialize_message_bus() first.")
    return _message_bus