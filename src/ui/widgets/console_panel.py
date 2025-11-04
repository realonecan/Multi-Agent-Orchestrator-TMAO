"""
Console Panel - Streaming logs with filtering.

Displays system logs with level filtering and agent coloring.

Author: TMAO Dev Team
License: MIT
"""

from collections import deque
from typing import Deque, Dict, Set
from rich.panel import Panel
from rich.console import Group
from rich.text import Text
from ..theme import theme_manager


class ConsolePanel:
    """
    Streaming console with log filtering.
    """
    
    def __init__(self, max_logs: int = 100):
        """
        Initialize console panel.
        
        Args:
            max_logs: Maximum log entries to keep
        """
        self.max_logs = max_logs
        self.logs: Deque[Dict] = deque(maxlen=max_logs)
        self.visible = True
        self.filter_levels: Set[str] = {"INFO", "WARNING", "ERROR"}  # Default visible levels
    
    def add_log(self, payload: Dict) -> None:
        """
        Add log entry.
        
        Args:
            payload: Log payload from event bus
        """
        self.logs.append(payload)
    
    def toggle_visibility(self) -> bool:
        """
        Toggle console visibility.
        
        Returns:
            New visibility state
        """
        self.visible = not self.visible
        return self.visible
    
    def toggle_level(self, level: str) -> None:
        """
        Toggle visibility of a log level.
        
        Args:
            level: Log level to toggle
        """
        if level in self.filter_levels:
            self.filter_levels.remove(level)
        else:
            self.filter_levels.add(level)
    
    def clear(self) -> None:
        """Clear all logs."""
        self.logs.clear()
    
    def __rich__(self) -> Panel:
        """
        Render as Rich panel.
        
        Returns:
            Rich Panel with console logs
        """
        if not self.visible:
            return Panel(
                Text("Console hidden (press L to show)", style=theme_manager.current["muted"]),
                title="📟 System Console",
                border_style=theme_manager.current["border"],
                padding=(1, 2)
            )
        
        lines = []
        
        # Show recent logs (last 20)
        recent_logs = list(self.logs)[-20:]
        
        for log in recent_logs:
            level = log.get("level", "INFO")
            
            # Skip if level is filtered out
            if level not in self.filter_levels:
                continue
            
            agent = log.get("agent", "System")
            message = log.get("message", "")
            ts = log.get("ts", "")
            
            # Format timestamp
            try:
                from datetime import datetime
                ts_obj = datetime.fromisoformat(ts)
                time_str = ts_obj.strftime("%H:%M:%S")
            except:
                time_str = "00:00:00"
            
            # Level color
            level_colors = {
                "DEBUG": theme_manager.current["muted"],
                "INFO": theme_manager.current["info"],
                "WARNING": theme_manager.current["warning"],
                "ERROR": theme_manager.current["error"]
            }
            level_color = level_colors.get(level, theme_manager.current["muted"])
            
            # Agent color
            agent_color = theme_manager.get_agent_color(agent)
            
            # Build log line
            line = Text()
            line.append(f"[{time_str}] ", style=theme_manager.current["muted"])
            line.append(f"{level:7s} ", style=level_color)
            line.append(f"{agent:12s} ", style=agent_color)
            line.append(f"│ {message[:80]}", style=theme_manager.current["foreground"])
            
            lines.append(line)
        
        # If no logs
        if not lines:
            lines.append(Text("No logs to display...", style=theme_manager.current["muted"]))
        
        # Filter legend
        legend = Text()
        legend.append("Filters: ", style=theme_manager.current["muted"])
        for level in ["INFO", "WARNING", "ERROR", "DEBUG"]:
            if level in self.filter_levels:
                legend.append(f"[{level}] ", style=theme_manager.current["success"])
            else:
                legend.append(f"[{level}] ", style=theme_manager.current["muted"])
        
        lines.append(Text(""))
        lines.append(legend)
        
        content = Group(*lines)
        
        return Panel(
            content,
            title="📟 System Console",
            border_style=theme_manager.current["border"],
            padding=(1, 2)
        )
