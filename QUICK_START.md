# TMAO Command Center - Quick Start Guide

## 🚀 Launch in 3 Steps

### Step 1: Open Terminal
```bash
cd C:\Users\owner\Desktop\multi-agent-orch
```

### Step 2: Launch Command Center
```bash
python src/ui/terminal_ui.py
```

### Step 3: Press Keys!
- Press `4` for **Full Orchestration** (recommended!)
- Press `1-3` for individual agent demos
- Press `Q` to quit

---

## ⌨️ Keyboard Controls

```
┌─────────────────────────────────────────┐
│  [1] Planner Demo    [2] Builder Demo  │
│  [3] Reviewer Demo   [4] ORCHESTRATE!  │
│                                         │
│  [P] Pause Globe     [L] Toggle Logs   │
│  [C] Clear Chat      [T] Switch Theme  │
│  [M] Memory View     [Q] Quit          │
└─────────────────────────────────────────┘
```

---

## 🎯 What to Expect

### Press `4` - Full Orchestration:

**You'll see:**
1. 🌍 Globe spins and brightens
2. 💬 Chat fills with agent messages
3. 📊 Progress bars animate
4. 📈 Metrics update with scores
5. 📟 Console streams logs

**Timeline:**
- 0-5s: Planner creates plan
- 5-15s: Builder executes subtasks
- 15-20s: Reviewer evaluates results
- 20s: Final score displayed!

---

## 🎨 UI Layout

```
╔═══════════════════════════════════════════╗
║         TMAO COMMAND CENTER               ║
╚═══════════════════════════════════════════╝
┌──────────┬────────────────────────────────┐
│  Globe   │  Agent Chat                    │
│  🌍      │  🧭 Planner: ...               │
│          │  🛠️ Builder: ...               │
│          │  🧪 Reviewer: ...              │
└──────────┴────────────────────────────────┘
┌──────────┬────────────────────────────────┐
│ Metrics  │  Console                       │
│ Progress │  [12:34:56] INFO ...           │
│ Scores   │  [12:34:57] INFO ...           │
└──────────┴────────────────────────────────┘
╔═══════════════════════════════════════════╗
║  Commands & Status                        ║
╚═══════════════════════════════════════════╝
```

---

## 💡 Tips

1. **Best Experience**: Use Windows Terminal (not PowerShell)
2. **Terminal Size**: At least 100x30 characters
3. **Wait for Completion**: Full orchestration takes ~20 seconds
4. **Watch the Globe**: It brightens when agents are active
5. **Check Metrics**: Final score appears in bottom-left panel

---

## 🐛 Troubleshooting

**Problem**: Keys not responding  
**Solution**: Make sure terminal window is focused

**Problem**: Layout looks broken  
**Solution**: Resize terminal to at least 100 columns wide

**Problem**: No messages in chat  
**Solution**: Wait a few seconds after pressing key

**Problem**: Error on startup  
**Solution**: Make sure you're in the project directory

---

## ✅ Quick Test

```bash
# 1. Launch
python src/ui/terminal_ui.py

# 2. Press 1 (Planner demo - quick test)
# Should see: Chat fills with Planner messages

# 3. Press 4 (Full orchestration)
# Should see: All agents working together

# 4. Press Q (Quit)
# Should see: Clean shutdown message
```

---

## 🎉 That's It!

You're ready to use the TMAO Command Center!

**Press `4` and watch the magic happen!** ✨
