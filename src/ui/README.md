# TMAO Command Center - UI Package

## Quick Start

```bash
# Launch the Command Center
python src/ui/terminal_ui.py
```

## Package Structure

```
src/ui/
├── __init__.py              # Package initialization
├── terminal_ui.py           # Main entry point (450 lines)
├── event_bus.py             # Pub/sub event system (60 lines)
├── theme.py                 # Theme manager (150 lines)
├── ascii_globe.py           # Globe animator (120 lines)
├── adapters.py              # Agent-to-UI bridges (150 lines)
└── widgets/
    ├── __init__.py
    ├── globe_panel.py       # Animated globe (60 lines)
    ├── chat_panel.py        # Conversation window (150 lines)
    ├── metrics_panel.py     # KPI dashboard (200 lines)
    ├── console_panel.py     # Log viewer (120 lines)
    └── footer_panel.py      # Command bar (60 lines)
```

## Module Overview

### Core Modules

**`terminal_ui.py`** - Main controller
- Manages UI lifecycle
- Handles keyboard input
- Coordinates all widgets
- Runs orchestration demos

**`event_bus.py`** - Event system
- Async pub/sub pattern
- Topic-based routing
- Decoupled communication

**`theme.py`** - Visual styling
- Two themes: Dark Neon, Solarized
- Agent colors and avatars
- Runtime theme switching

**`ascii_globe.py`** - Animation
- 10 pre-rendered frames
- 12 FPS rotation
- Activity-based coloring

**`adapters.py`** - Integration layer
- UILogHandler - Logging bridge
- ProgressAdapter - Progress updates
- MetricsAdapter - Score collection
- ChatAdapter - Message publishing

### Widget Modules

**`globe_panel.py`** - Animated globe widget
- Displays rotating Earth
- Shows pause/active status
- Color changes with activity

**`chat_panel.py`** - Agent conversation
- Ring buffer (100 messages)
- Typing simulation
- Agent avatars and colors

**`metrics_panel.py`** - KPI dashboard
- Progress bars
- Quality scores
- Memory statistics
- Orchestration IDs

**`console_panel.py`** - Log viewer
- Ring buffer (100 logs)
- Level filtering
- Agent color coding
- Toggle visibility

**`footer_panel.py`** - Command bar
- Hotkey reference
- Status messages
- Toggle help display

## Usage Examples

### Basic Usage

```python
from src.ui.terminal_ui import TMAOCommandCenter

# Create and run
command_center = TMAOCommandCenter()
await command_center.run()
```

### Event Publishing

```python
from src.ui.adapters import ChatAdapter, ProgressAdapter, metrics_adapter

# Publish chat message
await ChatAdapter.publish_message(
    agent="Planner",
    text="Task analysis complete",
    phase="plan",
    level="result"
)

# Publish progress
await ProgressAdapter.publish_progress(
    phase="build",
    percent=75.0,
    detail="Building step 4/5"
)

# Update metrics
await metrics_adapter.update_scores(
    accuracy=0.95,
    quality=0.87,
    final=0.91
)
```

### Event Subscription

```python
from src.ui.event_bus import event_bus

async def handle_chat(payload):
    agent = payload["agent"]
    text = payload["text"]
    print(f"{agent}: {text}")

await event_bus.subscribe("chat", handle_chat)
```

### Theme Management

```python
from src.ui.theme import theme_manager

# Get current theme colors
colors = theme_manager.current
print(colors["primary"])  # "bright_cyan"

# Switch theme
new_theme = theme_manager.switch_theme()

# Get agent styling
emoji = theme_manager.get_agent_emoji("Planner")  # "🧭"
color = theme_manager.get_agent_color("Planner")  # "cyan"
```

### Globe Animation

```python
from src.ui.ascii_globe import GlobeAnimator

animator = GlobeAnimator(fps=12.0)

# Get next frame
frame = animator.next_frame()

# Control animation
animator.pause()
animator.resume()
animator.toggle_pause()

# Set activity level
animator.set_activity_level(0.8)  # 0.0-1.0
```

## Event Topics

### Available Topics

- `chat` - Agent conversation messages
- `log` - System log entries
- `metrics.update` - Score and memory stats
- `progress` - Phase progress updates
- `plan.progress` - Planner progress
- `build.progress` - Builder progress
- `review.progress` - Reviewer progress
- `orchestrate.start` - Orchestration start

### Event Payloads

**Chat Event:**
```python
{
    "agent": "Planner",
    "text": "Message content",
    "ts": "2025-01-24T12:34:56.789",
    "phase": "plan",
    "level": "info"
}
```

**Progress Event:**
```python
{
    "phase": "build",
    "percent": 75.0,
    "detail": "Building step 4/5"
}
```

**Metrics Event:**
```python
{
    "accuracy": 0.95,
    "quality": 0.87,
    "final": 0.91,
    "memory_items": {"working": 10, "episodic": 5, "procedural": 3},
    "cache": {"size": 100, "hits": 75, "misses": 25}
}
```

## Keyboard Controls

| Key | Action | Handler |
|-----|--------|---------|
| `1` | Planner Demo | `_run_planner_demo()` |
| `2` | Builder Demo | `_run_builder_demo()` |
| `3` | Reviewer Demo | `_run_reviewer_demo()` |
| `4` | Full Orchestration | `_run_full_orchestration()` |
| `M` | Memory View | Placeholder |
| `L` | Toggle Logs | `console_panel.toggle_visibility()` |
| `P` | Pause/Resume | `globe_animator.toggle_pause()` |
| `C` | Clear Chat | `chat_panel.clear()` |
| `T` | Switch Theme | `theme_manager.switch_theme()` |
| `Q` | Quit | Sets `running = False` |

## Extending the UI

### Adding a New Widget

1. Create widget file in `widgets/`:

```python
# src/ui/widgets/my_widget.py
from rich.panel import Panel
from rich.text import Text

class MyWidget:
    def __init__(self):
        self.data = []
    
    async def handle_event(self, payload):
        self.data.append(payload)
    
    def __rich__(self) -> Panel:
        content = Text("\n".join(self.data))
        return Panel(content, title="My Widget")
```

2. Add to `terminal_ui.py`:

```python
from src.ui.widgets.my_widget import MyWidget

# In __init__
self.my_widget = MyWidget()

# Subscribe to events
await event_bus.subscribe("my_topic", self.my_widget.handle_event)

# Add to layout
self.layout["section"].update(self.my_widget)
```

### Adding a New Theme

Edit `theme.py`:

```python
THEMES["my_theme"] = {
    "name": "My Theme",
    "background": "#000000",
    "foreground": "#ffffff",
    "primary": "#00ff00",
    "secondary": "#ff00ff",
    "success": "#00ff00",
    "warning": "#ffff00",
    "error": "#ff0000",
    "info": "#00ffff",
    "muted": "#808080",
    "border": "#0000ff",
    "globe": "#00ffff",
    "progress_bar": "#00ff00",
    "progress_complete": "#00ff00",
    "metric_good": "#00ff00",
    "metric_medium": "#ffff00",
    "metric_poor": "#ff0000",
    "chat_bg": "#1a1a1a",
    "console_bg": "#0a0a0a"
}
```

### Adding a New Event Topic

1. Define payload structure
2. Publish from adapter or agent
3. Subscribe in widget

```python
# Publisher
await event_bus.publish("my_topic", {"key": "value"})

# Subscriber
async def handle_my_event(payload):
    print(payload["key"])

await event_bus.subscribe("my_topic", handle_my_event)
```

## Performance Tips

### Optimize Refresh Rate

```python
# In terminal_ui.py, adjust Live() parameters
with Live(
    self.layout,
    refresh_per_second=10,  # Lower = less CPU
    screen=True
) as live:
    ...
```

### Reduce Buffer Sizes

```python
# In widget initialization
self.chat_panel = ChatPanel(max_messages=50)  # Default: 100
self.console_panel = ConsolePanel(max_logs=50)  # Default: 100
```

### Disable Animations

```python
# Pause globe on startup
self.globe_animator.pause()
```

## Troubleshooting

### Globe Not Animating
- Press `P` to resume
- Check terminal supports Unicode

### Layout Broken
- Resize terminal to ≥100x30 chars
- Enable UTF-8 encoding

### High CPU Usage
- Reduce `refresh_per_second`
- Pause globe with `P`

### Keyboard Not Working
- Check stdin is not redirected
- Restart terminal

## Dependencies

- `rich>=13.7.0` - Terminal UI framework
- `asyncio` - Async event loop (stdlib)
- Platform-specific:
  - Windows: `msvcrt` (stdlib)
  - Unix/Linux/macOS: `select`, `termios` (stdlib)

## Testing

### Manual Testing

```bash
# Launch UI
python src/ui/terminal_ui.py

# Test all hotkeys
# Press: 1, 2, 3, 4, P, L, C, T, Q

# Test resize
# Resize terminal window

# Test themes
# Press T multiple times
```

### Integration Testing

```python
# Test event publishing
from src.ui.event_bus import event_bus

async def test_events():
    received = []
    
    async def handler(payload):
        received.append(payload)
    
    await event_bus.subscribe("test", handler)
    await event_bus.publish("test", {"data": "test"})
    
    assert len(received) == 1
    assert received[0]["data"] == "test"
```

## License

MIT License - See project root LICENSE file

## Support

For issues, questions, or contributions:
- See `docs/COMMAND_CENTER.md` for technical details
- Check `README.md` for user guide
- Review `COMMAND_CENTER_SUMMARY.md` for build overview
