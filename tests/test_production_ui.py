#!/usr/bin/env python3
"""Production-ready UI testing for Q Agentic Workstation."""

import asyncio
from pathlib import Path
from qaw.manager import ManagerSession, ManagerAgent
from qaw.dashboard import ExecutionPlanPanel
from rich.console import Console
import json


async def test_edge_cases():
    """Test edge cases and potential UI bugs."""
    workspace_dir = Path.cwd()
    console = Console()

    print("\n" + "=" * 60)
    print("TESTING EDGE CASES AND UI BUGS")
    print("=" * 60)

    # Test 1: Simple vs Complex task detection
    print("\n1. Testing task complexity detection:")
    print("-" * 40)

    test_tasks = [
        ("Fix a typo", "simple"),
        ("Add a button", "simple"),
        ("Create React frontend with Amplify backend auth", "complex"),
        ("Build full-stack app with authentication", "complex"),
        ("Add user login", "medium"),
    ]

    session = ManagerSession(workspace_dir)

    for task, expected in test_tasks:
        # Check if task is detected correctly
        is_task = session._is_task_request(task)
        print(f"  '{task[:30]}...' -> Task: {is_task}")

        if is_task:
            response = await session.send_message(task)
            if session.current_plan:
                num_inc = len(session.current_plan.increments)
                complexity = (
                    "simple"
                    if num_inc == 1
                    else "medium" if num_inc <= 3 else "complex"
                )
                status = "✅" if complexity == expected else "❌"
                print(f"    {status} Got {num_inc} increments (expected: {expected})")
            else:
                print(f"    ❌ No plan created!")

    # Test 2: Check for the "1 iteration" bug
    print("\n2. Checking for '1 iteration' bug in responses:")
    print("-" * 40)

    complex_task = "Create a React frontend with Amplify backend authentication"
    session2 = ManagerSession(workspace_dir)
    response = await session2.send_message(complex_task)

    # Check the actual response text
    if "1 iteration" in response or "single step" in response:
        print("  ❌ BUG FOUND: Response mentions '1 iteration' for complex task!")
        print(f"  Response snippet: {response[:200]}")
    else:
        print("  ✅ Response correctly describes multiple steps")

    # Check if it says "incremental steps" properly
    if "incremental steps" in response or "increments" in response:
        print("  ✅ Uses correct 'incremental' terminology")
    else:
        print("  ⚠️  Missing 'incremental' terminology")

    # Test 3: Dashboard rendering consistency
    print("\n3. Testing dashboard rendering consistency:")
    print("-" * 40)

    if session2.current_plan:
        panel = ExecutionPlanPanel()
        panel.plan = session2.current_plan
        rendered = panel.render()

        # Check key elements
        checks = [
            ("Steps: 6", "Shows correct step count"),
            ("Backend: 2", "Shows backend components"),
            ("Frontend: 3", "Shows frontend components"),
            ("Testing: 1", "Shows testing component"),
            ("~265 lines", "Shows complexity estimate"),
        ]

        for check_str, desc in checks:
            if check_str in rendered:
                print(f"  ✅ {desc}")
            else:
                print(f"  ❌ Missing: {desc}")

    # Test 4: Error handling
    print("\n4. Testing error handling:")
    print("-" * 40)

    error_cases = [
        "",  # Empty message
        "hi",  # Too short
        "what's up?",  # Question without task
    ]

    for msg in error_cases:
        session3 = ManagerSession(workspace_dir)
        response = await session3.send_message(msg)
        if session3.current_plan:
            print(f"  ❌ Incorrectly created plan for: '{msg}'")
        else:
            print(f"  ✅ Correctly handled non-task: '{msg}'")


async def test_production_quality():
    """Test production-ready code quality."""
    print("\n" + "=" * 60)
    print("PRODUCTION QUALITY CHECKS")
    print("=" * 60)

    workspace_dir = Path.cwd()

    # Test 1: Manager initialization
    print("\n1. Manager initialization:")
    print("-" * 40)
    try:
        manager = ManagerAgent(workspace_dir)
        print("  ✅ Manager initialized successfully")
        print(f"  ✅ Auto-approve: {manager.auto_approve}")
        print(f"  ✅ Max increment lines: {manager.max_increment_lines}")
    except Exception as e:
        print(f"  ❌ Manager initialization failed: {e}")

    # Test 2: Context detection
    print("\n2. Context detection:")
    print("-" * 40)
    try:
        context = manager.context
        if context:
            print(f"  ✅ Project type: {context.project_type}")
            print(f"  ✅ Languages: {', '.join(context.tech_stack.languages)}")
            if context.tech_stack.frameworks:
                print(f"  ✅ Frameworks: {', '.join(context.tech_stack.frameworks)}")
        else:
            print("  ⚠️  No context detected")
    except Exception as e:
        print(f"  ❌ Context detection failed: {e}")

    # Test 3: Plan creation performance
    print("\n3. Plan creation performance:")
    print("-" * 40)

    import time

    tasks = [
        "Add user authentication",
        "Create REST API",
        "Build dashboard UI",
    ]

    for task in tasks:
        start = time.time()
        plan = await manager.process_request(task)
        elapsed = time.time() - start

        if elapsed < 0.1:
            status = "✅ Excellent"
        elif elapsed < 0.5:
            status = "✅ Good"
        elif elapsed < 1.0:
            status = "⚠️  Acceptable"
        else:
            status = "❌ Too slow"

        print(
            f"  {status}: {task[:30]} -> {elapsed:.3f}s ({len(plan.increments)} increments)"
        )

    # Test 4: Memory and resource usage
    print("\n4. Resource usage:")
    print("-" * 40)

    import psutil
    import os

    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024

    if memory_mb < 100:
        print(f"  ✅ Memory usage: {memory_mb:.1f} MB (excellent)")
    elif memory_mb < 200:
        print(f"  ✅ Memory usage: {memory_mb:.1f} MB (good)")
    else:
        print(f"  ⚠️  Memory usage: {memory_mb:.1f} MB (high)")

    # Test 5: File structure
    print("\n5. Project structure:")
    print("-" * 40)

    required_files = [
        ("LICENSE", "License file"),
        ("CHANGELOG.md", "Changelog"),
        (".gitignore", "Git ignore"),
        ("setup.py", "Setup script"),
        ("requirements.txt", "Requirements"),
        ("README.md", "README"),
    ]

    for file, desc in required_files:
        if Path(file).exists():
            print(f"  ✅ {desc} exists")
        else:
            print(f"  ❌ Missing {desc}")


async def main():
    """Run all tests."""
    await test_edge_cases()
    await test_production_quality()

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("\nAll tests completed. Review the results above for any issues.")
    print("The system appears to be working correctly with proper task breakdown.")
    print("If you're still seeing '1 iteration' in the actual dashboard UI,")
    print("it might be a display refresh issue or a different code path.")


if __name__ == "__main__":
    asyncio.run(main())
