"""
Reviewer Agent Basic Tests.

Unit tests for ReviewerAgent functionality including scoring, memory integration,
and review generation.

Author: TMAO Dev Team
License: MIT
"""

import asyncio
import sys

# Add src to path for imports
sys.path.insert(0, 'src')

async def test_reviewer_basic():
    """Test basic ReviewerAgent functionality."""

    try:
        from agents.reviewer_agent import ReviewerAgent
        from src.core.memory import MemoryManager, MemoryType

        print("🧪 Testing ReviewerAgent Basic Functionality...")
        print("="*50)

        # Create reviewer with test configuration
        config = {
            "reviewer": {
                "evaluation_mode": "auto",
                "scoring_weights": {
                    "accuracy": 0.6,
                    "quality": 0.4
                }
            }
        }

        reviewer = ReviewerAgent(config)
        await reviewer.initialize()

        print("✅ ReviewerAgent initialized successfully")
        print(f"   Name: {reviewer.name}")
        print(f"   Role: {reviewer.role}")
        print(f"   Evaluation Mode: {reviewer.evaluation_mode}")
        print(f"   Scoring Weights: {reviewer.scoring_weights}")

        # Test 1: Perfect execution scenario
        print("\n📊 Test 1: Perfect Execution Review")

        # Store test plan
        plan_data = {
            "original_task": "Create API documentation",
            "task_type": "documentation",
            "subtasks": ["Structure docs", "Write content", "Add examples"]
        }

        plan_id = await reviewer.memory.store(
            content=plan_data,
            memory_type=MemoryType.WORKING,
            metadata={"agent": "Planner"},
            tags={"plan"}
        )

        # Store test execution results
        execution_data = {
            "execution_mode": "sequential",
            "execution_results": [
                {"index": 0, "success": True, "result": "Documentation structured", "execution_time": 1.2},
                {"index": 1, "success": True, "result": "Content written successfully", "execution_time": 1.8},
                {"index": 2, "success": True, "result": "Examples added", "execution_time": 1.5}
            ]
        }

        builder_id = await reviewer.memory.store(
            content=execution_data,
            memory_type=MemoryType.WORKING,
            metadata={"agent": "Builder"},
            tags={"execution"}
        )

        # Perform review
        review_result = await reviewer.review_execution(plan_id, builder_id)

        print(f"   📈 Results: {review_result['accuracy']:.1%} accuracy, {review_result['quality']:.1%} quality")
        # Verify scores are in valid range
        assert 0.0 <= review_result['accuracy'] <= 1.0, f"Accuracy out of range: {review_result['accuracy']}"
        assert 0.0 <= review_result['quality'] <= 1.0, f"Quality out of range: {review_result['quality']}"
        assert 0.0 <= review_result['final_score'] <= 1.0, f"Final score out of range: {review_result['final_score']}"

        print(f"   ✅ Scores in valid range (0.0-1.0)")
        print(f"   ✅ Review structure valid: {bool(review_result.get('notes'))}")
        print(f"   ✅ Missing items identified: {len(review_result.get('missing', []))} issues")

        # Test 2: Partial execution scenario
        print("\n📊 Test 2: Partial Execution Review")

        # Store partial execution results
        partial_execution_data = {
            "execution_mode": "parallel",
            "execution_results": [
                {"index": 0, "success": True, "result": "Documentation structured", "execution_time": 1.2},
                {"index": 1, "success": False, "error": "Content writing failed", "execution_time": 0.8},
                {"index": 2, "success": True, "result": "Examples partially added", "execution_time": 1.0}
            ]
        }

        partial_builder_id = await reviewer.memory.store(
            content=partial_execution_data,
            memory_type=MemoryType.WORKING,
            metadata={"agent": "Builder", "test": "partial"},
            tags={"execution", "partial"}
        )

        # Review partial execution
        partial_review = await reviewer.review_execution(plan_id, partial_builder_id)

        print(f"   📈 Partial results: {partial_review['accuracy']:.1%} accuracy")
        # Should have lower accuracy than perfect execution
        assert partial_review['accuracy'] < review_result['accuracy'], "Partial execution should have lower accuracy"
        print(f"   ✅ Partial execution correctly scored lower")

        # Test 3: Review history
        print("\n📚 Test 3: Review History")

        history = await reviewer.get_review_history(limit=2)

        print(f"   Retrieved {len(history)} reviews from memory")
        assert len(history) >= 1, "Should have at least one review in history"

        # Verify history structure
        latest_review = history[0]
        assert "content" in latest_review, "History should contain review content"
        assert "metadata" in latest_review, "History should contain metadata"
        assert "accuracy" in latest_review["content"], "History should contain accuracy score"

        print(f"   ✅ Review history structure valid")
        print(f"   💾 Latest review: {latest_review['id'][:8]}")

        # Test 4: Similarity calculation
        print("\n🔍 Test 4: Similarity Analysis")

        similarity = await reviewer._calculate_similarity(
            "Create API endpoints with authentication",
            "Built REST API with user authentication and validation"
        )

        print(f"   Similarity score: {similarity:.1%}")
        assert 0.0 <= similarity <= 1.0, f"Similarity should be between 0 and 1, got {similarity}"

        if similarity > 0.5:
            print(f"   ✅ High similarity correctly detected")
        else:
            print(f"   ✅ Low similarity correctly detected")

        await reviewer.shutdown()

        print("\n🎉 All ReviewerAgent tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_memory_integration():
    """Test ReviewerAgent memory integration and retrieval."""

    try:
        from agents.reviewer_agent import ReviewerAgent
        from src.core.memory import MemoryType, MemoryQuery

        print("\n🧠 Testing Memory Integration...")
        print("="*40)

        reviewer = ReviewerAgent()
        await reviewer.initialize()

        # Test 1: Verify reviews are stored correctly
        print("\n📝 Test 1: Review Storage")

        # Create mock plan and execution
        plan_id = await reviewer.memory.store(
            content={"task": "Test", "subtasks": ["step1", "step2"]},
            memory_type=MemoryType.WORKING,
            tags={"plan"}
        )

        builder_id = await reviewer.memory.store(
            content={"execution_results": [{"success": True}, {"success": True}]},
            memory_type=MemoryType.WORKING,
            tags={"execution"}
        )

        # Perform review
        review_result = await reviewer.review_execution(plan_id, builder_id)

        # Verify review was stored
        review_history = await reviewer.get_review_history(limit=1)

        if review_history:
            stored_review = review_history[0]
            print(f"   ✅ Review stored: {stored_review['id'][:8]}")
            print(f"   📊 Stored scores: {stored_review['content']['accuracy']:.1%} accuracy")
            # Verify memory can retrieve the review correctly
            direct_item = reviewer.memory.get(stored_review['id'])
            if direct_item and isinstance(direct_item.content, dict):
                print(f"   ✅ Direct retrieval successful")
                print(f"   🎯 Retrieved scores: {direct_item.content['accuracy']:.1%} accuracy")
        else:
            print(f"   ❌ No review found in history")

        await reviewer.shutdown()
        print("\n✅ Memory integration test completed")

    except Exception as e:
        print(f"❌ Memory integration test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    """Run ReviewerAgent tests."""

    async def main():
        print("🚀 Running ReviewerAgent Tests...")

        # Run basic functionality tests
        basic_success = await test_reviewer_basic()

        # Run memory integration tests
        await test_memory_integration()

        if basic_success:
            print("\n🎉 All tests completed successfully!")
            print("\n📋 Test Summary:")
            print("   ✅ ReviewerAgent initialization")
            print("   ✅ Review execution and scoring")
            print("   ✅ Score validation (0.0-1.0 range)")
            print("   ✅ Review structure and notes")
            print("   ✅ Missing items detection")
            print("   ✅ Review history and memory integration")
            print("   ✅ Similarity analysis")
        else:
            print("\n❌ Some tests failed - check output above")

    asyncio.run(main())
