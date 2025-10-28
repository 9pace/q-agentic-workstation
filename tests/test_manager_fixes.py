#!/usr/bin/env python3
"""
Test script to validate Manager Agent fixes for task breakdown.
Tests complex tasks like React/Amplify authentication.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from qaw.manager import ManagerAgent, ManagerSession, ExecutionPlan, Increment
from qaw.context import ContextManager, ProjectContext, TechStack, ProjectPatterns


async def test_complex_task_breakdown():
    """Test that complex tasks are properly broken down into multiple increments."""

    print("=" * 60)
    print("Testing Complex Task Breakdown")
    print("=" * 60)

    # Create a mock workspace
    workspace_dir = Path("/tmp/test_workspace")
    workspace_dir.mkdir(exist_ok=True)

    # Create manager
    manager = ManagerAgent(workspace_dir)

    # Test cases for complex tasks
    test_cases = [
        {
            "task": "Create a React frontend with authentication using Amplify backend",
            "expected_min_increments": 5,
            "should_contain": ["amplify", "react", "auth", "frontend", "backend"],
        },
        {
            "task": "Add user authentication with JWT tokens, login and signup forms, and protected routes",
            "expected_min_increments": 4,
            "should_contain": ["jwt", "login", "signup", "routes"],
        },
        {
            "task": "Build a full-stack user management system with CRUD operations",
            "expected_min_increments": 3,
            "should_contain": ["crud", "backend", "frontend"],
        },
        {
            "task": "Add a simple button to the homepage",
            "expected_min_increments": 1,
            "should_contain": ["button"],
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['task'][:50]}...")

        # Process the request
        plan = await manager.process_request(test_case["task"])

        print(f"  Generated {len(plan.increments)} increments:")
        for inc in plan.increments:
            print(f"    - {inc.description[:60]}...")
            print(f"      Agent: {inc.agent_type}, Lines: ~{inc.estimated_lines}")
            if inc.dependencies:
                print(f"      Dependencies: {inc.dependencies}")

        # Validate
        assert (
            len(plan.increments) >= test_case["expected_min_increments"]
        ), f"Expected at least {test_case['expected_min_increments']} increments, got {len(plan.increments)}"

        # Check that relevant keywords are addressed
        all_descriptions = " ".join(
            [inc.description.lower() for inc in plan.increments]
        )
        for keyword in test_case["should_contain"]:
            if keyword not in test_case["task"].lower():
                continue  # Skip keywords not in original task
            # Check if keyword appears in the breakdown
            keyword_found = any(
                keyword in inc.description.lower() for inc in plan.increments
            )
            if not keyword_found:
                print(
                    f"  ⚠️  Warning: Keyword '{keyword}' not found in increment descriptions"
                )

        print(f"  ✅ Test passed!")

    print("\n" + "=" * 60)
    print("All Complex Task Breakdown Tests Passed!")
    print("=" * 60)


async def test_manager_session_responses():
    """Test that ManagerSession properly formats responses."""

    print("\n" + "=" * 60)
    print("Testing Manager Session Response Formatting")
    print("=" * 60)

    workspace_dir = Path("/tmp/test_workspace")
    workspace_dir.mkdir(exist_ok=True)

    session = ManagerSession(workspace_dir)

    # Test task request
    print("\nTest 1: Complex task request")
    response = await session.send_message(
        "Create a React frontend with authentication using Amplify backend"
    )

    print(f"Response preview:\n{response[:500]}...")

    # Validate response format
    assert "increment" in response.lower(), "Response should mention increments"
    assert session.current_plan is not None, "Should have created a plan"
    assert len(session.current_plan.increments) > 1, "Should have multiple increments"

    # Check that response shows all increments
    for i, inc in enumerate(session.current_plan.increments, 1):
        assert f"{i}." in response, f"Response should show increment {i}"

    print("✅ Response properly formatted with all increments")

    # Test conversation (non-task)
    print("\nTest 2: Conversational message")
    response = await session.send_message("Hello")
    assert "Manager Agent" in response, "Should introduce itself"
    print("✅ Conversational response working")

    # Test status check
    print("\nTest 3: Status check")
    response = await session.send_message("What's the status?")
    assert (
        "Current plan" in response or "increments" in response.lower()
    ), "Should show plan status"
    print("✅ Status check working")

    print("\n" + "=" * 60)
    print("All Manager Session Tests Passed!")
    print("=" * 60)


async def test_increment_details():
    """Test that increments have proper details and dependencies."""

    print("\n" + "=" * 60)
    print("Testing Increment Details and Dependencies")
    print("=" * 60)

    workspace_dir = Path("/tmp/test_workspace")
    workspace_dir.mkdir(exist_ok=True)

    manager = ManagerAgent(workspace_dir)

    # Test React/Amplify auth task
    task = "Create a React frontend with authentication using Amplify backend"
    plan = await manager.process_request(task)

    print(f"\nTask: {task}")
    print(f"Generated {len(plan.increments)} increments:\n")

    # Validate each increment
    for inc in plan.increments:
        print(f"Increment {inc.id}:")
        print(f"  Description: {inc.description}")
        print(f"  Agent Type: {inc.agent_type}")
        print(f"  Est. Lines: {inc.estimated_lines}")
        print(f"  Dependencies: {inc.dependencies}")

        # Validate increment properties
        assert inc.id, "Increment should have an ID"
        assert inc.description, "Increment should have a description"
        assert inc.agent_type in [
            "backend",
            "frontend",
            "test",
            "orchestrator",
        ], f"Invalid agent type: {inc.agent_type}"
        assert (
            0 < inc.estimated_lines <= 50
        ), f"Lines should be between 1-50, got {inc.estimated_lines}"

        # Check dependencies are valid
        for dep in inc.dependencies:
            assert any(
                i.id == dep for i in plan.increments
            ), f"Dependency {dep} not found in plan"

        print("  ✅ Valid increment")

    # Check logical flow
    backend_incs = [i for i in plan.increments if i.agent_type == "backend"]
    frontend_incs = [i for i in plan.increments if i.agent_type == "frontend"]
    test_incs = [i for i in plan.increments if i.agent_type == "test"]

    print(f"\nBreakdown Summary:")
    print(f"  Backend increments: {len(backend_incs)}")
    print(f"  Frontend increments: {len(frontend_incs)}")
    print(f"  Test increments: {len(test_incs)}")

    # For auth tasks, we should have both backend and frontend
    if "auth" in task.lower():
        assert len(backend_incs) > 0, "Auth task should have backend increments"
        assert len(frontend_incs) > 0, "Auth task should have frontend increments"
        print("  ✅ Proper backend/frontend split for auth task")

    print("\n" + "=" * 60)
    print("All Increment Detail Tests Passed!")
    print("=" * 60)


async def test_task_simplification():
    """Test that tasks are properly simplified in summaries."""

    print("\n" + "=" * 60)
    print("Testing Task Simplification in Summaries")
    print("=" * 60)

    workspace_dir = Path("/tmp/test_workspace")
    workspace_dir.mkdir(exist_ok=True)

    session = ManagerSession(workspace_dir)

    # Complex task
    task = "Create a React frontend with authentication using Amplify backend including user registration, login, logout, password reset, and protected routes with role-based access control"

    print(f"Original task ({len(task)} chars):")
    print(f"  {task}\n")

    response = await session.send_message(task)
    plan = session.current_plan

    # Check that plan summary is simplified
    assert plan is not None, "Should have created a plan"

    print(f"Plan Summary:")
    print(f"  User Request: {plan.user_request[:100]}...")
    print(f"  Total Increments: {len(plan.increments)}")
    print(f"  Total Est. Lines: {plan.total_estimated_lines}")

    # Check increment descriptions are concise
    print(f"\nIncrement Descriptions:")
    for i, inc in enumerate(plan.increments, 1):
        print(f"  {i}. {inc.description}")
        assert (
            len(inc.description) < 100
        ), f"Increment description too long: {len(inc.description)} chars"

    # Get status summary
    summary = session.get_status_summary()
    print(f"\nStatus Summary:\n{summary}")

    assert len(summary) < len(task) * 3, "Summary should be concise"
    print("\n✅ Task properly simplified in summaries")

    print("\n" + "=" * 60)
    print("All Task Simplification Tests Passed!")
    print("=" * 60)


async def main():
    """Run all tests."""

    print("\n" + "=" * 60)
    print("MANAGER AGENT FIX VALIDATION")
    print("=" * 60)

    try:
        # Run all test suites
        await test_complex_task_breakdown()
        await test_manager_session_responses()
        await test_increment_details()
        await test_task_simplification()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)

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
