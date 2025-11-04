"""
Chat Panel - Agent conversation window with typing simulation.

Displays agent messages with avatars, colors, and typing indicators.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
from collections import deque
from datetime import datetime
from typing import Deque, Dict, Optional
from rich.panel import Panel
from rich.console import Group
from rich.text import Text
from ..theme import theme_manager


class ChatMessage:
    """Represents a single chat message."""
    
    def __init__(self, agent: str, text: str, ts: str, phase: str, level: str):
        """
        Initialize chat message.
        
        Args:
            agent: Agent name
            text: Message text
            ts: Timestamp
            phase: Phase (plan/build/review/coord)
            level: Level (info/thought/action/result)
        """
        self.agent = agent
        self.text = text
        self.ts = ts
        self.phase = phase
        self.level = level


class ChatPanel:
    """
    Agent conversation window with typing simulation.
    """
    
    def __init__(self, max_messages: int = 100):
        """
        Initialize chat panel.
        
        Args:
            max_messages: Maximum messages to keep in buffer
        """
        self.max_messages = max_messages
        self.messages: Deque[ChatMessage] = deque(maxlen=max_messages)
        self.typing_agent: Optional[str] = None
        self.typing_start: Optional[float] = None
        self._cleared = False
    
    async def add_message(self, payload: Dict) -> None:
        """
        Add message with typing simulation.
        
        Args:
            payload: Message payload from event bus
        """
        agent = payload.get("agent", "System")
        text = payload.get("text", "")
        ts = payload.get("ts", datetime.now().isoformat())
        phase = payload.get("phase", "general")
        level = payload.get("level", "info")
        
        # Show typing indicator
        self.typing_agent = agent
        self.typing_start = asyncio.get_event_loop().time()
        
        # Simulate typing delay (250-600ms based on message length)
        delay = min(0.6, 0.25 + len(text) * 0.002)
        await asyncio.sleep(delay)
        
        # Add message
        message = ChatMessage(agent, text, ts, phase, level)
        self.messages.append(message)
        
        # Clear typing indicator
        self.typing_agent = None
        self.typing_start = None
        
        # Play sound cue (placeholder)
        await self._play_sound_cue(agent)
    
    async def _play_sound_cue(self, agent: str) -> None:
        """
        Placeholder for sound cue.
        
        Args:
            agent: Agent name
        """
        # Log sound cue indicator
        pass  # Could log: 🔔 [SFX] {agent}_message
    
    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
        self._cleared = True
    
    def __rich__(self) -> Panel:
        """
        Render as Rich panel.
        
        Returns:
            Rich Panel with chat messages
        """
        lines = []
        
        # Show recent messages (last 15 for visibility)
        recent_messages = list(self.messages)[-15:]
        
        for msg in recent_messages:
            # Get agent styling
            emoji = theme_manager.get_agent_emoji(msg.agent)
            color = theme_manager.get_agent_color(msg.agent)
            
            # Format timestamp
            try:
                ts_obj = datetime.fromisoformat(msg.ts)
                time_str = ts_obj.strftime("%H:%M:%S")
            except:
                time_str = "00:00:00"
            
            # Level indicator
            level_icon = {
                "info": "ℹ️",
                "thought": "💭",
                "action": "⚡",
                "result": "✅"
            }.get(msg.level, "•")
            
            # Build message line
            header = Text()
            header.append(f"[{time_str}] ", style=theme_manager.current["muted"])
            header.append(f"{emoji} ", style=color)
            header.append(f"{msg.agent}", style=f"bold {color}")
            header.append(f" {level_icon}", style=color)
            
            # Message content
            content = Text()
            content.append("  ", style="")
            content.append(msg.text[:200], style=color)  # Truncate long messages
            
            lines.append(header)
            lines.append(content)
            lines.append(Text(""))  # Spacing
        
        # Show typing indicator
        if self.typing_agent:
            typing_text = Text()
            emoji = theme_manager.get_agent_emoji(self.typing_agent)
            color = theme_manager.get_agent_color(self.typing_agent)
            
            # Animated ellipsis
            elapsed = asyncio.get_event_loop().time() - (self.typing_start or 0)
            dots = "." * (int(elapsed * 3) % 4)
            
            typing_text.append(f"{emoji} ", style=color)
            typing_text.append(f"{self.typing_agent} is typing", style=f"italic {color}")
            typing_text.append(dots, style=color)
            
            lines.append(typing_text)
        
        # If no messages
        if not lines:
            lines.append(Text("Waiting for agent activity...", style=theme_manager.current["muted"]))
        
        content = Group(*lines)
        
        return Panel(
            content,
            title="💬 Agent Conversation",
            border_style=theme_manager.current["border"],
            padding=(1, 2),
            height=None
        )
