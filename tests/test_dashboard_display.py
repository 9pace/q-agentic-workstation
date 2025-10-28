#!/usr/bin/env python3
"""Test dashboard display issues."""

import asyncio
from pathlib import Path
from qaw.manager import ManagerSession
from qaw.dashboard import ExecutionPlanPanel
from rich.console import Console


async def test_dashboard_display():
    """Test how the dashboard displays complex tasks."""
    workspace_dir = Path.cwd()
    session = ManagerSession(workspace_dir)
    console = Console()

    # Test the exact scenario
    task = "Create a React frontend with Amplify backend authentication"

    print(f"\nTesting task: {task}")
    print("=" * 60)

    # Send the task
    response = await session.send_message(task)

    if session.current_plan:
        plan = session.current_plan

        # Create a panel to test rendering
        panel = ExecutionPlanPanel()
        panel.plan = plan

        # Get the rendered output
        rendered = panel.render()

        print("\nDashboard Panel Output:")
        print("-" * 40)
        console.print(rendered)

        # Check for issues
        print("\n" + "=" * 60)
        print("Analysis:")
        print("-" * 40)

        # Check if it shows proper breakdown
        if "1 iteration" in rendered.lower() or "1 step" in rendered.lower():
            print("❌ ISSUE: Dashboard shows '1 iteration' for complex task!")
        elif "6" in rendered:
            print("✅ Good: Dashboard correctly shows 6 steps")
        else:
            print("⚠️  WARNING: Can't determine step count in display")

        # Check for component breakdown
        if "Backend:" in rendered and "Frontend:" in rendered:
            print("✅ Good: Component breakdown is shown")
        else:
            print("❌ ISSUE: Component breakdown not displayed")

        # Check task simplification
        if len(plan.user_request) > 60:
            if "..." in rendered:
                print("✅ Good: Long task is truncated in display")
            else:
                print("⚠️  WARNING: Long task might not be truncated")

    else:
        print("❌ ERROR: No plan created!")


if __name__ == "__main__":
    asyncio.run(test_dashboard_display())
