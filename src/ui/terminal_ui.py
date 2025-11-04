"""
TMAO Command Center - Main Terminal UI.

Rich-based terminal interface for visualizing multi-agent orchestration.

Author: TMAO Dev Team
License: MIT

Usage:
    python src/ui/terminal_ui.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Fix Windows event loop policy for async + Rich UI compatibility
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from src.ui.event_bus import event_bus
from src.ui.theme import theme_manager
from src.ui.ascii_globe import GlobeAnimator
from src.ui.adapters import ChatAdapter, ProgressAdapter, metrics_adapter
from src.ui.widgets.globe_panel import GlobePanel
from src.ui.widgets.chat_panel import ChatPanel
from src.ui.widgets.metrics_panel import MetricsPanel
from src.ui.widgets.console_panel import ConsolePanel
from src.ui.widgets.footer_panel import FooterPanel


class TMAOCommandCenter:
    """
    Main terminal UI controller.
    """
    
    def __init__(self):
        """Initialize command center."""
        self.console = Console()
        self.running = False
        self.orchestration_task = None
        
        # Initialize components
        self.globe_animator = GlobeAnimator(fps=12.0)
        self.globe_panel = GlobePanel(self.globe_animator)
        self.chat_panel = ChatPanel(max_messages=100)
        self.metrics_panel = MetricsPanel()
        self.console_panel = ConsolePanel(max_logs=100)
        self.footer_panel = FooterPanel()
        
        # Layout
        self.layout = Layout()
        self._setup_layout()
        
        # Subscribe to events (will be awaited in run())

    async def _prompt(self, prompt_text: str) -> str:
        """Async-safe console prompt using thread executor."""
        loop = asyncio.get_event_loop()
        def _ask():
            try:
                return input(prompt_text)
            except Exception:
                return ""
        resp = await loop.run_in_executor(None, _ask)
        return resp.strip()

    def _setup_layout(self) -> None:
        """Setup Rich layout structure."""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        # Header
        self.layout["header"].update(self._create_header())
        
        # Main area split into top and bottom
        self.layout["main"].split_column(
            Layout(name="top", ratio=2),
            Layout(name="bottom", ratio=1)
        )
        
        # Top split into globe (left) and chat (right)
        self.layout["main"]["top"].split_row(
            Layout(name="globe", ratio=1),
            Layout(name="chat", ratio=2)
        )
        
        # Bottom split into metrics (left) and console (right)
        self.layout["main"]["bottom"].split_row(
            Layout(name="metrics", ratio=1),
            Layout(name="console", ratio=1)
        )
    
    def _create_header(self) -> Panel:
        """Create header panel."""
        title = Text()
        title.append("╔═══════════════════════════════════════════════════════════╗\n", style=theme_manager.current["primary"])
        title.append("║  ", style=theme_manager.current["primary"])
        title.append("TMAO COMMAND CENTER", style=f"bold {theme_manager.current['success']}")
        title.append("  │  Terminal Multi-Agent Orchestrator  ║\n", style=theme_manager.current["primary"])
        title.append("╚═══════════════════════════════════════════════════════════╝", style=theme_manager.current["primary"])
        
        return Panel(title, border_style=theme_manager.current["border"], padding=(0, 1))
    
    async def _subscribe_events(self) -> None:
        """Subscribe to event bus topics."""
        await event_bus.subscribe("chat", self._handle_chat)
        await event_bus.subscribe("log", self._handle_log)
        await event_bus.subscribe("metrics.update", self._handle_metrics)
        await event_bus.subscribe("progress", self._handle_progress)
        await event_bus.subscribe("orchestrate.start", self._handle_orchestrate_start)
    
    async def _handle_chat(self, payload: dict) -> None:
        """Handle chat messages."""
        await self.chat_panel.add_message(payload)
        # Increase globe activity
        self.globe_animator.set_activity_level(0.8)
    
    async def _handle_log(self, payload: dict) -> None:
        """Handle log messages."""
        self.console_panel.add_log(payload)
    
    async def _handle_metrics(self, payload: dict) -> None:
        """Handle metrics updates."""
        self.metrics_panel.update_metrics(payload)
    
    async def _handle_progress(self, payload: dict) -> None:
        """Handle progress updates."""
        self.metrics_panel.update_progress(payload)
        # Increase globe activity during progress
        self.globe_animator.set_activity_level(0.6)
    
    async def _handle_orchestrate_start(self, payload: dict) -> None:
        """Handle orchestration start."""
        task = payload.get("task", "Unknown task")
        self.metrics_panel.set_task(task)
        self.footer_panel.set_status("Orchestrating...")
    
    def _update_layout(self) -> None:
        """Update all layout panels."""
        self.layout["header"].update(self._create_header())
        self.layout["main"]["top"]["globe"].update(self.globe_panel)
        self.layout["main"]["top"]["chat"].update(self.chat_panel)
        self.layout["main"]["bottom"]["metrics"].update(self.metrics_panel)
        self.layout["main"]["bottom"]["console"].update(self.console_panel)
        self.layout["footer"].update(self.footer_panel)
    
    async def _keyboard_listener(self) -> None:
        """Listen for keyboard input (non-blocking)."""
        import sys
        
        # Only import Unix modules on Unix systems
        old_settings = None
        if sys.platform != 'win32':
            import tty
            import termios
            old_settings = termios.tcgetattr(sys.stdin)
        
        try:
            while self.running:
                # Check for input without blocking
                if sys.platform == 'win32':
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                        await self._handle_keypress(key)
                else:
                    # Unix-like systems
                    import select
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1).lower()
                        await self._handle_keypress(key)
                
                await asyncio.sleep(0.05)
        finally:
            # Restore terminal settings on Unix
            if sys.platform != 'win32' and old_settings is not None:
                import termios
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    async def _handle_keypress(self, key: str) -> None:
        """
        Handle keyboard input.
        
        Args:
            key: Key pressed
        """
        if key == 'q':
            self.running = False
            self.footer_panel.set_status("Shutting down...")
        
        elif key == '1':
            await self._run_planner()
        
        elif key == '2':
            await self._run_builder()
        
        elif key == '3':
            await self._run_reviewer()
        
        elif key == '4':
            await self._run_full_orchestration()
        
        elif key == 'p':
            paused = self.globe_animator.toggle_pause()
            status = "Paused" if paused else "Running"
            self.footer_panel.set_status(f"Animation {status}")
        
        elif key == 'l':
            visible = self.console_panel.toggle_visibility()
            status = "visible" if visible else "hidden"
            self.footer_panel.set_status(f"Console {status}")
        
        elif key == 'c':
            self.chat_panel.clear()
            self.footer_panel.set_status("Chat cleared")
        
        elif key == 't':
            new_theme = theme_manager.switch_theme()
            self.footer_panel.set_status(f"Theme: {new_theme}")
        
        elif key == 'm':
            # Toggle memory view (placeholder)
            self.footer_panel.set_status("Memory view (not implemented)")
    
    async def _run_planner(self) -> None:
        """Run PlannerAgent with user-provided task and publish real events."""
        try:
            from src.agents.planner_agent import PlannerAgent
            from src.core.memory import MemoryManager
            task = await self._prompt("\n🎯 Enter planning task: ")
            if not task:
                self.footer_panel.set_status("No task provided")
                return
            memory = MemoryManager()
            agent = PlannerAgent(shared_memory=memory)
            await agent.initialize()
            await ChatAdapter.publish_message("Planner", "Initialized and ready", "plan", "info")
            await agent.process_task(task, {})
            await agent.shutdown()
            self.footer_panel.set_status("Planner finished")
        except Exception as e:
            await ChatAdapter.publish_message("System", f"Planner error: {e}", "plan", "info")
            self.footer_panel.set_status(f"Error: {str(e)[:30]}")

    async def _run_builder(self) -> None:
        """Run BuilderAgent by first ensuring a plan exists for the provided task."""
        try:
            from src.agents.planner_agent import PlannerAgent
            from src.agents.builder_agent import BuilderAgent
            from src.core.memory import MemoryManager, MemoryType, MemoryQuery
            task = await self._prompt("\n🔨 Enter build task (will plan then build): ")
            if not task:
                self.footer_panel.set_status("No task provided")
                return
            memory = MemoryManager()
            planner = PlannerAgent(shared_memory=memory)
            await planner.initialize()
            await planner.process_task(task, {})
            await planner.shutdown()
            builder = BuilderAgent(shared_memory=memory)
            await builder.initialize()
            # Find latest plan_id for this task in shared memory
            plan_id = None
            try:
                query = MemoryQuery(text="task", memory_type=MemoryType.WORKING, limit=10)
                results = await memory.retrieve(query)
                # Filter for task_decomposition plans matching this task
                plans = [
                    item for item in results
                    if item.metadata.get("plan_type") == "task_decomposition"
                    and isinstance(item.content, dict)
                    and item.content.get("original_task", "").lower().strip() == task.lower().strip()
                ]
                plans.sort(key=lambda x: x.created_at, reverse=True)
                if plans:
                    plan_id = plans[0].id
            except Exception:
                plan_id = None

            await builder.process_task(task, {"plan_id": plan_id})
            await builder.shutdown()
            self.footer_panel.set_status("Builder finished")
        except Exception as e:
            await ChatAdapter.publish_message("System", f"Builder error: {e}", "build", "info")
            self.footer_panel.set_status(f"Error: {str(e)[:30]}")

    async def _run_reviewer(self) -> None:
        """Run ReviewerAgent by planning, building, then reviewing."""
        try:
            from src.agents.planner_agent import PlannerAgent
            from src.agents.builder_agent import BuilderAgent
            from src.agents.reviewer_agent import ReviewerAgent
            from src.core.memory import MemoryManager, MemoryType, MemoryQuery
            task = await self._prompt("\n🔍 Enter review task (will plan, build, then review): ")
            if not task:
                self.footer_panel.set_status("No task provided")
                return
            memory = MemoryManager()
            planner = PlannerAgent(shared_memory=memory)
            await planner.initialize()
            await planner.process_task(task, {})
            await planner.shutdown()
            builder = BuilderAgent(shared_memory=memory)
            await builder.initialize()
            # Locate plan_id
            plan_id = None
            try:
                query = MemoryQuery(text="task", memory_type=MemoryType.WORKING, limit=10)
                results = await memory.retrieve(query)
                plans = [
                    item for item in results
                    if item.metadata.get("plan_type") == "task_decomposition"
                    and isinstance(item.content, dict)
                    and item.content.get("original_task", "").lower().strip() == task.lower().strip()
                ]
                plans.sort(key=lambda x: x.created_at, reverse=True)
                if plans:
                    plan_id = plans[0].id
            except Exception:
                plan_id = None

            await builder.process_task(task, {"plan_id": plan_id})
            await builder.shutdown()
            reviewer = ReviewerAgent(shared_memory=memory)
            await reviewer.initialize()
            # Locate execution_id
            execution_id = None
            try:
                # Retrieve recent working memories and filter by execution tag and agent Builder
                query = MemoryQuery(memory_type=MemoryType.WORKING, limit=20)
                results = await memory.retrieve(query)
                executions = [
                    item for item in results
                    if "execution" in item.tags and item.metadata.get("agent") == "Builder"
                    and isinstance(item.content, dict)
                    and item.content.get("task", "").lower().strip() == task.lower().strip()
                ]
                executions.sort(key=lambda x: x.created_at, reverse=True)
                if executions:
                    execution_id = executions[0].id
            except Exception:
                execution_id = None

            await reviewer.process_task(task, {"plan_id": plan_id, "execution_id": execution_id})
            await reviewer.shutdown()
            self.footer_panel.set_status("Reviewer finished")
        except Exception as e:
            await ChatAdapter.publish_message("System", f"Reviewer error: {e}", "review", "info")
            self.footer_panel.set_status(f"Error: {str(e)[:30]}")

    async def _run_full_orchestration(self) -> None:
        """Run full orchestration."""
        if self.orchestration_task and not self.orchestration_task.done():
            self.footer_panel.set_status("Orchestration already running")
            return
        
        self.orchestration_task = asyncio.create_task(self._orchestrate())
    
    async def _orchestrate(self) -> None:
        """Execute full orchestration with user input."""
        self.footer_panel.set_status("Awaiting task input...")
        
        try:
            # Import coordinator
            from src.agents.coordinator_agent import CoordinatorAgent
            
            # Get task from user (will be prompted in CoordinatorAgent)
            await ChatAdapter.publish_message("System", "Starting orchestration...", "coord", "info")
            
            # Create coordinator
            coordinator = CoordinatorAgent()
            await coordinator.initialize()
            
            # Run orchestration with None to trigger user input
            result = await coordinator.orchestrate(None, {})
            
            # Extract results
            summary = result.get("summary", {})
            accuracy = summary.get("accuracy", 0.0)
            quality = summary.get("quality", 0.0)
            final_score = summary.get("final_score", 0.0)
            
            # Update metrics
            await metrics_adapter.update_scores(accuracy, quality, final_score)
            
            # Set IDs
            self.metrics_panel.set_ids(
                result.get("plan_id"),
                result.get("execution_id"),
                result.get("review_id")
            )
            
            # Final message
            await ChatAdapter.publish_message(
                "Coordinator",
                f"Orchestration complete! Final score: {final_score*100:.1f}%",
                "coord",
                "result"
            )
            
            await coordinator.shutdown()
            self.footer_panel.set_status(f"Orchestration complete: {final_score*100:.1f}%")
            
        except Exception as e:
            await ChatAdapter.publish_message("System", f"Orchestration error: {str(e)}", "coord", "info")
            self.footer_panel.set_status(f"Error: {str(e)[:30]}")
    
    async def run(self) -> None:
        """Run the command center UI."""
        self.running = True
        
        # Subscribe to events first
        await self._subscribe_events()
        
        # Start keyboard listener
        keyboard_task = asyncio.create_task(self._keyboard_listener())
        
        # Welcome messages
        await ChatAdapter.publish_message("System", "TMAO Command Center initialized", "general", "info")
        await ChatAdapter.publish_message("System", "Press [4] to start orchestration, [Q] to quit", "general", "info")
        
        try:
            with Live(
                self.layout,
                console=self.console,
                refresh_per_second=30,
                screen=True,
                transient=False
            ) as live:
                while self.running:
                    # Update layout
                    self._update_layout()
                    
                    # Decay globe activity
                    current_activity = self.globe_animator.activity_level
                    if current_activity > 0:
                        self.globe_animator.set_activity_level(current_activity * 0.95)
                    
                    # Small sleep to prevent CPU spinning (~30 FPS)
                    await asyncio.sleep(0.033)
        
        finally:
            # Cleanup
            keyboard_task.cancel()
            try:
                await keyboard_task
            except asyncio.CancelledError:
                pass
            
            # Cancel orchestration if running
            if self.orchestration_task and not self.orchestration_task.done():
                self.orchestration_task.cancel()
                try:
                    await self.orchestration_task
                except asyncio.CancelledError:
                    pass
            
            self.console.print("\n[green]TMAO Command Center shutdown complete.[/green]")


async def main():
    """Main entry point."""
    command_center = TMAOCommandCenter()
    await command_center.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
