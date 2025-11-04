Architecture Documentation
Overview

The Terminal Multi-Agent Orchestrator (TMAO) is a modular, cross-platform terminal application that coordinates multiple intelligent agents to complete complex tasks.
It runs entirely in the terminal (Windows, macOS, Linux) with no external servers required.

System Goals

🧩 Modular — Each agent is self-contained and replaceable.

⚙️ Lightweight — No servers, databases, or cloud dependencies.

🧠 Context-Aware — Session-based memory captures all reasoning steps.

💻 Cross-Platform — Works on any modern terminal.

🎨 Beautiful — Clean, color-coded, animated terminal output.

🔁 Extensible — Easily add agents, tools, or model adapters later.

High-Level Architecture
┌──────────────────────────────────────┐
│          CLI / Terminal Layer        │
│    main.py  |  rich / textual UI     │
└──────────────────────────────────────┘
                 │
┌──────────────────────────────────────┐
│          Orchestration Layer         │
│ orchestrator.py | config.yaml        │
│ Runs agent loop, logs steps          │
└──────────────────────────────────────┘
                 │
┌──────────────────────────────────────┐
│              Agent Layer             │
│ Planner | Builder | Evaluator | ...  │
│ Modular Python classes (BaseAgent)   │
└──────────────────────────────────────┘
                 │
┌──────────────────────────────────────┐
│             Memory Layer             │
│ memory.py → .orch/memory.jsonl       │
│ Append-only session memory           │
└──────────────────────────────────────┘

Core Components
1️⃣ CLI / Terminal Layer

Entry point for every run.

Example usage:

python main.py --task "Generate backend design"


Renders live agent output with colors and sections:

THOUGHT ▸ italic blue

ACTION ▸ bold yellow

RESULT ▸ bold green

ERROR ▸ bold red

2️⃣ Orchestration Layer

Reads config.yaml.

Initializes agents and memory.

Controls step order (Planner → Builder → Evaluator).

Handles retries and error recovery.

Logs every event (thought, action, result, etc.) to both:

Terminal (formatted)

Memory file (.orch/memory.jsonl)

3️⃣ Agent Layer

Each agent inherits from BaseAgent and implements its own reasoning logic.

Agent	Role
Planner	Breaks the task into subtasks or requirements.
Builder	Generates the actual artifact (text, code, data).
Evaluator	Reviews Builder output and decides pass/fail.
(optional) Researcher / Reviewer	Future specialized roles.

Communication:
Agents don’t talk directly — they read/write through the Memory Layer, ensuring clear data flow and replayability.

4️⃣ Memory Layer

Implements a simple but powerful blackboard system.

File: .orch/memory.jsonl

Format (one JSON line per entry):

{
  "ts": "2025-10-24T12:34:56Z",
  "session_id": "uuid",
  "agent": "Planner",
  "type": "thought|action|result|error|checkpoint",
  "payload": { "text": "..." }
}


Features:

Append-only (crash-safe)

In-memory cache for fast reads

Per-session separation

Human-readable logs

Data Flow
User → CLI
      ↓
  Orchestrator
      ↓
  [Planner] → [Builder] → [Evaluator]
      ↓
  Memory (record events)
      ↓
  Terminal Renderer (visual feedback)


Every action and thought is both displayed in real time and persisted for later replay or summary.

Config System

Example config.yaml:

memory:
  path: ".orch/memory.jsonl"

run:
  policy: "sequential"
  max_steps: 5

agents:
  - name: Planner
    model: "gpt-4o"
    role: "Decompose complex tasks"
  - name: Builder
    model: "claude-3.5-sonnet"
    role: "Generate artifacts"
  - name: Evaluator
    model: "gpt-4o"
    role: "Assess and summarize results"


Supports swapping models or disabling agents easily.

Keeps configuration human-readable and versionable.

Error Handling

Soft errors: Logged to memory and continue if possible.

Hard errors: Display bold red box + exit code ≠ 0.

Graceful recovery: Writes checkpoint before aborting.

All exceptions visible in the terminal — no silent fails.

Extensibility Roadmap
Phase	Feature	Description
2	Async orchestration	Run agents concurrently using asyncio.
3	Tool layer	Add callable tools (web_search, fs_write, exec).
4	Model adapters	Integrate OpenAI, Anthropic, or local Ollama models.
5	Export/report	Convert session memory into Markdown summary.
6	Visualization	Optional graphical dashboard or ASCII graph.
Cross-Platform & Security

100 % local; no internet required unless using API models.

Works identically on Windows, Linux, and macOS.

API keys read from environment variables (OPENAI_API_KEY, etc.).

All data stored locally in .orch/.

Summary

The TMAO architecture balances simplicity with depth:

Modular design for fast iteration

Persistent memory for traceability

Rich terminal UX for clarity

Zero external dependencies for easy deployment

It’s built to evolve — lightweight today, powerful tomorrow.