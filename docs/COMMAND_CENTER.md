# TMAO Command Center - Technical Documentation

## Overview

The TMAO Command Center is a Rich-based terminal UI that provides real-time visualization of multi-agent orchestration. It features animated components, live metrics, agent conversation tracking, and interactive keyboard controls.

## Architecture

### Component Hierarchy

```
TMAOCommandCenter (Main Controller)
├── EventBus (Pub/Sub Communication)
├── ThemeManager (Visual Styling)
├── GlobeAnimator (Animation State)
└── Widgets
    ├── GlobePanel (Animated Globe)
    ├── ChatPanel (Agent Conversation)
    ├── MetricsPanel (KPIs & Progress)
    ├── ConsolePanel (System Logs)
    └── FooterPanel (Command Bar)
```

### Event-Driven Architecture

The UI uses a lightweight event bus for decoupled communication:

**Event Topics:**
- `chat` - Agent conversation messages
- `log` - System log entries
- `metrics.update` - Score and memory statistics
- `progress` - Phase progress updates (plan/build/review)
- `orchestrate.start` - Orchestration initiation

**Event Flow:**
```
Agent Action → Adapter → Event Bus → Widget Subscriber → UI Update
```

### Module Structure

```
src/ui/
├── __init__.py              # Package initialization
├── terminal_ui.py           # Main entry point & controller
├── event_bus.py             # Pub/sub event system
├── theme.py                 # Color schemes & styling
├── ascii_globe.py           # Globe animation frames
├── adapters.py              # Agent-to-UI bridges
└── widgets/
    ├── __init__.py
    ├── globe_panel.py       # Animated globe widget
    ├── chat_panel.py        # Conversation window
    ├── metrics_panel.py     # Metrics dashboard
    ├── console_panel.py     # Log viewer
    └── footer_panel.py      # Command bar
```

## Core Components

### 1. Event Bus (`event_bus.py`)

**Purpose:** Decoupled async communication between agents and UI.

**Key Methods:**
- `subscribe(topic, callback)` - Register event listener
- `publish(topic, payload)` - Emit event to subscribers
- `unsubscribe(topic, callback)` - Remove listener

**Example:**
```python
from src.ui.event_bus import event_bus

async def handle_chat(payload):
    print(f"Agent {payload['agent']}: {payload['text']}")

await event_bus.subscribe("chat", handle_chat)
await event_bus.publish("chat", {
    "agent": "Planner",
    "text": "Task analysis complete",
    "phase": "plan",
    "level": "info"
})
```

### 2. Theme Manager (`theme.py`)

**Purpose:** Centralized color management and theme switching.

**Themes:**
- `dark_neon` - High contrast with neon accents (default)
- `solarized` - Softer, eye-friendly palette

**Key Methods:**
- `switch_theme()` - Cycle to next theme
- `get_agent_emoji(agent_name)` - Get agent avatar
- `get_agent_color(agent_name)` - Get agent color
- `style(color_key, bold, italic)` - Create Rich Style

**Example:**
```python
from src.ui.theme import theme_manager

# Get current theme colors
colors = theme_manager.current
print(colors["primary"])  # "bright_cyan"

# Switch theme
new_theme = theme_manager.switch_theme()
print(f"Switched to: {new_theme}")

# Get agent styling
emoji = theme_manager.get_agent_emoji("Planner")  # "🧭"
color = theme_manager.get_agent_color("Planner")  # "cyan"
```

### 3. Globe Animator (`ascii_globe.py`)

**Purpose:** Manages rotating ASCII globe animation state.

**Features:**
- 10 pre-rendered frames showing Earth rotation
- Configurable FPS (default: 12)
- Pause/resume control
- Activity level indicator (affects color intensity)

**Key Methods:**
- `next_frame()` - Get current frame and advance
- `pause()` / `resume()` - Control animation
- `toggle_pause()` - Toggle pause state
- `set_activity_level(level)` - Set activity (0.0-1.0)

**Example:**
```python
from src.ui.ascii_globe import GlobeAnimator

animator = GlobeAnimator(fps=12.0)
frame = animator.next_frame()  # Get ASCII art string

animator.set_activity_level(0.8)  # High activity
animator.pause()  # Stop rotation
```

### 4. Adapters (`adapters.py`)

**Purpose:** Bridge between agent APIs and UI event system.

**Components:**

**UILogHandler** - Logging handler that publishes to event bus
```python
handler = UILogHandler()
logger.addHandler(handler)
```

**ProgressAdapter** - Publishes progress updates
```python
await ProgressAdapter.publish_progress("plan", 50.0, "Analyzing...")
```

**MetricsAdapter** - Collects and publishes metrics
```python
await metrics_adapter.update_scores(0.95, 0.87, 0.91)
await metrics_adapter.update_memory_stats(10, 5, 3)
```

**ChatAdapter** - Publishes agent messages
```python
await ChatAdapter.publish_message(
    "Planner",
    "Task decomposition complete",
    "plan",
    "result"
)
```

## Widget Components

### Globe Panel (`globe_panel.py`)

**Displays:** Animated rotating globe with activity indicator

**Features:**
- Pulls frames from GlobeAnimator
- Color changes based on activity level
- Shows pause/active status

**Rendering:**
```python
globe_panel = GlobePanel(animator)
panel = globe_panel.__rich__()  # Returns Rich Panel
```

### Chat Panel (`chat_panel.py`)

**Displays:** Agent conversation with typing simulation

**Features:**
- Ring buffer (100 messages max)
- Typing indicators with animated ellipsis
- Agent avatars and color coding
- Timestamp formatting
- Message level icons (ℹ️💭⚡✅)

**Key Methods:**
- `add_message(payload)` - Add message with typing delay
- `clear()` - Clear all messages

**Typing Simulation:**
- Shows "{agent} is typing..." for 250-600ms
- Delay scales with message length
- Animated ellipsis during typing

### Metrics Panel (`metrics_panel.py`)

**Displays:** Live KPIs, progress bars, system stats

**Metrics Shown:**
- Current task and stage
- Progress bars (plan/build/review/overall)
- Quality scores (accuracy/quality/final)
- Orchestration IDs (plan/execution/review)
- Memory statistics (working/episodic/procedural)
- Cache stats (size, hit rate)
- System uptime

**Key Methods:**
- `update_metrics(payload)` - Update scores
- `update_progress(payload)` - Update progress bars
- `set_task(task)` - Set current task name
- `set_ids(plan_id, execution_id, review_id)` - Set IDs

**Progress Bars:**
- Visual: `[████████░░] 80.0%`
- Color-coded by score (green/yellow/red)
- Trend arrows for final score (↗️→↘️)

### Console Panel (`console_panel.py`)

**Displays:** Streaming system logs with filtering

**Features:**
- Ring buffer (100 logs max)
- Level filtering (INFO/WARNING/ERROR/DEBUG)
- Agent color coding
- Timestamp formatting
- Toggle visibility

**Key Methods:**
- `add_log(payload)` - Add log entry
- `toggle_visibility()` - Show/hide console
- `toggle_level(level)` - Filter by level
- `clear()` - Clear all logs

**Log Format:**
```
[12:34:56] INFO    Planner      │ Task analysis started
[12:34:57] WARNING Builder      │ Subtask retry needed
[12:34:58] ERROR   System       │ Connection failed
```

### Footer Panel (`footer_panel.py`)

**Displays:** Command bar with hotkey help and status

**Features:**
- Hotkey reference grid
- Status message display
- Toggle help visibility

**Hotkeys Displayed:**
- `[1-4]` - Demo shortcuts
- `[M]` - Memory view
- `[L]` - Toggle logs
- `[P]` - Pause/resume
- `[C]` - Clear chat
- `[T]` - Theme switch
- `[Q]` - Quit

## Main Controller (`terminal_ui.py`)

### TMAOCommandCenter Class

**Responsibilities:**
- Initialize all components
- Setup Rich layout
- Handle keyboard input
- Update UI loop
- Manage orchestration tasks

**Layout Structure:**
```
┌─────────────────────────────────────┐
│           Header (3 lines)          │
├─────────────┬───────────────────────┤
│   Globe     │   Chat                │
│  (ratio 1)  │  (ratio 2)            │
│             │                       │
├─────────────┴───────────────────────┤
│  Metrics    │   Console             │
│  (ratio 1)  │   (ratio 1)           │
└─────────────┴───────────────────────┘
│           Footer (3 lines)          │
└─────────────────────────────────────┘
```

**Keyboard Handling:**

The UI uses platform-specific non-blocking input:

**Windows:**
```python
import msvcrt
if msvcrt.kbhit():
    key = msvcrt.getch().decode('utf-8')
```

**Unix/Linux/macOS:**
```python
import select
if select.select([sys.stdin], [], [], 0.1)[0]:
    key = sys.stdin.read(1)
```

**Key Actions:**
- `1` → `_run_planner_demo()`
- `2` → `_run_builder_demo()`
- `3` → `_run_reviewer_demo()`
- `4` → `_run_full_orchestration()`
- `p` → Toggle globe animation
- `l` → Toggle console visibility
- `c` → Clear chat messages
- `t` → Switch theme
- `m` → Memory view (placeholder)
- `q` → Graceful shutdown

### Orchestration Integration

**Demo Execution:**
```python
async def _run_planner_demo(self):
    # Import agent
    from src.agents.planner_agent import PlannerAgent
    
    # Publish chat message
    await ChatAdapter.publish_message(
        "System", "Starting Planner demo...", "plan", "info"
    )
    
    # Create and run agent
    planner = PlannerAgent(shared_memory=memory)
    await planner.initialize()
    result = await planner.process_task("Build API", {})
    
    # Update metrics
    await metrics_adapter.update_memory_stats(...)
```

**Full Orchestration:**
```python
async def _orchestrate(self):
    coordinator = CoordinatorAgent()
    await coordinator.initialize()
    
    result = await coordinator.orchestrate(task, context)
    
    # Extract and display results
    await metrics_adapter.update_scores(
        result["summary"]["accuracy"],
        result["summary"]["quality"],
        result["summary"]["final_score"]
    )
```

## Event Payloads

### Chat Event
```python
{
    "agent": "Planner|Builder|Reviewer|Coordinator|System",
    "text": "Message content",
    "ts": "2025-01-24T12:34:56.789",
    "phase": "plan|build|review|coord|general",
    "level": "info|thought|action|result"
}
```

### Log Event
```python
{
    "level": "INFO|WARNING|ERROR|DEBUG",
    "agent": "Planner|Builder|Reviewer|Coordinator|System",
    "message": "Log message text",
    "ts": "2025-01-24T12:34:56.789"
}
```

### Metrics Update Event
```python
{
    "accuracy": 0.95,  # 0.0-1.0
    "quality": 0.87,   # 0.0-1.0
    "final": 0.91,     # 0.0-1.0
    "memory_items": {
        "working": 10,
        "episodic": 5,
        "procedural": 3
    },
    "cache": {
        "size": 100,
        "hits": 75,
        "misses": 25
    }
}
```

### Progress Event
```python
{
    "phase": "plan|build|review",
    "percent": 75.0,  # 0-100
    "detail": "Optional status message"
}
```

## Performance Optimization

### CPU Usage
- **Target:** <5% idle, ~10-15% during orchestration
- **Achieved:** Uses `asyncio.sleep(0.05)` to prevent CPU spinning
- **Refresh Rate:** 20 FPS (configurable)

### Memory Management
- **Ring Buffers:** Chat (100 msgs), Console (100 logs)
- **Globe Frames:** Pre-rendered (no runtime generation)
- **Event Bus:** Weak references to prevent leaks

### Animation Smoothness
- **Frame Duration:** 1/12 second (12 FPS globe)
- **UI Refresh:** 1/20 second (20 FPS overall)
- **Activity Decay:** 0.95x per frame (smooth fade)

## Cross-Platform Compatibility

### Windows
- Uses `msvcrt` for keyboard input
- Tested on PowerShell, CMD, Windows Terminal
- Full Unicode support in Windows Terminal

### Linux
- Uses `select` and `termios` for keyboard input
- Tested on GNOME Terminal, Konsole, xterm
- Requires UTF-8 locale

### macOS
- Uses `select` and `termios` for keyboard input
- Tested on Terminal.app, iTerm2
- Full emoji support

## Extension Points

### Adding New Themes

Edit `src/ui/theme.py`:
```python
THEMES["my_theme"] = {
    "name": "My Theme",
    "background": "#000000",
    "foreground": "#ffffff",
    "primary": "#00ff00",
    # ... more colors
}
```

### Adding New Widgets

1. Create widget file in `src/ui/widgets/`
2. Implement `__rich__()` method returning Rich Panel
3. Add to layout in `terminal_ui.py`
4. Subscribe to relevant events

Example:
```python
class MyWidget:
    def __init__(self):
        self.data = []
    
    async def handle_event(self, payload):
        self.data.append(payload)
    
    def __rich__(self) -> Panel:
        content = Text("\n".join(self.data))
        return Panel(content, title="My Widget")
```

### Adding New Event Topics

1. Define payload structure
2. Publish from adapter or agent
3. Subscribe in widget or controller

```python
# Publisher
await event_bus.publish("my_topic", {"key": "value"})

# Subscriber
async def handle_my_event(payload):
    print(payload["key"])

await event_bus.subscribe("my_topic", handle_my_event)
```

## Testing

### Manual Testing Checklist

- [ ] Launch UI: `python src/ui/terminal_ui.py`
- [ ] Globe animates smoothly
- [ ] Press `1` - Planner demo runs
- [ ] Press `2` - Builder demo runs
- [ ] Press `3` - Reviewer demo runs
- [ ] Press `4` - Full orchestration runs
- [ ] Press `P` - Globe pauses/resumes
- [ ] Press `L` - Console toggles
- [ ] Press `C` - Chat clears
- [ ] Press `T` - Theme switches
- [ ] Press `Q` - Clean shutdown
- [ ] Resize terminal - Layout adapts
- [ ] Run on Windows, Linux, macOS

### Error Scenarios

- [ ] Agent import fails - Shows error message
- [ ] Orchestration fails - Red banner, UI continues
- [ ] Terminal too small - Layout degrades gracefully
- [ ] Keyboard interrupt - Clean shutdown

## Troubleshooting

### Common Issues

**Issue:** Globe not visible
- **Cause:** Terminal doesn't support Unicode
- **Fix:** Use Windows Terminal or modern terminal emulator

**Issue:** Layout broken
- **Cause:** Terminal too small
- **Fix:** Resize to at least 100x30 characters

**Issue:** High CPU usage
- **Cause:** Refresh rate too high
- **Fix:** Reduce `refresh_per_second` in `Live()` call

**Issue:** Keyboard input not working
- **Cause:** Terminal in wrong mode
- **Fix:** Restart terminal, check stdin is not redirected

**Issue:** Colors look wrong
- **Cause:** Terminal color support limited
- **Fix:** Enable 256-color or truecolor support

## Future Enhancements

### Planned Features
- [ ] Memory view panel (press `M`)
- [ ] Agent health indicators
- [ ] Performance graphs (CPU/memory over time)
- [ ] Export orchestration report
- [ ] Replay mode (replay past orchestrations)
- [ ] Custom hotkey configuration
- [ ] Sound effects (optional)
- [ ] Mouse support for clickable elements

### API Improvements
- [ ] WebSocket support for remote monitoring
- [ ] REST API for external control
- [ ] Plugin system for custom widgets
- [ ] Theme marketplace

---

**Last Updated:** January 2025  
**Maintainer:** TMAO Dev Team  
**License:** MIT
