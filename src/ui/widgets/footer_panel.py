"""
Footer Panel - Command bar and hotkey help.

Displays available keyboard shortcuts and status information.

Author: TMAO Dev Team
License: MIT
"""

from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from ..theme import theme_manager


class FooterPanel:
    """
    Command bar with hotkey help.
    """
    
    def __init__(self):
        """Initialize footer panel."""
        self.status_message = "Ready"
        self.show_help = True
    
    def set_status(self, message: str) -> None:
        """
        Set status message.
        
        Args:
            message: Status message to display
        """
        self.status_message = message
    
    def toggle_help(self) -> bool:
        """
        Toggle help visibility.
        
        Returns:
            New help visibility state
        """
        self.show_help = not self.show_help
        return self.show_help
    
    def __rich__(self) -> Panel:
        """
        Render as Rich panel.
        
        Returns:
            Rich Panel with footer content
        """
        if not self.show_help:
            content = Text(f"Status: {self.status_message}", style=theme_manager.current["muted"])
        else:
            # Build hotkey help
            hotkeys = [
                ("1", "Planner"),
                ("2", "Builder"),
                ("3", "Reviewer"),
                ("4", "Orchestrate"),
                ("P", "Pause/Resume"),
                ("L", "Toggle Logs"),
                ("C", "Clear Chat"),
                ("T", "Theme"),
                ("M", "Memory"),
                ("Q", "Quit")
            ]
            
            hotkey_texts = []
            for key, desc in hotkeys:
                text = Text()
                text.append(f"[{key}]", style=f"bold {theme_manager.current['primary']}")
                text.append(f" {desc}", style=theme_manager.current["muted"])
                hotkey_texts.append(text)
            
            # Create columns
            content = Columns(hotkey_texts, equal=True, expand=True)
        
        return Panel(
            content,
            title=f"⌨️  Commands  │  Status: {self.status_message}",
            border_style=theme_manager.current["border"],
            padding=(0, 2)
        )
