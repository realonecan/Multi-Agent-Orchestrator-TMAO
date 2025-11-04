"""
Globe Panel - Animated ASCII globe widget.

Displays rotating Earth with activity-based coloring.

Author: TMAO Dev Team
License: MIT
"""

from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from ..ascii_globe import GlobeAnimator
from ..theme import theme_manager


class GlobePanel:
    """
    Rich renderable for animated ASCII globe.
    """
    
    def __init__(self, animator: GlobeAnimator):
        """
        Initialize globe panel.
        
        Args:
            animator: Globe animator instance
        """
        self.animator = animator
        self.title = "🌍 TMAO GLOBAL"
    
    def __rich__(self) -> Panel:
        """
        Render as Rich panel.
        
        Returns:
            Rich Panel with globe animation
        """
        # Get current frame
        frame = self.animator.next_frame()
        
        # Color based on activity level
        activity = self.animator.activity_level
        if activity > 0.7:
            color = theme_manager.current["globe"]
        elif activity > 0.3:
            color = theme_manager.current["primary"]
        else:
            color = theme_manager.current["muted"]
        
        # Create styled text
        globe_text = Text(frame, style=color, justify="center")
        
        # Status indicator
        status = "⏸️  PAUSED" if self.animator.is_paused else "▶️  ACTIVE"
        status_text = Text(f"\n{status}", style=theme_manager.current["muted"], justify="center")
        
        # Combine
        content = Text.assemble(globe_text, status_text)
        
        return Panel(
            Align.center(content),
            title=self.title,
            border_style=theme_manager.current["border"],
            padding=(1, 2)
        )
