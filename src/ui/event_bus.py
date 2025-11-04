"""
Event Bus - Lightweight pub/sub for UI <-> Agent communication.

Provides async event publishing and subscription without tight coupling.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
from typing import Any, Callable, Dict, List
from collections import defaultdict


class EventBus:
    """
    Lightweight async event bus for decoupled communication.
    
    Supports topic-based pub/sub with async callbacks.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def subscribe(self, topic: str, callback: Callable) -> None:
        """
        Subscribe to a topic.
        
        Args:
            topic: Event topic to subscribe to
            callback: Async callback function(payload)
        """
        async with self._lock:
            if callback not in self._subscribers[topic]:
                self._subscribers[topic].append(callback)
    
    async def unsubscribe(self, topic: str, callback: Callable) -> None:
        """
        Unsubscribe from a topic.
        
        Args:
            topic: Event topic to unsubscribe from
            callback: Callback to remove
        """
        async with self._lock:
            if callback in self._subscribers[topic]:
                self._subscribers[topic].remove(callback)
    
    async def publish(self, topic: str, payload: Any = None) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            topic: Event topic
            payload: Event data (dict recommended)
        """
        async with self._lock:
            subscribers = self._subscribers[topic].copy()
        
        # Call subscribers without holding lock
        for callback in subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(payload)
                else:
                    callback(payload)
            except Exception as e:
                # Log but don't crash on subscriber errors
                pass
    
    def clear(self) -> None:
        """Clear all subscriptions."""
        self._subscribers.clear()


# Global event bus instance
event_bus = EventBus()
