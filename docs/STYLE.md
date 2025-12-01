Style Guide
Overview

This guide defines the coding, documentation, and design conventions for the Terminal Multi-Agent Orchestrator (TMAO) project.
Consistency in style ensures that the codebase remains clean, maintainable, and easy to extend as new agents and features are added.

Code Style
Python Style

Follow PEP 8 with a few readability-focused adjustments.

Imports
# Standard library first
import os
import sys
import asyncio
from typing import Any, Dict, List, Optional

# Third-party packages
from rich.console import Console
from yaml import safe_load

# Local modules last
from src.core.memory import Memory
from src.agents.base_agent import BaseAgent

Naming Conventions
Type	Format	Example
Functions	snake_case	process_task()
Classes	PascalCase	PlannerAgent
Constants	UPPER_SNAKE_CASE	MAX_STEPS = 10
Variables	snake_case	session_id, agent_cache
Type Hints

Always use type hints and docstrings:

def append(self, agent: str, type_: str, payload: Dict[str, Any]) -> None:
    """Append a new memory entry to JSONL file."""
    ...

Strings

Prefer f-strings:

agent_name = "Planner"
print(f"[{agent_name}] Starting new task...")

Async Patterns

Use async/await for any I/O or simulated agent delay.

class BaseAgent:
    async def process(self, task: str) -> str:
        await asyncio.sleep(0.1)
        return f"Processed: {task}"

Documentation
Docstrings

Use concise Google-style docstrings:

class PlannerAgent(BaseAgent):
    """Analyzes user goals and creates subtasks."""

    async def plan(self, goal: str) -> List[str]:
        """Decompose a complex goal into subtasks.

        Args:
            goal: User-provided objective.

        Returns:
            List of subtasks to execute sequentially.
        """
        ...

Comments

Explain why, not what:

# Use cached memory to avoid redundant reads
memories = memory.get_recent()

Directory Structure
src/
├── core/          # orchestration + memory
│   ├── orchestrator.py
│   └── memory.py
├── agents/        # agent definitions
│   ├── base_agent.py
│   ├── planner_agent.py
│   ├── builder_agent.py
│   └── evaluator_agent.py
└── utils/         # helpers and shared logic
    └── logger.py

File Naming

Python files → snake_case.py

Tests → test_<module>.py

Docs → UPPER_SNAKE_CASE.md

Example:
planner_agent.py, test_memory.py, ARCHITECTURE.md

Testing

Use pytest for all testing.

import pytest
from src.core.memory import Memory

@pytest.mark.asyncio
async def test_memory_append_and_get(tmp_path):
    mem = Memory(path=tmp_path / "test.jsonl")
    mem.append("Planner", "thought", {"text": "Check logic"})
    results = mem.get()
    assert results[0]["agent"] == "Planner"


Tests should be fast, isolated, and file-safe.

Error Handling

Define clear exception hierarchy:

class OrchestratorError(Exception):
    """Base orchestrator error."""

class AgentError(OrchestratorError):
    """Errors inside an agent."""

class MemoryError(OrchestratorError):
    """Memory read/write failures."""


Pattern example:

try:
    memory.append(agent, "result", payload)
except Exception as e:
    raise MemoryError(f"Failed to append memory: {e}")

Logging

Use rich for clean terminal output.

from rich.console import Console
console = Console()

console.log("[Planner] Started planning phase")
console.log("[Builder] ✅ Code generation complete")


Keep logs color-coded and human-readable.
Avoid JSON loggers unless exporting to files.

Configuration

All configuration lives in config.yaml.

run:
  policy: sequential
  max_steps: 5

memory:
  path: ".orch/memory.jsonl"

agents:
  - name: Planner
  - name: Builder
  - name: Evaluator


Sensitive values use environment variables as needed.

Performance & Async

Avoid blocking code (e.g., heavy loops, time.sleep).

Use asyncio.gather() for concurrent agent runs.

Cache frequent lookups in memory.

Keep console updates rate-limited to avoid flicker.

Code Review Checklist

- Follows naming and PEP 8
- Uses docstrings and type hints
- No hard-coded secrets
- Proper async usage
- Meaningful commit messages
- Unit tests for new logic

CI Hooks (optional)

Example pre-commit hook:

#!/bin/bash
set -e
black --check src
flake8 src
pytest -q

Guiding Principle

“Readable, traceable, hackable.”

Every contributor should understand the code flow in a single read, and any new agent should drop in seamlessly with the same style.