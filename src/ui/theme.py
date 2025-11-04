"""
Theme System - Color palettes, styles, and visual elements.

Provides theme definitions and runtime theme switching.

Author: TMAO Dev Team
License: MIT
"""

from typing import Dict
from rich.style import Style
from rich.theme import Theme as RichTheme


# Agent avatars and colors
AGENT_CONFIG = {
    "Planner": {
        "emoji": "🧭",
        "color": "cyan",
        "accent": "bright_cyan"
    },
    "Builder": {
        "emoji": "🛠️",
        "color": "yellow",
        "accent": "bright_yellow"
    },
    "Reviewer": {
        "emoji": "🧪",
        "color": "magenta",
        "accent": "bright_magenta"
    },
    "Coordinator": {
        "emoji": "🎛️",
        "color": "green",
        "accent": "bright_green"
    },
    "System": {
        "emoji": "⚙️",
        "color": "white",
        "accent": "bright_white"
    }
}


# Theme definitions
THEMES = {
    "dark_neon": {
        "name": "Dark Neon",
        "background": "black",
        "foreground": "bright_white",
        "primary": "bright_cyan",
        "secondary": "bright_magenta",
        "success": "bright_green",
        "warning": "bright_yellow",
        "error": "bright_red",
        "info": "bright_blue",
        "muted": "bright_black",
        "border": "blue",
        "globe": "bright_cyan",
        "progress_bar": "cyan",
        "progress_complete": "bright_green",
        "metric_good": "bright_green",
        "metric_medium": "bright_yellow",
        "metric_poor": "bright_red",
        "chat_bg": "grey11",
        "console_bg": "grey7"
    },
    "solarized": {
        "name": "Solarized",
        "background": "#002b36",
        "foreground": "#839496",
        "primary": "#268bd2",
        "secondary": "#d33682",
        "success": "#859900",
        "warning": "#b58900",
        "error": "#dc322f",
        "info": "#2aa198",
        "muted": "#586e75",
        "border": "#073642",
        "globe": "#2aa198",
        "progress_bar": "#268bd2",
        "progress_complete": "#859900",
        "metric_good": "#859900",
        "metric_medium": "#b58900",
        "metric_poor": "#dc322f",
        "chat_bg": "#073642",
        "console_bg": "#002b36"
    }
}


class ThemeManager:
    """
    Manages theme state and provides styled components.
    """
    
    def __init__(self, initial_theme: str = "dark_neon"):
        """
        Initialize theme manager.
        
        Args:
            initial_theme: Starting theme name
        """
        self.current_theme_name = initial_theme
        self._themes = THEMES
        self._agent_config = AGENT_CONFIG
    
    @property
    def current(self) -> Dict[str, str]:
        """Get current theme colors."""
        return self._themes[self.current_theme_name]
    
    def switch_theme(self) -> str:
        """
        Switch to next theme.
        
        Returns:
            New theme name
        """
        theme_names = list(self._themes.keys())
        current_idx = theme_names.index(self.current_theme_name)
        next_idx = (current_idx + 1) % len(theme_names)
        self.current_theme_name = theme_names[next_idx]
        return self.current_theme_name
    
    def get_agent_emoji(self, agent_name: str) -> str:
        """Get emoji for agent."""
        return self._agent_config.get(agent_name, {}).get("emoji", "🤖")
    
    def get_agent_color(self, agent_name: str) -> str:
        """Get color for agent."""
        return self._agent_config.get(agent_name, {}).get("color", "white")
    
    def get_agent_accent(self, agent_name: str) -> str:
        """Get accent color for agent."""
        return self._agent_config.get(agent_name, {}).get("accent", "bright_white")
    
    def get_rich_theme(self) -> RichTheme:
        """
        Get Rich theme object.
        
        Returns:
            Rich Theme with current colors
        """
        theme = self.current
        return RichTheme({
            "info": theme["info"],
            "warning": theme["warning"],
            "error": theme["error"],
            "success": theme["success"],
            "primary": theme["primary"],
            "secondary": theme["secondary"],
            "muted": theme["muted"]
        })
    
    def style(self, color_key: str, bold: bool = False, italic: bool = False) -> Style:
        """
        Create a Rich Style from theme color.
        
        Args:
            color_key: Key in current theme
            bold: Bold text
            italic: Italic text
            
        Returns:
            Rich Style object
        """
        color = self.current.get(color_key, "white")
        return Style(color=color, bold=bold, italic=italic)


# Global theme manager
theme_manager = ThemeManager()
