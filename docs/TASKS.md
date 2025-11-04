Tasks Documentation
Overview

Tasks in the Terminal Multi-Agent Orchestrator (TMAO) represent discrete units of work coordinated between local agents.
Each task is self-contained, human-readable, and traceable — designed to execute seamlessly inside any terminal on Windows, Linux, or macOS.

A task can be as simple as “summarize this file” or as complex as “plan, generate, and evaluate a Python script.”

Task Lifecycle
┌─────────────┐ → ┌──────────────┐ → ┌─────────────┐ → ┌─────────────┐
│  Created    │   │  Assigned    │   │ Processing  │   │ Completed   │
└─────────────┘   └──────────────┘   └─────────────┘   └─────────────┘
          ↘             ↘                  ↘
          Failed     Cancelled          Expired

States
State	Description
Created	Task initialized and stored in the local JSONL memory
Assigned	Assigned to the most suitable agent based on capabilities
Processing	Agent actively working on it
Completed	Task finished successfully
Failed	Error during processing; eligible for retry
Cancelled	Manually stopped by user
Expired	Timed out or stale
Task Types
🟢 Simple Tasks

Single-agent operations such as:

Code snippet generation

Local file reading or summarization

Memory query

🟡 Composite Tasks

Multi-step tasks where several agents cooperate:

Planner → Builder → Evaluator pipeline

Research and report generation

Documentation workflow

🔵 Workflow Tasks

Reusable, predefined sequences stored as templates (YAML or JSON).
Example:

name: "Code Review Workflow"
steps:
  - agent: Planner
    action: "parse_requirements"
  - agent: Builder
    action: "generate_code"
  - agent: Evaluator
    action: "review_code"

Task Representation

Each task is stored as a JSONL object in .orch/tasks.jsonl.

{
  "id": "task_20251024_183200",
  "name": "Summarize research.md",
  "type": "simple",
  "status": "processing",
  "priority": "medium",
  "assigned_agent": "ReaderAgent",
  "input": "research.md",
  "output": null,
  "created_at": "2025-10-24T18:32:00",
  "progress": 0.65
}

Local Task Management
Create Task
from src.core.tasks import create_task

task = create_task(
    name="Generate README summary",
    type="simple",
    input_data={"file": "README.md"},
    priority="high"
)

Assign to Agent
from src.core.assigner import assign_task
assign_task(task)

Execute Task
await orchestrator.run(task)

Priority Levels
Level	Description
critical	Must run immediately
high	Preferential scheduling
medium	Default
low	Background, idle time only
Retry & Recovery

If a task fails, it’s retried up to max_retries (default: 2).
Example configuration in config.yaml:

tasks:
  max_retries: 2
  retry_delay: 1.0  # seconds

Task Queue (Local)

The orchestrator keeps a simple async priority queue in memory:

queue = {
  "critical": [],
  "high": [],
  "medium": [],
  "low": []
}


Tasks are dequeued based on priority and fed into agent coroutines.

Task Templates

Templates live in /templates/:

name: "Research Workflow"
agents:
  - Planner
  - Researcher
  - Writer
steps:
  - "Plan research outline"
  - "Collect sources"
  - "Summarize findings"
  - "Generate final report"


Use:

tmao run-template research.yaml

Monitoring

Each task has real-time terminal feedback using rich progress bars.

Example:

[PlannerAgent] Planning research outline...  ✅
[ResearchAgent] Collecting data...           78%
[WriterAgent] Drafting summary...            42%


All logs are also stored in .orch/logs/.

Error Handling

When errors occur:

The orchestrator logs the full traceback to .orch/errors.log

Retries automatically with exponential backoff

Marks as FAILED if retries exceed limit

Best Practices
✅ Task Design

Keep tasks atomic (small, self-contained)

Make tasks idempotent (safe to retry)

Avoid hidden global state

Always log start and end time

⚡ Performance

Parallelize independent subtasks using asyncio.gather

Keep memory reads/writes minimal

Reuse existing task results via memory caching

🧠 Observability

Use console.log() from rich for every major agent event

Persist progress and results to .orch/memory.jsonl

Example Flow
$ tmao new "Build AI chatbot demo"
> [Planner] → Breaking task into subtasks...
> [Builder] → Writing Python skeleton...
> [Evaluator] → Checking for logical errors...
> ✅ Task Completed in 8.2s

Future Enhancements

Dynamic task splitting via meta-planner

Shared memory index for agent collaboration

Rich TUI dashboard (optional tui mode)

Remote task sync via SSH / REST adapter (optional)

Conclusion

The TMAO Task System combines simplicity with extensibility — every task can be observed, retried, extended, and explained.
It’s designed to feel alive in the terminal: readable logs, visual feedback, and collaborative AI behavior — all without needing any cloud infrastructure.