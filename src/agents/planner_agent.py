"""
Planner Agent Implementation.

This module implements the PlannerAgent which analyzes complex instructions
and breaks them down into structured subtasks for other agents to execute.

The PlannerAgent serves as the strategic coordinator, ensuring complex tasks
are properly decomposed before execution.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
from typing import Any, Dict, List

# Rich import is handled in base_agent.py

from .base_agent import BaseAgent
from src.core.memory import MemoryType

# UI event publishing
try:
    from src.ui.adapters import publish_chat, publish_progress
    UI_ENABLED = True
except ImportError:
    UI_ENABLED = False


class PlannerAgent(BaseAgent):
    """
    Planner Agent for task decomposition and strategic planning.

    The PlannerAgent analyzes complex user instructions and breaks them down
    into manageable subtasks that other specialized agents can execute.
    It serves as the first stage in the orchestration pipeline.

    Attributes:
        Inherits all attributes from BaseAgent
        task_templates: Predefined templates for common task patterns
    """

    def __init__(self, config: Dict[str, Any] = None, shared_memory=None):
        """
        Initialize the PlannerAgent.

        Args:
            config: Configuration dictionary with agent-specific settings
            shared_memory: Optional shared MemoryManager instance
        """
        super().__init__(
            name="Planner",
            role="Task Decomposition & Strategic Planning",
            config=config or {},
            shared_memory=shared_memory
        )

        # Task templates for common patterns
        self.task_templates = {
            "general": [
                "Understand the task requirements",
                "Break down into logical components",
                "Assign responsibilities to sub-agents",
                "Set execution order and dependencies",
                "Execute planned steps",
                "Review and validate results"
            ],
            "code_generation": [
                "Analyze requirements and constraints",
                "Design solution architecture",
                "Implement core functionality",
                "Add error handling and validation",
                "Create tests and documentation",
                "Review and optimize code"
            ],
            "research": [
                "Define research scope and objectives",
                "Gather relevant sources and data",
                "Analyze and synthesize information",
                "Draw conclusions and insights",
                "Document findings and methodology"
            ],
            "documentation": [
                "Understand target audience and purpose",
                "Gather existing information and resources",
                "Structure content outline",
                "Write comprehensive documentation",
                "Review for accuracy and clarity",
                "Format and finalize output"
            ],
            "design": [
                "Analyze design requirements",
                "Create conceptual design",
                "Develop detailed specifications",
                "Review design feasibility",
                "Document design decisions"
            ],
            "testing": [
                "Define testing scope and objectives",
                "Create test cases and scenarios",
                "Execute tests systematically",
                "Analyze test results",
                "Report findings and recommendations"
            ]
        }

    async def process_task(self, task: str, context: Dict[str, Any]) -> str:
        """
        Process a planning task by decomposing it into subtasks.

        Args:
            task: The complex task to decompose and plan
            context: Additional context including constraints, preferences, etc.

        Returns:
            Summary of the planned subtasks and approach

        Raises:
            Exception: If task planning fails due to invalid input or errors
        """
        try:
            await self.log(f"Planning task: {task[:60]}...", style="action")
            await self.update_task_progress(0.1, "Starting analysis")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Planner", f"Analyzing task: {task[:50]}...", "plan", "action")
                await publish_progress("plan", 10.0, "Starting analysis")

            # Parse and understand the task
            task_type = await self._classify_task(task)
            await self.update_task_progress(0.3, f"Classified as: {task_type}")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Planner", f"Task classified as: {task_type}", "plan", "thought")
                await publish_progress("plan", 30.0, f"Classified as {task_type}")

            # Generate subtasks based on task type and content
            if UI_ENABLED:
                await publish_chat("Planner", "Generating subtask breakdown...", "plan", "action")
                await publish_progress("plan", 50.0, "Generating subtasks")
            
            subtasks = await self.generate_subtasks(task, task_type, context)
            await self.update_task_progress(0.7, f"Generated {len(subtasks)} subtasks")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Planner", f"Created {len(subtasks)} subtasks for execution", "plan", "result")
                await publish_progress("plan", 70.0, f"Generated {len(subtasks)} subtasks")

            # Store the complete plan in memory
            plan_data = {
                "original_task": task,
                "task_type": task_type,
                "subtasks": subtasks,
                "context": context,
                "timestamp": asyncio.get_event_loop().time()
            }

            memory_id = await self.memory.store(
                content=plan_data,
                memory_type=MemoryType.WORKING,
                metadata={
                    "agent": self.name,
                    "plan_type": "task_decomposition",
                    "subtask_count": len(subtasks)
                },
                tags={"plan", "decomposition", task_type}
            )

            await self.update_task_progress(0.9, "Storing plan in memory")

            # Create summary
            summary = await self._create_plan_summary(task, subtasks, task_type)

            await self.update_task_progress(1.0, "Planning complete")

            await self.log(f"Plan created with {len(subtasks)} subtasks", style="success")
            await self.log(f"Stored in memory: {memory_id[:8]}", style="info")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Planner", f"✓ Plan complete! {len(subtasks)} subtasks ready for execution", "plan", "result")
                await publish_progress("plan", 100.0, "Planning complete")

            # Store individual subtasks for easy retrieval
            await self._store_subtasks(subtasks, task)

            return summary

        except Exception as e:
            await self.handle_error(e, "task planning")
            raise

    async def generate_subtasks(
        self,
        task: str,
        task_type: str = "general",
        context: Dict[str, Any] = None
    ) -> List[str]:
        """
        Generate a list of subtasks for the given task.

        This method analyzes the task and breaks it down into logical,
        sequential steps that other agents can execute.

        Args:
            task: The main task to decompose
            task_type: The classified type of task
            context: Additional context for planning

        Returns:
            List of subtask strings
        """
        context = context or {}

        # Use template if available
        if task_type in self.task_templates:
            base_subtasks = self.task_templates[task_type]
            await self.log(f"Using {task_type} template with {len(base_subtasks)} steps", style="thought")
        else:
            await self.log("Using general planning template", style="thought")

        # Customize subtasks based on task content and context
        customized_subtasks = []

        for i, subtask_template in enumerate(base_subtasks):
            # Customize based on task content
            if "code" in task.lower():
                if "test" in subtask_template.lower():
                    customized_subtasks.append(f"Create comprehensive tests for {task}")
                elif "document" in subtask_template.lower():
                    customized_subtasks.append(f"Document the implementation of {task}")
                else:
                    customized_subtasks.append(subtask_template)
            elif "research" in task.lower():
                if "gather" in subtask_template.lower():
                    customized_subtasks.append(f"Research and collect data for: {task}")
                elif "analyze" in subtask_template.lower():
                    customized_subtasks.append(f"Analyze research findings from {task}")
                else:
                    customized_subtasks.append(subtask_template)
            else:
                # Generic customization
                customized_subtasks.append(f"{subtask_template} for: {task}")

        # Add context-specific subtasks
        if context.get("include_testing", False):
            customized_subtasks.append("Create and run comprehensive tests")

        if context.get("include_documentation", False):
            customized_subtasks.append("Generate documentation and usage examples")

        if context.get("deadline"):
            customized_subtasks.append(f"Ensure completion by {context['deadline']}")

        # Add task-specific subtasks based on keywords
        task_lower = task.lower()
        if "api" in task_lower or "web" in task_lower:
            customized_subtasks.insert(2, "Design API endpoints and data structures")

        if "database" in task_lower or "storage" in task_lower:
            customized_subtasks.insert(2, "Design database schema and relationships")

        if "ui" in task_lower or "interface" in task_lower:
            customized_subtasks.insert(2, "Design user interface components")

        await self.log(f"Generated {len(customized_subtasks)} customized subtasks", style="thought")

        return customized_subtasks

    async def _classify_task(self, task: str) -> str:
        """
        Classify the task type based on content analysis.

        Args:
            task: The task string to classify

        Returns:
            The classified task type
        """
        task_lower = task.lower()

        # Keyword-based classification
        if any(keyword in task_lower for keyword in ["code", "program", "script", "function", "class"]):
            return "code_generation"
        elif any(keyword in task_lower for keyword in ["research", "analyze", "study", "investigate"]):
            return "research"
        elif any(keyword in task_lower for keyword in ["document", "readme", "guide", "manual"]):
            return "documentation"
        elif any(keyword in task_lower for keyword in ["design", "architecture", "structure"]):
            return "design"
        elif any(keyword in task_lower for keyword in ["test", "validate", "verify", "check"]):
            return "testing"
        else:
            return "general"

    async def _create_plan_summary(self, task: str, subtasks: List[str], task_type: str) -> str:
        """
        Create a formatted summary of the planning results.

        Args:
            task: The original task
            subtasks: The generated subtasks
            task_type: The classified task type

        Returns:
            Formatted summary string
        """
        summary = f"""
🎯 **Task Planning Summary**

**Original Task:** {task}

**Classification:** {task_type.replace('_', ' ').title()}

**Plan Overview:**
- Total Subtasks: {len(subtasks)}
- Estimated Complexity: {'High' if len(subtasks) > 5 else 'Medium' if len(subtasks) > 3 else 'Low'}

**Detailed Subtasks:**
"""

        for i, subtask in enumerate(subtasks, 1):
            summary += f"{i:2d}. {subtask}\n"

        summary += f"\n✅ Planning phase complete. Ready for execution by specialized agents."

        return summary.strip()

    async def _store_subtasks(self, subtasks: List[str], original_task: str) -> None:
        """
        Store individual subtasks in memory for easy retrieval.

        Args:
            subtasks: List of subtask strings
            original_task: The original task they belong to
        """
        for i, subtask in enumerate(subtasks):
            await self.memory.store(
                content=subtask,
                memory_type=MemoryType.PROCEDURAL,
                metadata={
                    "agent": self.name,
                    "original_task": original_task,
                    "subtask_index": i,
                    "total_subtasks": len(subtasks)
                },
                tags={"subtask", "planned", f"step_{i+1}"}
            )

    async def get_recent_plans(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve recently created plans from memory.

        Args:
            limit: Maximum number of plans to retrieve

        Returns:
            List of recent planning results
        """
        from src.core.memory import MemoryQuery

        # Search for plans by agent and metadata
        query = MemoryQuery(
            text="plan",  # Search for plans in general
            memory_type=MemoryType.WORKING,
            limit=limit * 3  # Get more to filter
        )

        results = await self.memory.retrieve(query)

        # Filter to only task decomposition plans from this agent
        filtered_results = []
        for item in results:
            if (item.metadata.get("agent") == self.name and
                item.metadata.get("plan_type") == "task_decomposition"):
                filtered_results.append(item)

        # Sort by creation time (newest first)
        filtered_results.sort(key=lambda x: x.created_at, reverse=True)

        return [
            {
                "id": item.id,
                "content": item.content,
                "metadata": item.metadata,
                "tags": item.tags,
                "created_at": item.created_at.isoformat()
            }
            for item in filtered_results[:limit]
        ]

    async def optimize_plan(self, plan_id: str, optimization_goal: str) -> str:
        """
        Optimize an existing plan based on specific goals.

        Args:
            plan_id: The memory ID of the plan to optimize
            optimization_goal: The optimization objective (speed, quality, cost, etc.)

        Returns:
            Optimized plan summary
        """
        try:
            await self.log(f"Optimizing plan {plan_id[:8]} for: {optimization_goal}", style="action")

            # Retrieve the original plan
            from src.core.memory import MemoryQuery

            query = MemoryQuery(
                text=f"id:{plan_id}",
                limit=1
            )

            # Use direct get method instead of query for specific ID
            plan_item = self.memory.get(plan_id)
            
            if not plan_item:
                raise ValueError(f"Plan {plan_id} not found in memory")

            original_plan = plan_item.content
            
            if not isinstance(original_plan, dict):
                raise ValueError(f"Plan {plan_id} content is not structured (got {type(original_plan)})")

            # Apply optimization logic based on goal
            optimized_subtasks = await self._apply_optimization(
                original_plan["subtasks"],
                optimization_goal
            )

            # Create optimized plan
            optimized_plan = original_plan.copy()
            optimized_plan["subtasks"] = optimized_subtasks
            optimized_plan["optimization_goal"] = optimization_goal
            optimized_plan["optimization_timestamp"] = asyncio.get_event_loop().time()

            # Store optimized plan
            memory_id = await self.memory.store(
                content=optimized_plan,
                memory_type=MemoryType.WORKING,
                metadata={
                    "agent": self.name,
                    "plan_type": "optimized_decomposition",
                    "original_plan_id": plan_id,
                    "optimization_goal": optimization_goal
                },
                tags={"plan", "optimized", optimization_goal}
            )

            summary = await self._create_plan_summary(
                original_plan["original_task"],
                optimized_subtasks,
                f"{original_plan['task_type']}_optimized"
            )

            await self.log(f"Plan optimization complete: {memory_id[:8]}", style="success")

            return summary

        except Exception as e:
            await self.handle_error(e, "plan optimization")
            raise

    async def _apply_optimization(self, subtasks: List[str], goal: str) -> List[str]:
        """
        Apply optimization logic to subtasks based on the goal.

        Args:
            subtasks: Original list of subtasks
            goal: Optimization goal

        Returns:
            Optimized list of subtasks
        """
        optimized = subtasks.copy()

        if goal == "speed":
            # Prioritize parallelizable tasks
            await self.log("Applying speed optimization (parallel execution)", style="thought")
            new_steps = ["Execute independent tasks in parallel where possible"]
            optimized.extend([step for step in new_steps if step not in optimized])

        elif goal == "quality":
            # Add more review and validation steps
            await self.log("Applying quality optimization (enhanced validation)", style="thought")
            new_steps = [
                "Conduct thorough quality review and validation",
                "Apply final quality assurance checks"
            ]
            # Insert quality check before the last step (review)
            if len(optimized) > 1:
                # Insert before any existing review step
                for i, step in enumerate(optimized):
                    if "review" in step.lower():
                        optimized.insert(i, new_steps[0])
                        break
                else:
                    optimized.insert(-1, new_steps[0])

                # Add final check at the end
                optimized.append(new_steps[1])

        elif goal == "cost":
            # Optimize for resource efficiency
            await self.log("Applying cost optimization (resource efficiency)", style="thought")
            new_steps = ["Optimize resource usage and minimize costs"]
            optimized.extend([step for step in new_steps if step not in optimized])

        elif goal == "reliability":
            # Add redundancy and error handling
            await self.log("Applying reliability optimization (redundancy)", style="thought")
            new_steps = [
                "Add error handling and recovery mechanisms",
                "Implement comprehensive logging and monitoring"
            ]
            optimized.extend([step for step in new_steps if step not in optimized])

        # Remove any duplicates that might have been created
        optimized = list(dict.fromkeys(optimized))

        return optimized
