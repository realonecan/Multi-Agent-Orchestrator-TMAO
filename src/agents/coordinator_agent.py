"""
Coordinator Agent Implementation.

This module implements the CoordinatorAgent which orchestrates the complete
multi-agent workflow from task input to final reviewed output. It serves as
the main conductor that coordinates Planner → Builder → Reviewer pipeline.

The CoordinatorAgent provides a single entry point for complex task automation.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
from typing import Any, Dict, Optional

from .base_agent import BaseAgent
from .planner_agent import PlannerAgent
from .builder_agent import BuilderAgent
from .reviewer_agent import ReviewerAgent
from src.core.memory import MemoryType

# UI event publishing
try:
    from src.ui.adapters import publish_chat, publish_progress
    from src.ui.event_bus import event_bus
    UI_ENABLED = True
except ImportError:
    UI_ENABLED = False


class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent for multi-agent workflow orchestration.

    The CoordinatorAgent serves as the central conductor that orchestrates
    the complete pipeline: Planner creates plans, Builder executes them,
    and Reviewer evaluates the results. It provides a single entry point
    for complex task automation and maintains the overall workflow state.

    Attributes:
        Inherits all attributes from BaseAgent
        planner: PlannerAgent instance for task decomposition
        builder: BuilderAgent instance for task execution
        reviewer: ReviewerAgent instance for quality assessment
        mode: Orchestration mode (auto/manual)
        max_retries: Maximum retry attempts for failed stages
        enable_parallel: Whether to enable parallel execution
    """

    def __init__(self, config: Dict[str, Any] = None, shared_memory=None):
        """
        Initialize the CoordinatorAgent.

        Args:
            config: Configuration dictionary with coordinator-specific settings
            shared_memory: Optional shared MemoryManager instance
        """
        super().__init__(
            name="Coordinator",
            role="Workflow Orchestration",
            config=config or {},
            shared_memory=shared_memory
        )

        # Coordinator configuration
        coordinator_config = self.config.get("coordinator", {})
        self.mode = coordinator_config.get("mode", "auto")
        self.max_retries = coordinator_config.get("max_retries", 2)
        self.enable_parallel = coordinator_config.get("enable_parallel", True)

        # Agent instances (will share memory with coordinator)
        self.planner: Optional[PlannerAgent] = None
        self.builder: Optional[BuilderAgent] = None
        self.reviewer: Optional[ReviewerAgent] = None

        # Orchestration state
        self._active_orchestrations = {}

    async def process_task(self, task: str, context: Dict[str, Any]) -> str:
        """
        Process a coordination task by running the full orchestration pipeline.

        Args:
            task: The high-level task to orchestrate
            context: Additional context for the orchestration

        Returns:
            Summary of the orchestration results

        Raises:
            Exception: If orchestration fails
        """
        try:
            await self.log(f"🎯 Orchestrating task: {task[:60]}...", style="action")
            await self.update_task_progress(0.1, "Starting orchestration")

            # Run the complete orchestration pipeline
            orchestration_result = await self.orchestrate(task, context)

            await self.update_task_progress(1.0, "Orchestration complete")

            # Create comprehensive summary
            summary = await self._create_orchestration_summary(orchestration_result)

            await self.log(f"✅ Orchestration completed: {orchestration_result['summary']['final_score']:.1%} final score", style="success")

            # Store orchestration metadata
            await self._store_orchestration(orchestration_result)

            return summary

        except Exception as e:
            await self.handle_error(e, "orchestration")
            raise

    async def orchestrate(self, task: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run the complete plan-build-review orchestration cycle.

        Args:
            task: The high-level task to process (if None, prompts user for input)
            context: Additional context for orchestration (framework, style, etc.)

        Returns:
            Structured orchestration report with all intermediate IDs and results

        Raises:
            Exception: If any stage of orchestration fails
        """
        context = context or {}
        
        # Get task from user if not provided (async-safe prompt)
        if not task:
            loop = asyncio.get_event_loop()
            def _prompt() -> str:
                try:
                    return input("\n🎯 Enter orchestration task: ").strip()
                except Exception:
                    return ""
            task = await loop.run_in_executor(None, _prompt)
            if not task:
                task = "Build a simple Python calculator with basic operations"
                print(f"   Using default task: {task}")
        
        await self.log(f"🎯 Starting orchestration: {task[:60]}...", style="action")
        await self.update_task_progress(0.1, "Initializing orchestration")
        
        # Publish to UI
        if UI_ENABLED:
            await publish_chat("Coordinator", f"Starting orchestration: {task[:50]}...", "coord", "action")
            await event_bus.publish("orchestrate.start", {"task": task})

        orchestration_id = f"orch_{asyncio.get_event_loop().time()}"
        self._active_orchestrations[orchestration_id] = {
            "task": task,
            "status": "running",
            "start_time": asyncio.get_event_loop().time()
        }

        # Stage 1: Planning
        await self.log(f"📋 Stage 1: Planning task with PlannerAgent", style="thought")
        await self.update_task_progress(0.2, "Planning phase")
        
        # Publish to UI
        if UI_ENABLED:
            await publish_chat("Coordinator", "Delegating to Planner...", "coord", "action")

        try:
            plan_result = await self._execute_with_retry(
                lambda: self._run_planner_stage(task, context),
                "planning",
                orchestration_id
            )

            plan_id = plan_result["plan_id"]
            await self.log(f"✅ Planning complete: {plan_id[:8]}", style="success")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Coordinator", f"Planner completed: {plan_id[:8]}", "coord", "result")

            # Stage 2: Building
            await self.log(f"🔨 Stage 2: Executing plan with BuilderAgent", style="thought")
            await self.update_task_progress(0.5, "Building phase")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Coordinator", "Delegating to Builder...", "coord", "action")

            execution_result = await self._execute_with_retry(
                lambda: self._run_builder_stage(task, plan_id, context),
                "building",
                orchestration_id
            )

            execution_id = execution_result["execution_id"]
            await self.log(f"✅ Building complete: {execution_id[:8]}", style="success")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Coordinator", f"Builder completed: {execution_id[:8]}", "coord", "result")

            # Stage 3: Review
            await self.log(f"🔍 Stage 3: Reviewing execution with ReviewerAgent", style="thought")
            await self.update_task_progress(0.8, "Review phase")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Coordinator", "Delegating to Reviewer...", "coord", "action")

            review_result = await self._execute_with_retry(
                lambda: self._run_reviewer_stage(plan_id, execution_id),
                "reviewing",
                orchestration_id
            )

            review_id = review_result["review_id"]
            await self.log(f"✅ Review complete: {review_id[:8]}", style="success")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Coordinator", f"Reviewer completed: {review_id[:8]}", "coord", "result")

            # Compile final results
            await self.update_task_progress(1.0, "Compiling results")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Coordinator", "Compiling final results...", "coord", "action")

            orchestration_result = {
                "orchestration_id": orchestration_id,
                "task": task,
                "plan_id": plan_id,
                "execution_id": execution_id,
                "review_id": review_id,
                "summary": {
                    "accuracy": review_result["accuracy"],
                    "quality": review_result["quality"],
                    "final_score": review_result["final_score"],
                    "notes": review_result["notes"]
                },
                "stage_results": {
                    "planning": plan_result,
                    "building": execution_result,
                    "reviewing": review_result
                },
                "metadata": {
                    "mode": self.mode,
                    "parallel_enabled": self.enable_parallel,
                    "start_time": self._active_orchestrations[orchestration_id]["start_time"],
                    "end_time": asyncio.get_event_loop().time(),
                    "duration": asyncio.get_event_loop().time() - self._active_orchestrations[orchestration_id]["start_time"]
                }
            }

            # Clean up active orchestration
            self._active_orchestrations[orchestration_id]["status"] = "complete"
            self._active_orchestrations[orchestration_id]["result"] = orchestration_result

            await self.log(f"🎉 Orchestration {orchestration_id} completed successfully", style="success")
            
            # Publish to UI
            if UI_ENABLED:
                final_score = review_result["final_score"]
                await publish_chat("Coordinator", f"✓ Orchestration complete! Final score: {final_score:.1%}", "coord", "result")

            return orchestration_result

        except Exception as e:
            # Mark orchestration as failed
            if orchestration_id in self._active_orchestrations:
                self._active_orchestrations[orchestration_id]["status"] = "failed"
                self._active_orchestrations[orchestration_id]["error"] = str(e)

            await self.log(f"❌ Orchestration {orchestration_id} failed: {str(e)}", style="error")
            raise

    async def _run_planner_stage(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the planning stage using PlannerAgent.

        Args:
            task: The task to plan
            context: Planning context

        Returns:
            Planning stage results with plan_id
        """
        # Initialize PlannerAgent if needed (with shared memory)
        if not self.planner:
            self.planner = PlannerAgent(
                config=self.config.get("planner", {}),
                shared_memory=self.memory
            )
            await self.planner.initialize()

        # Run planning
        plan_summary = await self.planner.process_task(task, context)

        # Get the plan ID using shared memory directly
        from src.core.memory import MemoryQuery

        # Search for recent plans in shared memory - use broader search
        query = MemoryQuery(
            text="task",  # Broader search term
            memory_type=MemoryType.WORKING,
            limit=10  # Get more results to filter
        )

        results = await self.memory.retrieve(query)

        # Find the most recent plan from this orchestration
        plan_results = []
        for item in results:
            # Check metadata for plan type
            if item.metadata.get("plan_type") == "task_decomposition":
                # Handle both dict and string content
                content = item.content
                if isinstance(content, str):
                    # Skip string content - we need structured data
                    continue
                elif isinstance(content, dict) and content.get("original_task") == task:
                    plan_results.append(item)

        # Sort by timestamp (newest first)
        plan_results.sort(key=lambda x: x.created_at, reverse=True)

        if not plan_results:
            raise ValueError("No plan generated by PlannerAgent")

        plan_id = plan_results[0].id

        # Verify the plan exists and has subtasks
        plan_item = self.memory.get(plan_id)
        if not plan_item or not isinstance(plan_item.content, dict):
            raise ValueError(f"Plan {plan_id} not found or malformed")

        return {
            "plan_id": plan_id,
            "summary": plan_summary,
            "stage": "planning"
        }

    async def _run_builder_stage(self, task: str, plan_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the building stage using BuilderAgent.

        Args:
            task: The original task
            plan_id: The plan to execute
            context: Building context

        Returns:
            Building stage results with execution_id
        """
        # Initialize BuilderAgent if needed (with shared memory)
        if not self.builder:
            builder_config = self.config.get("builder", {})
            # Configure execution mode based on coordinator settings
            if "execution_mode" not in builder_config:
                builder_config["execution_mode"] = "parallel" if self.enable_parallel else "sequential"

            self.builder = BuilderAgent(
                config=builder_config,
                shared_memory=self.memory
            )
            await self.builder.initialize()

        # Get the plan data to pass directly to builder
        plan_item = self.memory.get(plan_id)
        if not plan_item or not isinstance(plan_item.content, dict):
            raise ValueError(f"Plan {plan_id} not found or malformed")

        plan_data = plan_item.content
        subtasks = plan_data.get("subtasks", [])

        if not subtasks:
            raise ValueError(f"No subtasks found in plan {plan_id}")

        # Run building with plan data in context - ensure BuilderAgent uses it
        build_context = {
            "plan_id": plan_id,
            "plan_data": plan_data,  # This ensures BuilderAgent uses the data directly
            "subtasks": subtasks,    # This provides the subtasks directly
            "execution_mode": "parallel" if self.enable_parallel else "sequential",
            **context
        }

        build_summary = await self.builder.process_task(task, build_context)

        # Get the execution ID using shared memory directly
        from src.core.memory import MemoryQuery

        # Search for recent execution results in shared memory - use broader search
        query = MemoryQuery(
            text="build",  # Broader search term
            memory_type=MemoryType.WORKING,
            limit=10  # Get more results to filter
        )

        results = await self.memory.retrieve(query)

        # Find the most recent execution from this orchestration
        execution_results = []
        for item in results:
            # Check if this has execution-related tags
            if "execution" in item.tags or "build" in item.tags:
                # Handle both dict and string content
                content = item.content
                if isinstance(content, str):
                    # Skip string content - we need structured data
                    continue
                elif isinstance(content, dict) and content.get("task") == task:
                    execution_results.append(item)

        # Sort by timestamp (newest first)
        execution_results.sort(key=lambda x: x.created_at, reverse=True)

        if not execution_results:
            raise ValueError("No execution generated by BuilderAgent")

        execution_id = execution_results[0].id

        # Verify the execution exists and has results
        execution_item = self.memory.get(execution_id)
        if not execution_item or not isinstance(execution_item.content, dict):
            raise ValueError(f"Execution {execution_id} not found or malformed")

        return {
            "execution_id": execution_id,
            "summary": build_summary,
            "stage": "building"
        }

    async def _run_reviewer_stage(self, plan_id: str, execution_id: str) -> Dict[str, Any]:
        """
        Execute the review stage using ReviewerAgent.

        Args:
            plan_id: The plan to review against
            execution_id: The execution to review

        Returns:
            Review stage results with review_id
        """
        # Initialize ReviewerAgent if needed (with shared memory)
        if not self.reviewer:
            reviewer_config = self.config.get("reviewer", {})
            self.reviewer = ReviewerAgent(
                config=reviewer_config,
                shared_memory=self.memory
            )
            await self.reviewer.initialize()

        # Get the execution data to pass directly to reviewer
        execution_item = self.memory.get(execution_id)
        if not execution_item or not isinstance(execution_item.content, dict):
            raise ValueError(f"Execution {execution_id} not found or malformed")

        execution_data = execution_item.content

        # Get the original task from the plan for the review message
        plan_item = self.memory.get(plan_id)
        original_task = plan_item.content.get("original_task", "task") if plan_item and isinstance(plan_item.content, dict) else "task"
        
        # Run review with execution data in context
        review_context = {
            "plan_id": plan_id,
            "execution_id": execution_id,
            "execution_data": execution_data,
            "review_mode": "auto"
        }

        review_result = await self.reviewer.process_task(f"Review execution of: {original_task}", review_context)

        # Get the review ID using shared memory directly
        from src.core.memory import MemoryQuery

        # Search for recent review results in shared memory - use broader search
        query = MemoryQuery(
            text="review",  # Broader search term
            memory_type=MemoryType.EPISODIC,
            limit=10  # Get more results to filter
        )

        results = await self.memory.retrieve(query)

        # Find the most recent review from this orchestration
        review_results = []
        for item in results:
            # Check metadata for review type
            if item.metadata.get("review_type") == "execution_review":
                # Handle both dict and string content
                content = item.content
                if isinstance(content, str):
                    # Skip string content - we need structured data
                    continue
                elif isinstance(content, dict) and content.get("plan_id") == plan_id:
                    review_results.append(item)

        # Sort by timestamp (newest first)
        review_results.sort(key=lambda x: x.created_at, reverse=True)

        if not review_results:
            raise ValueError("No review generated by ReviewerAgent")

        review_id = review_results[0].id

        # Verify the review exists and has results
        review_item = self.memory.get(review_id)
        if not review_item or not isinstance(review_item.content, dict):
            raise ValueError(f"Review {review_id} not found or malformed")

        # Add review_id to the result
        review_result["review_id"] = review_id

        return review_result

    async def _execute_with_retry(self, stage_func, stage_name: str, orchestration_id: str) -> Any:
        """
        Execute a stage with retry logic.

        Args:
            stage_func: The async function to execute
            stage_name: Name of the stage for logging
            orchestration_id: Current orchestration ID

        Returns:
            Stage execution results

        Raises:
            Exception: If all retry attempts fail
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                await self.log(f"🔄 {stage_name.capitalize()} attempt {attempt + 1}/{self.max_retries + 1}", style="thought")

                # Update orchestration status
                self._active_orchestrations[orchestration_id]["status"] = f"{stage_name}_attempt_{attempt + 1}"

                result = await stage_func()

                await self.log(f"✅ {stage_name.capitalize()} succeeded on attempt {attempt + 1}", style="success")
                return result

            except Exception as e:
                last_error = e
                await self.log(f"❌ {stage_name.capitalize()} failed on attempt {attempt + 1}: {str(e)}", style="warning")

                if attempt < self.max_retries:
                    await self.log(f"🔄 Retrying {stage_name} in {2 ** attempt} seconds...", style="thought")
                    await self.sleep(2 ** attempt)  # Exponential backoff
                else:
                    await self.log(f"💥 {stage_name.capitalize()} failed after {self.max_retries + 1} attempts", style="error")

        # All retries failed
        raise last_error

    async def _create_orchestration_summary(self, orchestration_result: Dict[str, Any]) -> str:
        """
        Create a comprehensive summary of the orchestration results.

        Args:
            orchestration_result: The complete orchestration data

        Returns:
            Formatted summary string
        """
        summary = orchestration_result["summary"]
        metadata = orchestration_result["metadata"]

        formatted_summary = f"""
🎭 **Multi-Agent Orchestration Summary**

**Task:** {orchestration_result['task']}

**Orchestration ID:** {orchestration_result['orchestration_id']}

**Pipeline Results:**
📋 **Planning** → {orchestration_result['plan_id'][:8]}
🔨 **Building** → {orchestration_result['execution_id'][:8]}
🔍 **Review** → {orchestration_result['review_id'][:8]}

**Quality Metrics:**
- Accuracy: {summary['accuracy']:.1%} ({summary['accuracy']*100:.1f}/100)
- Quality: {summary['quality']:.1%} ({summary['quality']*100:.1f}/100)
- **Final Score: {summary['final_score']:.1%} ({summary['final_score']*100:.1f}/100)**
**Performance:**
- Duration: {metadata['duration']:.1f} seconds
- Mode: {metadata['mode']}
- Parallel: {'Enabled' if metadata['parallel_enabled'] else 'Disabled'}

**Notes:** {summary['notes']}

**Stage Details:**
- Planning: {'✅ Success' if orchestration_result['stage_results']['planning'] else '❌ Failed'}
- Building: {'✅ Success' if orchestration_result['stage_results']['building'] else '❌ Failed'}
- Review: {'✅ Success' if orchestration_result['stage_results']['reviewing'] else '❌ Failed'}

✅ **Orchestration complete.** All agents coordinated successfully.
        """

        return formatted_summary.strip()

    async def _store_orchestration(self, orchestration_result: Dict[str, Any]) -> None:
        """
        Store the orchestration results in memory.

        Args:
            orchestration_result: The complete orchestration data
        """
        await self.memory.store(
            content=orchestration_result,
            memory_type=MemoryType.EPISODIC,
            metadata={
                "agent": self.name,
                "orchestration_type": "full_pipeline",
                "task": orchestration_result["task"],
                "final_score": orchestration_result["summary"]["final_score"],
                "accuracy": orchestration_result["summary"]["accuracy"],
                "quality": orchestration_result["summary"]["quality"],
                "duration": orchestration_result["metadata"]["duration"]
            },
            tags={"orchestration", "summary", "pipeline"}
        )

        await self.log(f"💾 Orchestration stored in memory", style="info")

    async def get_orchestration_history(self, limit: int = 10) -> Dict[str, Any]:
        """
        Retrieve recent orchestration history.

        Args:
            limit: Maximum number of orchestrations to retrieve

        Returns:
            Dictionary with orchestration summaries and details
        """
        from src.core.memory import MemoryQuery

        query = MemoryQuery(
            text="orchestration_type:full_pipeline",
            memory_type=MemoryType.EPISODIC,
            limit=limit
        )

        results = await self.memory.retrieve(query)

        # Filter to only orchestrations from this coordinator
        filtered_results = [
            item for item in results
            if item.metadata.get("agent") == self.name
        ]

        # Sort by timestamp (newest first)
        filtered_results.sort(key=lambda x: x.created_at, reverse=True)

        return {
            "total_orchestrations": len(filtered_results),
            "orchestrations": [
                {
                    "id": item.id,
                    "content": item.content,
                    "metadata": item.metadata,
                    "created_at": item.created_at.isoformat()
                }
                for item in filtered_results[:limit]
            ]
        }

    async def get_orchestration_status(self, orchestration_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a specific orchestration.

        Args:
            orchestration_id: The orchestration ID to check

        Returns:
            Orchestration status and details, or None if not found
        """
        if orchestration_id in self._active_orchestrations:
            return self._active_orchestrations[orchestration_id]

        # Check completed orchestrations in memory
        history = await self.get_orchestration_history(limit=50)
        for orch in history["orchestrations"]:
            if orch["content"]["orchestration_id"] == orchestration_id:
                return {
                    "status": "complete",
                    "result": orch["content"],
                    "metadata": orch["metadata"]
                }

        return None

    async def initialize(self) -> None:
        """
        Initialize the CoordinatorAgent and all sub-agents.

        This method initializes the coordinator and prepares all sub-agents
        for orchestration tasks.
        """
        await super().initialize()

        # Initialize sub-agents if needed
        if self.planner and not self.planner.is_active():
            await self.planner.initialize()

        if self.builder and not self.builder.is_active():
            await self.builder.initialize()

        if self.reviewer and not self.reviewer.is_active():
            await self.reviewer.initialize()

        await self.log(f"🤖 {self.name} ({self.role}) ready for orchestration", style="success")

    async def shutdown(self) -> None:
        """
        Shutdown the CoordinatorAgent and all sub-agents.

        This method cleanly shuts down all agents in the orchestration pipeline.
        """
        # Shutdown sub-agents
        if self.planner and self.planner.is_active():
            await self.planner.shutdown()

        if self.builder and self.builder.is_active():
            await self.builder.shutdown()

        if self.reviewer and self.reviewer.is_active():
            await self.reviewer.shutdown()

        await super().shutdown()

        await self.log(f"🛑 {self.name} orchestration pipeline shutdown complete", style="info")

    def is_active(self) -> bool:
        """
        Check if the coordinator and its sub-agents are active.

        Returns:
            True if coordinator and all sub-agents are active
        """
        base_active = super().is_active()

        # Check sub-agents
        planner_active = not self.planner or self.planner.is_active()
        builder_active = not self.builder or self.builder.is_active()
        reviewer_active = not self.reviewer or self.reviewer.is_active()

        return base_active and planner_active and builder_active and reviewer_active
