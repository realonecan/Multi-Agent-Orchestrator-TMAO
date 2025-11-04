"""
Metrics Panel - Live KPIs, progress bars, and system stats.

Displays orchestration metrics, progress, and memory statistics.

Author: TMAO Dev Team
License: MIT
"""

from typing import Dict, Optional
from rich.panel import Panel
from rich.console import Group
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, TaskID
from ..theme import theme_manager


class MetricsPanel:
    """
    System metrics and progress visualization.
    """
    
    def __init__(self):
        """Initialize metrics panel."""
        self.current_task = "Idle"
        self.current_stage = "READY"
        self.plan_id = "N/A"
        self.execution_id = "N/A"
        self.review_id = "N/A"
        
        # Scores
        self.accuracy = 0.0
        self.quality = 0.0
        self.final_score = 0.0
        self.prev_final_score = 0.0
        
        # Progress
        self.plan_progress = 0.0
        self.build_progress = 0.0
        self.review_progress = 0.0
        self.overall_progress = 0.0
        
        # Memory stats
        self.memory_items = {"working": 0, "episodic": 0, "procedural": 0}
        self.cache_stats = {"size": 0, "hits": 0, "misses": 0}
        
        # Uptime
        import time
        self.start_time = time.time()
    
    def update_metrics(self, payload: Dict) -> None:
        """
        Update metrics from event payload.
        
        Args:
            payload: Metrics payload
        """
        self.accuracy = payload.get("accuracy", 0.0)
        self.quality = payload.get("quality", 0.0)
        self.prev_final_score = self.final_score
        self.final_score = payload.get("final", 0.0)
        
        self.memory_items = payload.get("memory_items", self.memory_items)
        self.cache_stats = payload.get("cache", self.cache_stats)
    
    def update_progress(self, payload: Dict) -> None:
        """
        Update progress from event payload.
        
        Args:
            payload: Progress payload
        """
        phase = payload.get("phase", "")
        percent = payload.get("percent", 0.0)
        
        if phase == "plan":
            self.plan_progress = percent
            self.current_stage = "PLANNING"
        elif phase == "build":
            self.build_progress = percent
            self.current_stage = "BUILDING"
        elif phase == "review":
            self.review_progress = percent
            self.current_stage = "REVIEWING"
        
        # Calculate overall progress
        self.overall_progress = (self.plan_progress + self.build_progress + self.review_progress) / 3.0
    
    def set_task(self, task: str) -> None:
        """Set current task name."""
        self.current_task = task[:50]  # Truncate
    
    def set_ids(self, plan_id: str = None, execution_id: str = None, review_id: str = None) -> None:
        """Set orchestration IDs."""
        if plan_id:
            self.plan_id = plan_id[:8]
        if execution_id:
            self.execution_id = execution_id[:8]
        if review_id:
            self.review_id = review_id[:8]
    
    def _get_score_color(self, score: float) -> str:
        """Get color for score value."""
        if score >= 0.8:
            return theme_manager.current["metric_good"]
        elif score >= 0.5:
            return theme_manager.current["metric_medium"]
        else:
            return theme_manager.current["metric_poor"]
    
    def _get_trend_arrow(self) -> str:
        """Get trend arrow for final score."""
        if self.final_score > self.prev_final_score:
            return "↗️"
        elif self.final_score < self.prev_final_score:
            return "↘️"
        else:
            return "→"
    
    def _create_progress_bar(self, label: str, percent: float, width: int = 20) -> Text:
        """Create a simple progress bar."""
        filled = int(width * (percent / 100.0))
        empty = width - filled
        
        bar = "█" * filled + "░" * empty
        color = self._get_score_color(percent / 100.0)
        
        text = Text()
        text.append(f"{label:12s} ", style=theme_manager.current["muted"])
        text.append(f"[{bar}]", style=color)
        text.append(f" {percent:5.1f}%", style=color)
        
        return text
    
    def __rich__(self) -> Panel:
        """
        Render as Rich panel.
        
        Returns:
            Rich Panel with metrics
        """
        lines = []
        
        # Current task and stage
        lines.append(Text.assemble(
            ("📋 Task: ", theme_manager.current["muted"]),
            (self.current_task, theme_manager.current["primary"])
        ))
        lines.append(Text.assemble(
            ("🎯 Stage: ", theme_manager.current["muted"]),
            (self.current_stage, theme_manager.current["success"])
        ))
        lines.append(Text(""))
        
        # Progress bars
        lines.append(Text("Progress:", style=f"bold {theme_manager.current['primary']}"))
        lines.append(self._create_progress_bar("Plan", self.plan_progress))
        lines.append(self._create_progress_bar("Build", self.build_progress))
        lines.append(self._create_progress_bar("Review", self.review_progress))
        lines.append(self._create_progress_bar("Overall", self.overall_progress))
        lines.append(Text(""))
        
        # Scores
        lines.append(Text("Quality Metrics:", style=f"bold {theme_manager.current['primary']}"))
        
        acc_color = self._get_score_color(self.accuracy)
        qual_color = self._get_score_color(self.quality)
        final_color = self._get_score_color(self.final_score)
        trend = self._get_trend_arrow()
        
        lines.append(Text.assemble(
            ("  Accuracy:    ", theme_manager.current["muted"]),
            (f"{self.accuracy*100:5.1f}%", acc_color)
        ))
        lines.append(Text.assemble(
            ("  Quality:     ", theme_manager.current["muted"]),
            (f"{self.quality*100:5.1f}%", qual_color)
        ))
        lines.append(Text.assemble(
            ("  Final Score: ", theme_manager.current["muted"]),
            (f"{self.final_score*100:5.1f}%", final_color),
            (f" {trend}", final_color)
        ))
        lines.append(Text(""))
        
        # IDs
        lines.append(Text("Orchestration IDs:", style=f"bold {theme_manager.current['primary']}"))
        lines.append(Text.assemble(
            ("  Plan:      ", theme_manager.current["muted"]),
            (self.plan_id, theme_manager.current["info"])
        ))
        lines.append(Text.assemble(
            ("  Execution: ", theme_manager.current["muted"]),
            (self.execution_id, theme_manager.current["info"])
        ))
        lines.append(Text.assemble(
            ("  Review:    ", theme_manager.current["muted"]),
            (self.review_id, theme_manager.current["info"])
        ))
        lines.append(Text(""))
        
        # Memory stats
        total_items = sum(self.memory_items.values())
        lines.append(Text("Memory:", style=f"bold {theme_manager.current['primary']}"))
        lines.append(Text.assemble(
            ("  Items:  ", theme_manager.current["muted"]),
            (f"{total_items} ", theme_manager.current["info"]),
            (f"(W:{self.memory_items['working']} ", theme_manager.current["muted"]),
            (f"E:{self.memory_items['episodic']} ", theme_manager.current["muted"]),
            (f"P:{self.memory_items['procedural']})", theme_manager.current["muted"])
        ))
        
        # Cache stats
        cache_size = self.cache_stats.get("size", 0)
        cache_hits = self.cache_stats.get("hits", 0)
        cache_misses = self.cache_stats.get("misses", 0)
        total_requests = cache_hits + cache_misses
        hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        lines.append(Text.assemble(
            ("  Cache:  ", theme_manager.current["muted"]),
            (f"{cache_size} entries, ", theme_manager.current["info"]),
            (f"{hit_rate:.1f}% hit rate", theme_manager.current["success"] if hit_rate > 50 else theme_manager.current["warning"])
        ))
        
        # Uptime
        import time
        uptime_seconds = int(time.time() - self.start_time)
        uptime_str = f"{uptime_seconds // 60}m {uptime_seconds % 60}s"
        lines.append(Text.assemble(
            ("  Uptime: ", theme_manager.current["muted"]),
            (uptime_str, theme_manager.current["info"])
        ))
        
        content = Group(*lines)
        
        return Panel(
            content,
            title="📊 System Metrics",
            border_style=theme_manager.current["border"],
            padding=(1, 2)
        )
