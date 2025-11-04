"""
ASCII Globe Animation - Rotating Earth visualization.

Provides pre-rendered ASCII globe frames and animation control.

Author: TMAO Dev Team
License: MIT
"""

import time
from typing import List


# ASCII globe frames (10 frames showing Earth rotation)
GLOBE_FRAMES = [
    # Frame 0
    """    ___
  /     \\
 |  🌍   |
 | ~~~  |
  \\_____/""",
    
    # Frame 1
    """    ___
  /     \\
 |   🌍  |
 |  ~~~ |
  \\_____/""",
    
    # Frame 2
    """    ___
  /     \\
 |    🌍 |
 |   ~~~|
  \\_____/""",
    
    # Frame 3
    """    ___
  /     \\
 |     🌍|
 |    ~~|
  \\_____/""",
    
    # Frame 4
    """    ___
  /     \\
 |🌍     |
 |~~~    |
  \\_____/""",
    
    # Frame 5
    """    ___
  /     \\
 | 🌍    |
 | ~~~   |
  \\_____/""",
    
    # Frame 6
    """    ___
  /     \\
 |  🌍   |
 |  ~~~  |
  \\_____/""",
    
    # Frame 7
    """    ___
  /     \\
 |   🌍  |
 |   ~~~ |
  \\_____/""",
    
    # Frame 8
    """    ___
  /     \\
 |    🌍 |
 |    ~~~|
  \\_____/""",
    
    # Frame 9
    """    ___
  /     \\
 |     🌍|
 |     ~~|
  \\_____/"""
]


class GlobeAnimator:
    """
    Manages ASCII globe animation state.
    
    Provides frame sequencing and timing control for smooth rotation.
    """
    
    def __init__(self, frames: List[str] = None, fps: float = 12.0):
        """
        Initialize globe animator.
        
        Args:
            frames: List of ASCII art frames (uses default if None)
            fps: Target frames per second
        """
        self.frames = frames or GLOBE_FRAMES
        self.fps = fps
        self.frame_duration = 1.0 / fps
        
        self._current_frame = 0
        self._last_update = time.time()
        self._paused = False
        self._activity_level = 0.0  # 0.0 to 1.0
    
    def next_frame(self) -> str:
        """
        Get next frame in sequence.
        
        Returns:
            ASCII art string for current frame
        """
        if not self._paused:
            current_time = time.time()
            if current_time - self._last_update >= self.frame_duration:
                self._current_frame = (self._current_frame + 1) % len(self.frames)
                self._last_update = current_time
        
        return self.frames[self._current_frame]
    
    def pause(self) -> None:
        """Pause animation."""
        self._paused = True
    
    def resume(self) -> None:
        """Resume animation."""
        self._paused = False
        self._last_update = time.time()
    
    def toggle_pause(self) -> bool:
        """
        Toggle pause state.
        
        Returns:
            New paused state
        """
        if self._paused:
            self.resume()
        else:
            self.pause()
        return self._paused
    
    @property
    def is_paused(self) -> bool:
        """Check if animation is paused."""
        return self._paused
    
    def set_activity_level(self, level: float) -> None:
        """
        Set activity level (affects visual intensity).
        
        Args:
            level: Activity level from 0.0 to 1.0
        """
        self._activity_level = max(0.0, min(1.0, level))
    
    @property
    def activity_level(self) -> float:
        """Get current activity level."""
        return self._activity_level
    
    def reset(self) -> None:
        """Reset to first frame."""
        self._current_frame = 0
        self._last_update = time.time()
