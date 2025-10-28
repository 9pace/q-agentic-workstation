#!/usr/bin/env python3
"""
Test backdoor for debugging agent execution issues.

This creates a simple test environment to debug why agents are stalling.
"""

import asyncio
import tempfile
import sys
import time
from pathlib import Path

# Add the qaw package to path
sys.path.insert(0, str(Path(__file__).parent))

from qaw.manager import ManagerSession
from qaw.state import StateManager, TaskPriority, AgentStatus
from qaw.executor import AgentExecutor


def create_test_workspace():
    """Create a test workspace with proper structure."""
    test_dir = Path(tempfile.mkdtemp())
    print(f"Test workspace: {test_dir}")

    # Initialize QAW workspace
    qaw_dir = test_dir / ".qaw"
    qaw_dir.mkdir()
    for subdir in ["state", "logs", "results", "pids", "context"]:
        (qaw_dir / subdir).mkdir()

    return test_dir


def test_direct_agent_execution():
    """Test direct agent execution without manager."""
    print("🧪 Testing Direct Agent Execution...")

    test_dir = create_test_workspace()
    state = StateManager(test_dir)
    executor = AgentExecutor(state)

    # Create a simple task
    task = state.create_task(
        description="Create a simple hello.txt file with 'Hello World'",
        priority=TaskPriority.HIGH,
    )

    # Create agent
    agent = state.create_agent(
        agent_name="test-agent", task_id=task.id, task_description=task.description
    )

    print(f"Created agent: {agent.semantic_name} ({agent.id})")
    print(f"Task: {task.description}")

    try:
        # Spawn agent with minimal settings
        print("Spawning agent...")
        pid = executor.spawn_agent(
            agent,
            trust_all_tools=True,
            autopilot=False,  # Don't use autopilot for testing
        )

        print(f"Agent spawned with PID: {pid}")

        # Monitor for 60 seconds
        for i in range(12):  # 12 * 5 = 60 seconds
            time.sleep(5)
            status = executor.check_agent_status(agent.id)
            agent_state = state.get_agent(agent.id)

            print(f"[{i*5:2d}s] Status: {status.value if status else 'unknown'}")

            if status and status.value in ["completed", "failed", "cancelled"]:
                print(f"Agent finished with status: {status.value}")
                break

            if agent_state and agent_state.error_message:
                print(f"Error: {agent_state.error_message}")
                break
        else:
            print("Agent still running after 60 seconds - may be stalled")

        # Check logs
        if agent.log_file and Path(agent.log_file).exists():
            print("\n📋 Agent Log (last 20 lines):")
            with open(agent.log_file) as f:
                lines = f.readlines()
                for line in lines[-20:]:
                    print(f"  {line.rstrip()}")
        else:
            print("❌ No log file found")

        # Check results
        if agent.result_dir and Path(agent.result_dir).exists():
            result_files = list(Path(agent.result_dir).glob("*"))
            print(f"\n📁 Result files: {len(result_files)}")
            for f in result_files:
                print(f"  {f.name}")

        return True

    except Exception as e:
        print(f"❌ Error during execution: {e}")
        return False


async def test_manager_execution():
    """Test manager-based execution."""
    print("\n🧪 Testing Manager Execution...")

    test_dir = create_test_workspace()
    session = ManagerSession(test_dir)

    # Test simple task
    print("Sending simple task to manager...")
    response = await session.send_message("Create a simple hello.txt file")
    print(f"Manager response: {response}")

    if session.current_plan:
        print(f"Plan created with {len(session.current_plan.increments)} increments")

        # Try to execute just the first increment manually
        increment = session.current_plan.increments[0]
        print(f"Testing increment: {increment.description}")

        # Create task and agent manually
        task = session.manager.state.create_task(
            description=increment.description,
            priority=TaskPriority.HIGH,
        )

        agent = session.manager.state.create_agent(
            agent_name=f"{increment.agent_type}-agent",
            task_id=task.id,
            task_description=increment.description,
        )

        print(f"Created agent: {agent.semantic_name} ({agent.id})")

        try:
            # Spawn with basic settings
            pid = session.manager.executor.spawn_agent(
                agent,
                trust_all_tools=True,
                autopilot=False,  # No autopilot for testing
            )

            print(f"Agent spawned with PID: {pid}")

            # Wait and monitor
            for i in range(6):  # 30 seconds
                await asyncio.sleep(5)
                status = session.manager.executor.check_agent_status(agent.id)
                print(f"[{i*5:2d}s] Status: {status.value if status else 'unknown'}")

                if status and status.value in ["completed", "failed", "cancelled"]:
                    print(f"Agent finished: {status.value}")
                    break
            else:
                print("Agent still running after 30 seconds")

            # Check logs
            if agent.log_file and Path(agent.log_file).exists():
                print("\n📋 Agent Log (last 10 lines):")
                with open(agent.log_file) as f:
                    lines = f.readlines()
                    for line in lines[-10:]:
                        print(f"  {line.rstrip()}")

            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    return False


def main():
    """Run all tests."""
    print("🚀 Q Agentic Workstation - Agent Execution Debug")
    print("=" * 60)

    # Test 1: Direct execution
    direct_success = test_direct_agent_execution()

    # Test 2: Manager execution
    manager_success = asyncio.run(test_manager_execution())

    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"Direct Execution: {'✅' if direct_success else '❌'}")
    print(f"Manager Execution: {'✅' if manager_success else '❌'}")

    if not direct_success and not manager_success:
        print("\n⚠️  Both tests failed - likely Q CLI or configuration issue")
        print("Check:")
        print("1. Q CLI is installed and working: `q --version`")
        print("2. Agent configs exist in ~/.aws/amazonq/cli-agents/")
        print("3. No firewall/network issues")
    elif direct_success and not manager_success:
        print("\n⚠️  Manager has issues but direct execution works")
    elif not direct_success and manager_success:
        print("\n⚠️  Direct execution failed but manager works (unusual)")
    else:
        print("\n🎉 Both tests passed!")


if __name__ == "__main__":
    main()
