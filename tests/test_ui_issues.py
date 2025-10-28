#!/usr/bin/env python3
"""Test UI issues with complex task breakdown."""

import asyncio
from pathlib import Path
from qaw.manager import ManagerSession


async def test_complex_task_breakdown():
    """Test that complex tasks are properly broken down."""
    workspace_dir = Path.cwd()
    session = ManagerSession(workspace_dir)

    # Test the exact scenario mentioned by user
    test_cases = [
        "Create a React frontend with Amplify backend authentication",
        "Build a React app with user authentication using AWS Amplify",
        "Add React frontend auth with Amplify backend",
    ]

    for task in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {task}")
        print("=" * 60)

        # Send the task
        response = await session.send_message(task)

        # Check the plan
        if session.current_plan:
            plan = session.current_plan
            num_increments = len(plan.increments)

            print(f"\nPlan created with {num_increments} increments:")

            # Count by type
            backend_count = sum(
                1 for inc in plan.increments if inc.agent_type == "backend"
            )
            frontend_count = sum(
                1 for inc in plan.increments if inc.agent_type == "frontend"
            )
            test_count = sum(1 for inc in plan.increments if inc.agent_type == "test")

            print(f"  Backend: {backend_count}")
            print(f"  Frontend: {frontend_count}")
            print(f"  Testing: {test_count}")

            # Show each increment
            for i, inc in enumerate(plan.increments, 1):
                print(f"\n  {i}. {inc.description}")
                print(f"     Agent: {inc.agent_type}, Lines: {inc.estimated_lines}")
                if inc.dependencies:
                    print(f"     Dependencies: {inc.dependencies}")

            # Check if properly broken down
            if num_increments == 1:
                print("\n❌ ISSUE: Complex task only shows 1 iteration!")
            elif num_increments < 3:
                print(f"\n⚠️  WARNING: Complex task only has {num_increments} steps")
            else:
                print(f"\n✅ Good: Task broken into {num_increments} increments")

            print(f"\nManager Response Preview:")
            print("-" * 40)
            print(response[:500] + "..." if len(response) > 500 else response)
        else:
            print("❌ ERROR: No plan created!")


if __name__ == "__main__":
    asyncio.run(test_complex_task_breakdown())
