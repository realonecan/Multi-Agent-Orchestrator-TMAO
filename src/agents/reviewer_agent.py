"""
Reviewer Agent Implementation.

This module implements the ReviewerAgent which evaluates the BuilderAgent's execution
results against the PlannerAgent's original plan. It provides structured review,
scoring metrics, and quality assessment for the multi-agent orchestration system.

The ReviewerAgent serves as the quality assurance component in the pipeline.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import numpy as np
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent
from src.core.memory import MemoryType, MemoryQuery

# UI event publishing
try:
    from src.ui.adapters import publish_chat, publish_progress, publish_metrics
    UI_ENABLED = True
except ImportError:
    UI_ENABLED = False


class ReviewerAgent(BaseAgent):
    """
    Reviewer Agent for quality assessment and evaluation.

    The ReviewerAgent analyzes BuilderAgent execution results against PlannerAgent
    plans to provide structured reviews, scoring metrics, and improvement suggestions.
    It ensures quality control and provides feedback for the orchestration system.

    Attributes:
        Inherits all attributes from BaseAgent
        evaluation_mode: How to perform evaluations (auto/manual)
        scoring_weights: Weights for accuracy vs quality in final score
    """

    def __init__(self, config: Dict[str, Any] = None, shared_memory=None):
        """
        Initialize the ReviewerAgent.

        Args:
            config: Configuration dictionary with agent-specific settings
            shared_memory: Optional shared MemoryManager instance
        """
        super().__init__(
            name="Reviewer",
            role="Evaluation & Feedback",
            config=config or {},
            shared_memory=shared_memory
        )

        # Review configuration
        reviewer_config = self.config.get("reviewer", {})
        self.evaluation_mode = reviewer_config.get("evaluation_mode", "auto")
        self.scoring_weights = reviewer_config.get("scoring_weights", {
            "accuracy": 0.6,
            "quality": 0.4
        })

        # Review state
        self._review_history = []

    async def process_task(self, task: str, context: Dict[str, Any]) -> str:
        """
        Process a review task by evaluating execution against plans.

        Args:
            task: The review task description
            context: Context including plan_id and builder_id to review

        Returns:
            Summary of the review results

        Raises:
            Exception: If review process fails
        """
        try:
            await self.log(f"🔍 Reviewing task: {task[:60]}...", style="action")
            await self.update_task_progress(0.1, "Starting review")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Reviewer", f"Starting review: {task[:50]}...", "review", "action")
                await publish_progress("review", 10.0, "Starting review")

            # Get required IDs from context
            plan_id = context.get("plan_id")
            execution_id = context.get("execution_id")

            if not plan_id:
                raise ValueError("plan_id required for review")

            await self.update_task_progress(0.2, f"Found plan: {plan_id[:8]}")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Reviewer", f"Analyzing plan {plan_id[:8]}...", "review", "thought")

            # Retrieve the original plan
            plan_item = self.memory.get(plan_id)
            if not plan_item:
                raise ValueError(f"Plan {plan_id} not found in memory")

            plan_data = plan_item.content
            if not isinstance(plan_data, dict):
                raise ValueError(f"Plan data is not structured (got {type(plan_data)})")

            await self.update_task_progress(0.3, "Retrieved plan")

            # Check if execution_data is provided directly in context (from CoordinatorAgent)
            execution_data = context.get("execution_data")
            if execution_data and isinstance(execution_data, dict):
                await self.log(f"🔍 Using execution data from context", style="info")
            elif execution_id:
                # Retrieve execution results as fallback
                await self.log(f"🔍 No execution data in context, retrieving from memory", style="thought")
                execution_item = self.memory.get(execution_id)
                if not execution_item:
                    raise ValueError(f"Execution {execution_id} not found in memory")

                execution_data = execution_item.content
                if not isinstance(execution_data, dict):
                    raise ValueError(f"Execution data is not structured (got {type(execution_data)})")
            else:
                raise ValueError("Either execution_data or execution_id required for review")

            await self.update_task_progress(0.5, "Retrieved execution")

            # Extract subtasks and results
            plan_subtasks = plan_data.get("subtasks", [])
            execution_results = execution_data.get("execution_results", [])

            if not plan_subtasks:
                raise ValueError("No subtasks found in plan")

            await self.update_task_progress(0.6, f"Analyzing {len(plan_subtasks)} subtasks")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Reviewer", f"Evaluating {len(plan_subtasks)} subtasks...", "review", "action")
                await publish_progress("review", 60.0, f"Analyzing {len(plan_subtasks)} subtasks")

            # Perform detailed analysis
            review_details = await self._analyze_execution(plan_subtasks, execution_results)

            # Calculate scores
            accuracy = await self._calculate_accuracy(plan_subtasks, execution_results)
            quality = await self._calculate_quality(plan_data, execution_data)
            missing_items = await self._identify_missing_items(plan_subtasks, execution_results)

            # Generate notes
            notes = await self._generate_review_notes(review_details, accuracy, quality)

            # Calculate weighted final score
            final_score = (
                accuracy * self.scoring_weights["accuracy"] +
                quality * self.scoring_weights["quality"]
            )

            await self.update_task_progress(0.9, "Scoring complete")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Reviewer", f"Scoring: {accuracy:.1%} accuracy, {quality:.1%} quality", "review", "result")
                await publish_progress("review", 90.0, "Scoring complete")
                # Publish metrics
                await publish_metrics({
                    "accuracy": accuracy,
                    "quality": quality,
                    "final": final_score
                })

            review_result = {
                "accuracy": accuracy,
                "quality": quality,
                "final_score": final_score,
                "missing": missing_items,
                "notes": notes,
                "review_details": review_details,
                "plan_id": plan_id,
                "builder_id": execution_id or "context_provided",
                "timestamp": asyncio.get_event_loop().time()
            }

            await self.log(f"📊 Scores: {accuracy:.1%} accuracy, {quality:.1%} quality, {final_score:.1%} final", style="result")
            
            # Publish to UI
            if UI_ENABLED:
                await publish_chat("Reviewer", f"✓ Review complete! Final score: {final_score:.1%}", "review", "result")
                await publish_progress("review", 100.0, "Review complete")

            # Store the review in memory
            await self._store_review(review_result, plan_id, execution_id or "context_provided")

            # Create summary
            summary = await self._create_review_summary(review_result)

            await self.update_task_progress(1.0, "Review complete")

            # Return the full review_result dict (not just summary string) for coordinator
            review_result["summary_text"] = summary
            return review_result

        except Exception as e:
            await self.handle_error(e, "review process")
            raise

    async def review_execution(self, plan_id: str, builder_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Review BuilderAgent execution against PlannerAgent plan.

        Args:
            plan_id: The memory ID of the original plan
            builder_id: The memory ID of the execution results
            context: Context including execution data

        Returns:
            Structured review with scores and analysis

        Raises:
            Exception: If review fails due to missing data or errors
        """
        try:
            await self.log(f"🔍 Reviewing plan {plan_id[:8]} vs execution {builder_id[:8]}", style="action")

            # Retrieve the original plan using single item retrieval
            plan_item = self.memory.get(plan_id)
            if not plan_item:
                raise ValueError(f"Plan {plan_id} not found in memory")

            plan_data = plan_item.content
            if not isinstance(plan_data, dict):
                raise ValueError(f"Plan data is not structured (got {type(plan_data)})")

            await self.update_task_progress(0.3, "Retrieved plan")

            # Check if execution_data is provided directly in context (from CoordinatorAgent)
            execution_data = context.get("execution_data") if context else None
            if execution_data and isinstance(execution_data, dict):
                await self.log(f"🔍 Using execution data from context", style="info")
            elif builder_id:
                # Retrieve execution results as fallback
                await self.log(f"🔍 No execution data in context, retrieving from memory", style="thought")
                execution_item = self.memory.get(builder_id)
                if not execution_item:
                    raise ValueError(f"Execution {builder_id} not found in memory")

                execution_data = execution_item.content
                if not isinstance(execution_data, dict):
                    raise ValueError(f"Execution data is not structured (got {type(execution_data)})")
            else:
                raise ValueError("Either execution_data or builder_id required for review")

            await self.update_task_progress(0.5, "Retrieved execution")

            # Extract subtasks and results
            plan_subtasks = plan_data.get("subtasks", [])
            execution_results = execution_data.get("execution_results", [])

            if not plan_subtasks:
                raise ValueError("No subtasks found in plan")

            await self.update_task_progress(0.6, f"Analyzing {len(plan_subtasks)} subtasks")

            # Perform detailed analysis
            review_details = await self._analyze_execution(plan_subtasks, execution_results)

            # Calculate scores
            accuracy = await self._calculate_accuracy(plan_subtasks, execution_results)
            quality = await self._calculate_quality(plan_data, execution_data)
            missing_items = await self._identify_missing_items(plan_subtasks, execution_results)

            # Generate notes
            notes = await self._generate_review_notes(review_details, accuracy, quality)

            # Calculate weighted final score
            final_score = (
                accuracy * self.scoring_weights["accuracy"] +
                quality * self.scoring_weights["quality"]
            )

            await self.update_task_progress(0.9, "Scoring complete")

            review_result = {
                "accuracy": accuracy,
                "quality": quality,
                "final_score": final_score,
                "missing": missing_items,
                "notes": notes,
                "review_details": review_details,
                "plan_id": plan_id,
                "builder_id": builder_id,
                "timestamp": asyncio.get_event_loop().time()
            }

            await self.log(f"📊 Scores: {accuracy:.1%} accuracy, {quality:.1%} quality, {final_score:.1%} final", style="result")

            return review_result

        except Exception as e:
            await self.handle_error(e, "execution review")
            raise

    async def _analyze_execution(self, plan_subtasks: List[str], execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze execution results against planned subtasks.

        Args:
            plan_subtasks: List of planned subtask strings
            execution_results: List of execution result dictionaries

        Returns:
            Detailed analysis results
        """
        analysis = {
            "total_planned": len(plan_subtasks),
            "total_executed": len(execution_results),
            "completed_subtasks": [],
            "failed_subtasks": [],
            "similarity_scores": []
        }

        # Analyze each planned subtask
        for i, planned_subtask in enumerate(plan_subtasks):
            # Find corresponding execution result
            execution_result = None
            for result in execution_results:
                if result.get("index") == i:
                    execution_result = result
                    break

            if execution_result and execution_result.get("success", False):
                analysis["completed_subtasks"].append({
                    "index": i,
                    "planned": planned_subtask,
                    "executed": execution_result.get("result", ""),
                    "execution_time": execution_result.get("execution_time", 0)
                })
            else:
                analysis["failed_subtasks"].append({
                    "index": i,
                    "planned": planned_subtask,
                    "error": execution_result.get("error", "Not executed") if execution_result else "Missing"
                })

        # Calculate similarity scores for completed tasks
        for completed in analysis["completed_subtasks"]:
            similarity = await self._calculate_similarity(completed["planned"], completed["executed"])
            completed["similarity"] = similarity
            analysis["similarity_scores"].append(similarity)

        return analysis

    async def _calculate_accuracy(self, plan_subtasks: List[str], execution_results: List[Dict[str, Any]]) -> float:
        """
        Calculate accuracy as completion ratio.

        Args:
            plan_subtasks: List of planned subtasks
            execution_results: List of execution results

        Returns:
            Accuracy score between 0.0 and 1.0
        """
        if not plan_subtasks:
            return 0.0

        completed_count = sum(1 for result in execution_results if result.get("success", False))
        accuracy = completed_count / len(plan_subtasks)

        await self.log(f"📈 Accuracy: {completed_count}/{len(plan_subtasks)} = {accuracy:.1%}", style="thought")
        return accuracy

    async def _calculate_quality(self, plan_data: Dict[str, Any], execution_data: Dict[str, Any]) -> float:
        """
        Calculate quality score using cosine similarity.

        Args:
            plan_data: The original plan data
            execution_data: The execution results

        Returns:
            Quality score between 0.0 and 1.0
        """
        # Create text representations for similarity comparison
        plan_text = self._plan_to_text(plan_data)
        execution_text = self._execution_to_text(execution_data)

        # Calculate cosine similarity
        similarity = await self._calculate_similarity(plan_text, execution_text)

        await self.log(f"✨ Quality similarity: {similarity:.1%}", style="thought")
        return similarity

    async def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts using embeddings.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not text1 or not text2:
            return 0.0

        # Generate embeddings
        embed1 = await self.memory._embed(text1)
        embed2 = await self.memory._embed(text2)

        # Calculate cosine similarity
        dot_product = np.dot(embed1, embed2)
        norm1 = np.linalg.norm(embed1)
        norm2 = np.linalg.norm(embed2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return float(similarity)

    async def _identify_missing_items(self, plan_subtasks: List[str], execution_results: List[Dict[str, Any]]) -> List[str]:
        """
        Identify missing or incomplete subtasks.

        Args:
            plan_subtasks: List of planned subtasks
            execution_results: List of execution results

        Returns:
            List of missing items
        """
        missing = []

        # Check for missing execution results
        executed_indices = {result.get("index") for result in execution_results if result.get("success", False)}

        for i, subtask in enumerate(plan_subtasks):
            if i not in executed_indices:
                missing.append(f"Missing execution: {subtask}")

        # Check for failed executions
        for result in execution_results:
            if not result.get("success", False):
                missing.append(f"Failed: {result.get('subtask', 'Unknown')} - {result.get('error', 'No error details')}")

        return missing

    async def _generate_review_notes(self, analysis: Dict[str, Any], accuracy: float, quality: float) -> str:
        """
        Generate human-readable review notes.

        Args:
            analysis: Detailed analysis results
            accuracy: Calculated accuracy score
            quality: Calculated quality score

        Returns:
            Formatted notes string
        """
        notes = []

        # Overall assessment
        if accuracy >= 0.9 and quality >= 0.8:
            notes.append("Excellent execution with high fidelity to plan.")
        elif accuracy >= 0.7 and quality >= 0.6:
            notes.append("Good execution with reasonable alignment to plan.")
        elif accuracy >= 0.5:
            notes.append("Partial execution completed, some gaps identified.")
        else:
            notes.append("Significant issues found in execution.")

        # Specific observations
        completed = analysis.get("completed_subtasks", [])
        failed = analysis.get("failed_subtasks", [])

        if completed:
            avg_time = sum(c.get("execution_time", 0) for c in completed) / len(completed)
            notes.append(f"Successfully completed {len(completed)} subtasks (avg: {avg_time:.1f}s each).")

        if failed:
            notes.append(f"Failed or missing {len(failed)} subtasks.")

        # Similarity analysis
        similarities = analysis.get("similarity_scores", [])
        if similarities:
            avg_similarity = sum(similarities) / len(similarities)
            if avg_similarity > 0.8:
                notes.append("High similarity between planned and executed content.")
            elif avg_similarity > 0.6:
                notes.append("Good alignment between plan and execution.")
            else:
                notes.append("Some divergence between planned and actual execution.")

        return " ".join(notes)

    def _plan_to_text(self, plan_data: Dict[str, Any]) -> str:
        """
        Convert plan data to text for similarity comparison.

        Args:
            plan_data: The plan dictionary

        Returns:
            Text representation of the plan
        """
        parts = []

        # Add main task
        if "original_task" in plan_data:
            parts.append(f"Task: {plan_data['original_task']}")

        # Add task type
        if "task_type" in plan_data:
            parts.append(f"Type: {plan_data['task_type']}")

        # Add subtasks
        subtasks = plan_data.get("subtasks", [])
        if subtasks:
            parts.append(f"Subtasks: {'; '.join(subtasks)}")

        # Add context
        context = plan_data.get("context", {})
        if context:
            parts.append(f"Context: {context}")

        return " | ".join(parts)

    def _execution_to_text(self, execution_data: Dict[str, Any]) -> str:
        """
        Convert execution data to text for similarity comparison.

        Args:
            execution_data: The execution results dictionary

        Returns:
            Text representation of the execution
        """
        parts = []

        # Add execution mode and metadata
        execution_mode = execution_data.get("execution_mode", "unknown")
        parts.append(f"Execution mode: {execution_mode}")

        # Add results summary
        execution_results = execution_data.get("execution_results", [])
        successful = sum(1 for r in execution_results if r.get("success", False))
        total = len(execution_results)
        parts.append(f"Results: {successful}/{total} successful")

        # Add individual subtask details
        subtask_details = []
        for result in execution_results:
            if result.get("success", False):
                subtask_text = result.get("subtask", "")
                if result.get("result"):
                    # Extract meaningful text from result (handle both string and structured)
                    result_content = result["result"]
                    if isinstance(result_content, str):
                        # Take first line or first 100 chars of generated content
                        meaningful = result_content.split('\n')[0] if '\n' in result_content else result_content
                        subtask_details.append(f"✅ {subtask_text[:30]}... → {meaningful[:50]}...")
                    else:
                        subtask_details.append(f"✅ {subtask_text[:30]}... → [Structured result]")

        if subtask_details:
            parts.append(f"Details: {'; '.join(subtask_details[:3])}")  # Limit to first 3

        return " | ".join(parts)

    async def _create_review_summary(self, review_result: Dict[str, Any]) -> str:
        """
        Create a formatted summary of review results.

        Args:
            review_result: The structured review result

        Returns:
            Formatted summary string
        """
        summary = f"""
📊 **Execution Review Summary**

**Plan ID:** {review_result['plan_id'][:8]}
**Builder ID:** {review_result['builder_id'][:8]}

**Overall Assessment:**
- Accuracy: {review_result['accuracy']:.1%}
- Quality: {review_result['quality']:.1%}
- Final Score: {review_result['final_score']:.1%}

**Analysis Details:**
- Total Planned: {review_result['review_details']['total_planned']}
- Total Executed: {review_result['review_details']['total_executed']}
- Completed: {len(review_result['review_details']['completed_subtasks'])}
- Failed: {len(review_result['review_details']['failed_subtasks'])}

**Issues Found:**
"""
        for missing in review_result['missing'][:5]:  # Show first 5 issues
            summary += f"• {missing}\n"

        if len(review_result['missing']) > 5:
            summary += f"... and {len(review_result['missing']) - 5} more issues\n"

        summary += f"\n**Notes:** {review_result['notes']}\n"
        summary += f"\n✅ Review complete. Quality metrics calculated and stored."

        return summary.strip()

    async def _store_review(self, review_result: Dict[str, Any], plan_id: str, builder_id: str) -> None:
        """
        Store the review results in memory.

        Args:
            review_result: The structured review result
            plan_id: The original plan ID
            builder_id: The execution ID
        """
        await self.memory.store(
            content=review_result,
            memory_type=MemoryType.EPISODIC,
            metadata={
                "agent": self.name,
                "review_type": "execution_review",
                "plan_id": plan_id,
                "builder_id": builder_id,
                "accuracy": review_result["accuracy"],
                "quality": review_result["quality"],
                "final_score": review_result["final_score"]
            },
            tags={"review", "evaluation", "quality_assessment"}
        )

        await self.log(f"💾 Review stored in memory", style="info")

    async def get_review_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent review history from memory.

        Args:
            limit: Maximum number of reviews to retrieve

        Returns:
            List of recent review results
        """
        # Search by metadata since reviews are stored with specific metadata
        query = MemoryQuery(
            memory_type=MemoryType.EPISODIC,
            limit=limit * 2  # Get more to filter
        )

        results = await self.memory.retrieve(query)

        # Filter to only reviews from this agent
        filtered_results = []
        for item in results:
            if (item.metadata.get("agent") == self.name and
                item.metadata.get("review_type") == "execution_review"):
                filtered_results.append(item)

        # Sort by timestamp (newest first)
        filtered_results.sort(key=lambda x: x.created_at, reverse=True)

        return [
            {
                "id": item.id,
                "content": item.content,
                "metadata": item.metadata,
                "created_at": item.created_at.isoformat()
            }
            for item in filtered_results[:limit]
        ]
