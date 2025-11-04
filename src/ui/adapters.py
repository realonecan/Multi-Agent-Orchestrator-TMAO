"""
Adapters - Bridge between agents and UI event bus.

Intercepts logs, progress updates, and metrics to publish UI events.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from .event_bus import event_bus


class UILogHandler(logging.Handler):
    """
    Logging handler that publishes log records to event bus.
    """
    
    def __init__(self):
        """Initialize UI log handler."""
        super().__init__()
        self.loop = None
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit log record to event bus.
        
        Args:
            record: Log record to emit
        """
        try:
            # Extract agent name from logger name if possible
            agent_name = "System"
            if hasattr(record, 'name') and ' - ' in record.name:
                parts = record.name.split(' - ')
                if len(parts) >= 2:
                    agent_name = parts[1]
            
            payload = {
                "level": record.levelname,
                "agent": agent_name,
                "message": self.format(record),
                "ts": datetime.now().isoformat()
            }
            
            # Publish to event bus (non-blocking)
            if self.loop is None:
                try:
                    self.loop = asyncio.get_event_loop()
                except RuntimeError:
                    return
            
            if self.loop and self.loop.is_running():
                asyncio.create_task(event_bus.publish("log", payload))
        
        except Exception:
            # Don't crash on logging errors
            pass


class ProgressAdapter:
    """
    Adapts agent progress updates to UI events.
    """
    
    @staticmethod
    async def publish_progress(phase: str, percent: float, detail: str = "") -> None:
        """
        Publish progress update.
        
        Args:
            phase: Phase name (plan/build/review)
            percent: Progress percentage (0-100)
            detail: Optional detail message
        """
        payload = {
            "phase": phase,
            "percent": percent,
            "detail": detail,
            "ts": datetime.now().isoformat()
        }
        await event_bus.publish(f"{phase}.progress", payload)
        await event_bus.publish("progress", payload)


class MetricsAdapter:
    """
    Collects and publishes system metrics.
    """
    
    def __init__(self):
        """Initialize metrics adapter."""
        self._metrics = {
            "accuracy": 0.0,
            "quality": 0.0,
            "final": 0.0,
            "memory_items": {
                "working": 0,
                "episodic": 0,
                "procedural": 0
            },
            "cache": {
                "size": 0,
                "hits": 0,
                "misses": 0
            }
        }
    
    async def update_scores(self, accuracy: float, quality: float, final: float) -> None:
        """
        Update score metrics.
        
        Args:
            accuracy: Accuracy score (0.0-1.0)
            quality: Quality score (0.0-1.0)
            final: Final score (0.0-1.0)
        """
        self._metrics["accuracy"] = accuracy
        self._metrics["quality"] = quality
        self._metrics["final"] = final
        await self._publish()
    
    async def update_memory_stats(self, working: int, episodic: int, procedural: int) -> None:
        """
        Update memory statistics.
        
        Args:
            working: Working memory item count
            episodic: Episodic memory item count
            procedural: Procedural memory item count
        """
        self._metrics["memory_items"] = {
            "working": working,
            "episodic": episodic,
            "procedural": procedural
        }
        await self._publish()
    
    async def update_cache_stats(self, size: int, hits: int, misses: int) -> None:
        """
        Update cache statistics.
        
        Args:
            size: Cache size
            hits: Cache hits
            misses: Cache misses
        """
        self._metrics["cache"] = {
            "size": size,
            "hits": hits,
            "misses": misses
        }
        await self._publish()
    
    async def _publish(self) -> None:
        """Publish current metrics."""
        await event_bus.publish("metrics.update", self._metrics.copy())
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        return self._metrics.copy()


class ChatAdapter:
    """
    Publishes agent chat messages to UI.
    """
    
    @staticmethod
    async def publish_message(
        agent: str,
        text: str,
        phase: str = "general",
        level: str = "info"
    ) -> None:
        """
        Publish chat message.
        
        Args:
            agent: Agent name
            text: Message text
            phase: Phase (plan/build/review/coord)
            level: Message level (info/thought/action/result)
        """
        payload = {
            "agent": agent,
            "text": text,
            "ts": datetime.now().isoformat(),
            "phase": phase,
            "level": level
        }
        await event_bus.publish("chat", payload)


# Global adapter instances
metrics_adapter = MetricsAdapter()


# Convenience functions for agent integration
async def publish_chat(agent: str, text: str, phase: str = "general", level: str = "info") -> None:
    """
    Convenience function to publish chat message.
    
    Args:
        agent: Agent name
        text: Message text
        phase: Phase (plan/build/review/coord/general)
        level: Level (info/thought/action/result)
    """
    await ChatAdapter.publish_message(agent, text, phase, level)


async def publish_progress(phase: str, percent: float, detail: str = "") -> None:
    """
    Convenience function to publish progress.
    
    Args:
        phase: Phase name (plan/build/review)
        percent: Progress percentage (0-100)
        detail: Optional detail message
    """
    await ProgressAdapter.publish_progress(phase, percent, detail)


async def publish_metrics(metrics: Dict[str, Any]) -> None:
    """
    Convenience function to publish metrics.
    
    Args:
        metrics: Metrics dict with accuracy, quality, final, etc.
    """
    if "accuracy" in metrics and "quality" in metrics and "final" in metrics:
        await metrics_adapter.update_scores(
            metrics["accuracy"],
            metrics["quality"],
            metrics["final"]
        )
    
    if "memory_items" in metrics:
        mem = metrics["memory_items"]
        await metrics_adapter.update_memory_stats(
            mem.get("working", 0),
            mem.get("episodic", 0),
            mem.get("procedural", 0)
        )
    
    if "cache" in metrics:
        cache = metrics["cache"]
        await metrics_adapter.update_cache_stats(
            cache.get("size", 0),
            cache.get("hits", 0),
            cache.get("misses", 0)
        )
