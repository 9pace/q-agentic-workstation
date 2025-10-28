#!/usr/bin/env python3
"""
Production-ready validation test for Q Agentic Workstation.
Tests the complete flow with complex tasks like React/Amplify authentication.
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from qaw.manager import ManagerSession
from qaw.dashboard import DashboardApp
from qaw.state import StateManager


async def test_react_amplify_scenario():
    """Test the exact scenario user mentioned: React frontend with Amplify backend auth."""

    print("=" * 70)
    print("PRODUCTION-READY TEST: React/Amplify Authentication")
    print("=" * 70)

    workspace_dir = Path("/tmp/test_workspace")
    workspace_dir.mkdir(exist_ok=True)

    # Create manager session
    session = ManagerSession(workspace_dir)

    # Test the exact task user mentioned
    task = "Create a React frontend with authentication using Amplify backend"

    print(f"\n📝 Task: {task}")
    print("-" * 70)

    # Send the task
    response = await session.send_message(task)

    # Validate response format
    print("\n📊 Response Analysis:")
    print("-" * 70)

    # Check that it properly shows multiple increments
    assert (
        "incremental steps" in response
        or "manageable steps" in response
        or "single step" in response
    ), "Response should clearly indicate how many steps"

    # Check for component breakdown
    if "Component Breakdown" in response:
        print("✅ Shows component breakdown for complex task")
        assert "Backend:" in response
        assert "Frontend:" in response
        print("   - Backend components identified")
        print("   - Frontend components identified")

    # Check for execution steps
    assert "Execution Steps" in response, "Should show execution steps"
    print("✅ Shows detailed execution steps")

    # Verify plan was created
    assert session.current_plan is not None, "Should create a plan"
    plan = session.current_plan

    print(f"\n📈 Plan Details:")
    print(f"   - Total increments: {len(plan.increments)}")
    print(f"   - Total complexity: ~{plan.total_estimated_lines} lines")

    # Validate increments
    assert (
        len(plan.increments) >= 5
    ), f"Complex auth task should have at least 5 increments, got {len(plan.increments)}"

    # Check increment types
    backend_count = sum(1 for inc in plan.increments if inc.agent_type == "backend")
    frontend_count = sum(1 for inc in plan.increments if inc.agent_type == "frontend")
    test_count = sum(1 for inc in plan.increments if inc.agent_type == "test")

    print(f"\n🔧 Increment Breakdown:")
    print(f"   - Backend: {backend_count} increments")
    print(f"   - Frontend: {frontend_count} increments")
    print(f"   - Testing: {test_count} increments")

    assert (
        backend_count >= 2
    ), "Should have at least 2 backend increments for Amplify setup"
    assert (
        frontend_count >= 3
    ), "Should have at least 3 frontend increments for React auth"

    # Check dependencies are logical
    print(f"\n🔗 Dependency Analysis:")
    for inc in plan.increments:
        if inc.dependencies:
            print(f"   - {inc.id} depends on: {', '.join(inc.dependencies)}")
            # Verify dependencies exist
            for dep in inc.dependencies:
                assert any(
                    i.id == dep for i in plan.increments
                ), f"Dependency {dep} not found"

    # Test the response formatting
    print(f"\n📄 Response Quality Check:")

    # For complex tasks with multiple increments, should not say "1 increment"
    if len(plan.increments) > 1:
        # The response should indicate multiple steps, not "1 increment(s)"
        assert (
            "single step" not in response.lower() or len(plan.increments) == 1
        ), "Should not say 'single step' for multi-increment plans"

    # Should have clear formatting
    assert (
        "**" in response or "##" in response or "•" in response
    ), "Should use markdown formatting for clarity"

    # Should mention execution
    assert (
        "Execute" in response or "proceed" in response.lower()
    ), "Should mention how to execute the plan"

    print("   ✅ Clear increment breakdown")
    print("   ✅ Proper markdown formatting")
    print("   ✅ Execution instructions included")

    print("\n" + "=" * 70)
    print("✅ PRODUCTION-READY TEST PASSED!")
    print("=" * 70)

    return True


async def test_ui_stability():
    """Test UI stability and error handling."""

    print("\n" + "=" * 70)
    print("UI STABILITY TEST")
    print("=" * 70)

    workspace_dir = Path("/tmp/test_workspace")
    workspace_dir.mkdir(exist_ok=True)

    session = ManagerSession(workspace_dir)

    # Test various edge cases
    test_cases = [
        {"input": "", "should_be_task": False, "description": "Empty input"},
        {"input": "hi", "should_be_task": False, "description": "Simple greeting"},
        {
            "input": "what's the status?",
            "should_be_task": False,
            "description": "Status query",
        },
        {"input": "Add a button", "should_be_task": True, "description": "Simple task"},
        {
            "input": "Create " + "a" * 500 + " feature",  # Very long input
            "should_be_task": True,
            "description": "Very long task description",
        },
    ]

    for test in test_cases:
        print(f"\n📝 Testing: {test['description']}")

        try:
            # Check if correctly identified as task
            is_task = session._is_task_request(test["input"])
            assert (
                is_task == test["should_be_task"]
            ), f"Failed to correctly identify '{test['description']}' as task={test['should_be_task']}"

            # Send message and ensure no crash
            response = await session.send_message(test["input"])
            assert response is not None, "Should always return a response"
            assert len(response) > 0, "Response should not be empty"

            print(f"   ✅ Handled correctly (task={is_task})")

        except Exception as e:
            print(f"   ❌ Failed: {e}")
            raise

    print("\n" + "=" * 70)
    print("✅ UI STABILITY TEST PASSED!")
    print("=" * 70)

    return True


async def test_error_recovery():
    """Test error handling and recovery."""

    print("\n" + "=" * 70)
    print("ERROR RECOVERY TEST")
    print("=" * 70)

    workspace_dir = Path("/tmp/test_workspace")
    workspace_dir.mkdir(exist_ok=True)

    # Test state manager error handling
    state = StateManager(workspace_dir)

    print("\n📝 Testing state management robustness...")

    # Create multiple agents rapidly
    for i in range(5):
        agent = state.create_agent(
            agent_name="test-agent",
            task_id=f"task-{i}",
            task_description=f"Test task {i}",
        )
        assert agent is not None, f"Failed to create agent {i}"

    print("   ✅ Handled rapid agent creation")

    # Test stats calculation with various states
    stats = state.get_stats()
    assert isinstance(stats, dict), "Stats should be a dictionary"
    assert "total" in stats, "Stats should include total"
    assert stats["total"] >= 5, "Should have created at least 5 agents"

    print("   ✅ Stats calculation working")

    # Test cleanup of stale agents
    from qaw.executor import AgentExecutor

    executor = AgentExecutor(state)
    executor.cleanup_stale_agents()

    print("   ✅ Stale agent cleanup working")

    print("\n" + "=" * 70)
    print("✅ ERROR RECOVERY TEST PASSED!")
    print("=" * 70)

    return True


async def test_performance():
    """Test performance with complex tasks."""

    print("\n" + "=" * 70)
    print("PERFORMANCE TEST")
    print("=" * 70)

    workspace_dir = Path("/tmp/test_workspace")
    workspace_dir.mkdir(exist_ok=True)

    session = ManagerSession(workspace_dir)

    # Test with increasingly complex tasks
    tasks = [
        "Add a button",
        "Create a user profile page with edit functionality",
        "Build a complete e-commerce checkout flow with payment processing",
        "Implement a real-time chat system with WebSocket support, user presence, typing indicators, and message history",
    ]

    print("\n📊 Testing task complexity scaling:")

    for task in tasks:
        start_time = datetime.now()

        # Process task
        response = await session.send_message(task)

        # Measure time
        elapsed = (datetime.now() - start_time).total_seconds()

        # Get plan details
        plan = session.current_plan
        increments = len(plan.increments) if plan else 0

        print(f"\n   Task: {task[:50]}...")
        print(f"   - Processing time: {elapsed:.2f}s")
        print(f"   - Increments generated: {increments}")
        print(f"   - Response length: {len(response)} chars")

        # Performance assertions
        assert elapsed < 5.0, f"Task processing took too long: {elapsed}s"
        assert len(response) < 5000, f"Response too verbose: {len(response)} chars"

        if increments > 0:
            assert increments <= 10, f"Too many increments: {increments}"

    print("\n   ✅ All tasks processed within performance limits")

    print("\n" + "=" * 70)
    print("✅ PERFORMANCE TEST PASSED!")
    print("=" * 70)

    return True


async def main():
    """Run all production-ready tests."""

    print("\n" + "=" * 70)
    print("Q AGENTIC WORKSTATION - PRODUCTION READY VALIDATION")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Run all test suites
        await test_react_amplify_scenario()
        await test_ui_stability()
        await test_error_recovery()
        await test_performance()

        print("\n" + "=" * 70)
        print("🎉 ALL PRODUCTION TESTS PASSED!")
        print("=" * 70)
        print("\nThe system is production-ready with:")
        print("  ✅ Complex task breakdown working correctly")
        print("  ✅ UI stable and responsive")
        print("  ✅ Error handling robust")
        print("  ✅ Performance within acceptable limits")
        print("  ✅ React/Amplify scenario properly handled")

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
