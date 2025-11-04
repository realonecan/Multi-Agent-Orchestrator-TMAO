"""
Base Agent Module for Terminal Multi-Agent Orchestrator.

This module provides the BaseAgent class that all specialized agents inherit from.
It establishes the common interface and functionality for agent collaboration,
memory management, and task processing.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import logging
import traceback
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set

# Try to import rich for beautiful terminal output, fallback to standard logging
try:
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

from src.core.memory import MemoryManager, MemoryType


# ================================
# BASE AGENT CLASS
# ================================
class BaseAgent(ABC):
    """
    Base class for all TMAO agents.

    This abstract class provides the common functionality and interface
    that all specialized agents (Planner, Builder, Reviewer, etc.) must implement.
    It handles memory management, logging, and inter-agent communication.

    Attributes:
        name: Unique identifier for the agent
        role: Human-readable description of the agent's purpose
        memory: Instance of MemoryManager for persistent storage
        config: Configuration dictionary for agent-specific settings
    """

    def __init__(
        self,
        name: str,
        role: str,
        config: Optional[Dict[str, Any]] = None,
        shared_memory: Optional[MemoryManager] = None
    ):
        """
        Initialize the base agent.

        Args:
            name: Unique name for this agent instance
            role: Description of the agent's role/purpose
            config: Optional configuration dictionary
            shared_memory: Optional shared MemoryManager instance for multi-agent coordination
        """
        self.name = name
        self.role = role
        self.memory = shared_memory if shared_memory is not None else MemoryManager()
        self.config = config or {}

        # Rich console for beautiful terminal output (fallback to standard logging)
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None

        # Configure logging
        self._setup_logging(config)

        # Agent state
        self._active = False
        self._current_task: Optional[str] = None

    def _setup_logging(self, config: Dict[str, Any]) -> None:
        """
        Configure logging for this agent.

        Args:
            config: Configuration dictionary that may contain logging settings
        """
        # Get logging configuration
        log_config = config.get("logging", {})

        # Set up standard Python logging
        self.logger = logging.getLogger(f"agent.{self.name}")

        # Configure log level
        log_level = log_config.get("level", "INFO").upper()
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))

        # Only add handler if none exists (avoid duplicate handlers)
        if not self.logger.handlers:
            # Create console handler for fallback logging
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - {self.name} - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # Attach UI log handler to publish logs to event bus (if available)
        try:
            from src.ui.adapters import UILogHandler
            if not any(isinstance(h, UILogHandler) for h in self.logger.handlers):
                self.logger.addHandler(UILogHandler())
        except Exception:
            # UI not available or import failed; proceed without UI handler
            pass

        # Disable propagation to avoid duplicate logs
        self.logger.propagate = False

    async def process_task(self, task: str, context: Dict[str, Any]) -> str:
        """
        Process a task assigned to this agent.

        This is the main method that specialized agents must implement.
        It contains the core logic for handling tasks specific to each agent type.

        Args:
            task: The task description or instruction
            context: Additional context data for task processing

        Returns:
            The result or output from task processing

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement process_task method")

    # ================================
    # CORE FUNCTIONALITY
    # ================================

    async def initialize(self) -> None:
        """
        Initialize the agent and prepare for task processing.

        This method is called before the agent starts processing tasks.
        Subclasses can override this for custom initialization logic.
        """
        self._active = True
        await self.log(f"{self.name} ({self.role}) initialized", style="success")

    async def shutdown(self) -> None:
        """
        Clean up resources and shutdown the agent.

        This method is called when the agent is no longer needed.
        Subclasses should call super().shutdown() after their cleanup.
        """
        self._active = False
        await self.log(f"{self.name} shutting down", style="info")

    async def communicate_with_agent(self, other_agent: 'BaseAgent', message: str) -> str:
        """
        Communicate with another agent in the system.

        This method facilitates inter-agent communication by storing
        the message in shared memory and optionally triggering the
        other agent's attention mechanism.

        Args:
            other_agent: The target agent to communicate with
            message: The message content to send

        Returns:
            Response from the other agent if applicable
        """
        # Store communication in memory
        await self.memory.store(
            content=message,
            memory_type=MemoryType.EPISODIC,
            metadata={
                "from_agent": self.name,
                "to_agent": other_agent.name,
                "message_type": "inter_agent_communication"
            },
            tags={"communication", self.name, other_agent.name}
        )

        await self.log(f"→ {other_agent.name}: {message[:50]}...")

        # In a more sophisticated system, this could trigger the other agent's
        # attention or queue the message for processing
        return f"Message sent to {other_agent.name}"

    async def log(self, message: str, style: str = "info") -> None:
        """
        Log a message with appropriate styling.

        This method provides a consistent logging interface for all agents,
        using standard Python logging for reliable terminal output.

        Args:
            message: The message to log
            style: The style of the message (info, success, warning, error)
        """
        # Map styles to log levels
        if style == "error":
            self.logger.error(message)
        elif style == "warning":
            self.logger.warning(message)
        elif style in ["success", "action", "thought", "result"]:
            self.logger.info(f"[{style.upper()}] {message}")
        else:
            self.logger.info(message)

        # Also store in memory for persistence
        await self.memory.store(
            content=message,
            memory_type=MemoryType.EPISODIC,
            metadata={
                "agent": self.name,
                "log_style": style,
                "current_task": self._current_task
            },
            tags={"log", style, self.name}
        )

    async def update_task_progress(self, progress: float, status: str = "") -> None:
        """
        Update the current task's progress.

        Args:
            progress: Progress value between 0.0 and 1.0
            status: Optional status message
        """
        self._current_task = f"{progress:.1%} - {status}" if status else f"{progress:.1%}"

        await self.log(
            f"Progress: {progress:.1%} - {status}",
            style="info"
        )

    async def handle_error(self, error: Exception, context: str = "") -> None:
        """
        Handle errors in a consistent manner.

        Args:
            error: The exception that occurred
            context: Additional context about where the error happened
        """
        error_message = f"Error in {context}: {str(error)}" if context else str(error)
        error_traceback = traceback.format_exc()

        await self.log(error_message, style="error")

        # Store error in memory for analysis with full traceback
        await self.memory.store(
            content={
                "error_message": str(error),
                "error_type": type(error).__name__,
                "context": context,
                "traceback": error_traceback,
                "timestamp": asyncio.get_event_loop().time()
            },
            memory_type=MemoryType.EPISODIC,
            metadata={
                "agent": self.name,
                "error_type": type(error).__name__,
                "context": context,
                "has_traceback": bool(error_traceback)
            },
            tags={"error", self.name, type(error).__name__}
        )

    # ================================
    # UTILITY METHODS
    # ================================

    async def search_memory(
        self,
        query_text: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search the agent's memory for relevant information.

        Args:
            query_text: The search query
            memory_type: Optional filter by memory type
            limit: Maximum number of results to return

        Returns:
            List of memory items matching the query
        """
        from src.core.memory import MemoryQuery

        query = MemoryQuery(
            text=query_text,
            memory_type=memory_type,
            limit=limit
        )

        results = await self.memory.retrieve(query)

        # Convert to simple dict format for easier consumption
        return [
            {
                "id": item.id,
                "content": item.content,
                "metadata": item.metadata,
                "tags": item.tags,
                "created_at": item.created_at.isoformat()
            }
            for item in results
        ]

    async def store_result(self, result: Any, tags: Optional[Set[str]] = None) -> str:
        """
        Store a task result in memory.

        Args:
            result: The result data to store
            tags: Optional tags for categorization

        Returns:
            The memory ID of the stored result
        """
        memory_id = await self.memory.store(
            content=result,
            memory_type=MemoryType.WORKING,
            metadata={
                "agent": self.name,
                "task_result": True,
                "current_task": self._current_task
            },
            tags=(tags or set()) | {"result", self.name}
        )

        await self.log(f"Stored result in memory: {memory_id[:8]}")
        return memory_id

    def is_active(self) -> bool:
        """
        Check if the agent is currently active.

        Returns:
            True if the agent is active, False otherwise
        """
        return self._active

    def get_capabilities(self) -> List[str]:
        """
        Get the agent's capabilities.

        This method should be overridden by subclasses to specify
        what types of tasks this agent can handle.

        Returns:
            List of capability strings
        """
        return self.config.get("capabilities", [])

    # ================================
    # CONTEXT MANAGEMENT
    # ================================

    async def get_context(self, context_keys: List[str]) -> Dict[str, Any]:
        """
        Retrieve context information from memory.

        Args:
            context_keys: List of context keys to retrieve

        Returns:
            Dictionary of context data
        """
        context_data = {}

        for key in context_keys:
            # Search for context with the specific key
            results = await self.search_memory(f"context:{key}", limit=1)
            if results:
                context_data[key] = results[0]["content"]

        return context_data

    async def set_context(self, context_data: Dict[str, Any]) -> None:
        """
        Store context information in memory.

        Args:
            context_data: Dictionary of context data to store
        """
        for key, value in context_data.items():
            await self.memory.store(
                content=value,
                memory_type=MemoryType.WORKING,
                metadata={
                    "context_key": key,
                    "agent": self.name
                },
                tags={"context", key, self.name}
            )

        await self.log(f"Updated context: {list(context_data.keys())}")

    # ================================
    # ASYNC SUPPORT
    # ================================

    async def sleep(self, seconds: float) -> None:
        """
        Async sleep utility.

        Args:
            seconds: Number of seconds to sleep
        """
        await asyncio.sleep(seconds)

    async def timeout(self, coroutine, timeout_seconds: float):
        """
        Execute a coroutine with a timeout.

        Args:
            coroutine: The async function to execute
            timeout_seconds: Maximum time to wait

        Returns:
            Result of the coroutine or raises asyncio.TimeoutError
        """
        try:
            return await asyncio.wait_for(coroutine, timeout=timeout_seconds)
        except asyncio.TimeoutError:
            await self.log(f"Operation timed out after {timeout_seconds}s", style="warning")
            raise
