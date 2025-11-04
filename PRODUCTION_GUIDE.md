# TMAO Command Center - Production Guide

## 🚀 Quick Start

### 1. Launch
```bash
cd C:\Users\owner\Desktop\multi-agent-orch
python src/ui/terminal_ui.py
```

### 2. Start Orchestration
Press **[4]** on your keyboard

### 3. Enter Your Task
When prompted:
```
🎯 Enter orchestration task: _
```

Type your task and press Enter, for example:
```
Create a REST API for managing user accounts
```

### 4. Watch the Magic
The system will:
1. 🧭 **Planner** - Analyzes and breaks down your task
2. 🛠️ **Builder** - Executes the subtasks
3. 🧪 **Reviewer** - Evaluates quality and accuracy
4. 🎛️ **Coordinator** - Compiles final report

---

## ⌨️ Keyboard Controls

| Key | Action | Description |
|-----|--------|-------------|
| **4** | **Orchestrate** | Start new orchestration (prompts for task) |
| **P** | Pause/Resume | Pause or resume globe animation |
| **L** | Toggle Logs | Show/hide console panel |
| **C** | Clear Chat | Clear all chat messages |
| **T** | Theme | Switch between light/dark themes |
| **M** | Memory | View memory stats (placeholder) |
| **Q** | Quit | Exit the Command Center |

---

## 💡 Example Tasks

### Web Development
```
Create a REST API for a blog platform with authentication
Build a web scraper for e-commerce product prices
Develop a real-time chat application with WebSockets
```

### Data Processing
```
Build a data pipeline for CSV to JSON conversion
Create an ETL system for database migration
Develop a log analyzer with pattern detection
```

### CLI Tools
```
Build a file organizer CLI with regex support
Create a task scheduler with cron-like syntax
Develop a backup utility with compression
```

### Automation
```
Build a GitHub webhook handler for CI/CD
Create an email automation system
Develop a web form submission bot
```

---

## 🎨 UI Layout

```
╔═══════════════════════════════════════════╗
║       TMAO COMMAND CENTER                 ║
╚═══════════════════════════════════════════╝
┌────────────┬──────────────────────────────┐
│   Globe    │   Agent Chat                 │
│   🌍       │   🧭 Planner: ...            │
│            │   🛠️ Builder: ...            │
│            │   🧪 Reviewer: ...           │
└────────────┴──────────────────────────────┘
┌────────────┬──────────────────────────────┐
│  Metrics   │   Console                    │
│  Progress  │   [12:34:56] INFO ...        │
│  Scores    │   [12:34:57] INFO ...        │
└────────────┴──────────────────────────────┘
╔═══════════════════════════════════════════╗
║  [4] Orchestrate  [Q] Quit                ║
╚═══════════════════════════════════════════╝
```

---

## 📊 What You'll See

### 1. Globe Panel (Top-Left)
- Animated ASCII globe
- Brightens during agent activity
- Rotates continuously (pause with P)

### 2. Chat Panel (Top-Right)
- Real-time agent messages
- Color-coded by agent:
  - 🧭 **Planner** (Cyan)
  - 🛠️ **Builder** (Yellow)
  - 🧪 **Reviewer** (Magenta)
  - 🎛️ **Coordinator** (Green)
- Typing simulation effect

### 3. Metrics Panel (Bottom-Left)
- Current task name
- Current stage (PLANNING/BUILDING/REVIEWING)
- Progress bars for each phase
- Quality scores (Accuracy, Quality, Final)
- Memory statistics
- Orchestration IDs

### 4. Console Panel (Bottom-Right)
- Live system logs
- Timestamped entries
- Filterable by level (INFO/WARNING/ERROR/DEBUG)
- Toggle visibility with L

### 5. Footer (Bottom)
- Available keyboard commands
- Current status message

---

## 🔄 Orchestration Flow

```
Press [4]
    ↓
Enter Task
    ↓
Coordinator Starts
    ↓
┌─────────────────────────────────────┐
│  STAGE 1: PLANNING                  │
│  🧭 Planner analyzes task           │
│  📋 Creates subtask breakdown       │
│  ✅ Plan stored in memory           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  STAGE 2: BUILDING                  │
│  🛠️ Builder executes subtasks       │
│  ⚙️ Runs in parallel/sequential     │
│  ✅ Results stored in memory        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  STAGE 3: REVIEWING                 │
│  🧪 Reviewer evaluates results      │
│  📊 Calculates quality scores       │
│  ✅ Final report generated          │
└─────────────────────────────────────┘
    ↓
Orchestration Complete!
Final Score: XX%
```

---

## 🎯 Best Practices

### Task Input
- ✅ **Be specific**: "Build a REST API for user management"
- ✅ **Include context**: "Create a CLI tool with Python and Click"
- ❌ **Too vague**: "Make something"
- ❌ **Too complex**: "Build entire social media platform"

### Optimal Task Scope
- **Good**: Single feature or component
- **Good**: Well-defined functionality
- **Too Small**: "Print hello world"
- **Too Large**: "Build complete operating system"

### Terminal Settings
- **Width**: At least 100 columns
- **Height**: At least 30 rows
- **Font**: Monospace (Consolas, Courier New)
- **Terminal**: Windows Terminal (recommended) or PowerShell

---

## 🐛 Troubleshooting

### Issue: Keys Not Responding
**Solution**: Click on terminal window to focus it

### Issue: Layout Looks Broken
**Solution**: Resize terminal to at least 100x30 characters

### Issue: No Prompt for Task
**Solution**: Make sure you pressed [4], not another key

### Issue: Orchestration Hangs
**Solution**: Press Q to quit, restart UI, try simpler task

### Issue: UI Flickering
**Solution**: Already fixed with Windows event loop policy

---

## 📈 Performance Tips

### For Faster Orchestration
1. Use simpler, well-defined tasks
2. Avoid overly complex requirements
3. Let agents work sequentially first

### For Better Results
1. Provide clear task descriptions
2. Include technology preferences (e.g., "using Python")
3. Specify desired output format

### For Smoother UI
1. Use Windows Terminal instead of PowerShell
2. Keep terminal size consistent
3. Don't resize during orchestration

---

## ✅ Validation

After launching, verify:
- [ ] UI displays without errors
- [ ] No demo tasks appear
- [ ] Status shows "Ready" or "Awaiting task input"
- [ ] Footer shows only production commands
- [ ] Globe is animating
- [ ] Chat shows welcome messages
- [ ] Pressing [4] prompts for task input

---

## 🎉 You're Ready!

The TMAO Command Center is now:
- ✅ **Clean** - No demo content
- ✅ **Dynamic** - User-driven tasks
- ✅ **Stable** - Windows-compatible
- ✅ **Production-Ready** - Real orchestrations

**Press [4], enter your task, and watch the multi-agent system work!** 🚀

---

## 📞 Quick Reference

```bash
# Launch
python src/ui/terminal_ui.py

# Orchestrate
Press [4] → Enter task → Watch magic

# Quit
Press [Q]
```

**That's it! Simple, clean, powerful.** ✨
