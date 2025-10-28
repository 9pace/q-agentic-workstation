#!/usr/bin/env python3
"""
Comprehensive validation script for Q Agentic Workstation.

Tests all major components and fixes to ensure production-level quality.
"""

import asyncio
import tempfile
import sys
import time
import traceback
from pathlib import Path
from typing import List, Dict, Any

# Add the qaw package to path
sys.path.insert(0, str(Path(__file__).parent))

from qaw.manager import ManagerSession
from qaw.state import StateManager, TaskPriority, AgentStatus
from qaw.executor import AgentExecutor
from qaw.naming import AgentNamer
from qaw.context import ContextManager


class ValidationResult:
    """Result of a validation test."""

    def __init__(self, name: str, success: bool, message: str, details: str = ""):
        self.name = name
        self.success = success
        self.message = message
        self.details = details


class ComprehensiveValidator:
    """Comprehensive validation suite for QAW."""

    def __init__(self):
        self.results: List[ValidationResult] = []
        self.test_workspace = None

    def create_test_workspace(self) -> Path:
        """Create a test workspace with proper structure."""
        test_dir = Path(tempfile.mkdtemp())
        print(f"Test workspace: {test_dir}")

        # Initialize QAW workspace
        qaw_dir = test_dir / ".qaw"
        qaw_dir.mkdir()
        for subdir in ["state", "logs", "results", "pids", "context"]:
            (qaw_dir / subdir).mkdir()

        return test_dir

    def add_result(self, name: str, success: bool, message: str, details: str = ""):
        """Add a test result."""
        result = ValidationResult(name, success, message, details)
        self.results.append(result)

        status = "✅" if success else "❌"
        print(f"{status} {name}: {message}")
        if details and not success:
            print(f"   Details: {details}")

    def test_state_management(self) -> None:
        """Test state management functionality."""
        print("\n🧪 Testing State Management...")

        try:
            test_dir = self.create_test_workspace()
            state = StateManager(test_dir)

            # Test task creation
            task = state.create_task(
                description="Test task", priority=TaskPriority.HIGH
            )

            self.add_result(
                "Task Creation",
                task.id is not None and task.description == "Test task",
                "Task created successfully",
            )

            # Test agent creation with semantic naming
            agent = state.create_agent(
                agent_name="frontend-agent",
                task_id=task.id,
                task_description="Create a React login component",
            )

            self.add_result(
                "Agent Creation",
                agent.id is not None and agent.semantic_name is not None,
                f"Agent created with semantic name: {agent.semantic_name}",
            )

            # Test state persistence
            saved_agent = state.get_agent(agent.id)
            self.add_result(
                "State Persistence",
                saved_agent is not None
                and saved_agent.semantic_name == agent.semantic_name,
                "Agent state persisted correctly",
            )

            # Test statistics
            stats = state.get_stats()
            self.add_result(
                "Statistics",
                stats["total"] == 1 and stats["pending"] == 1,
                f"Statistics correct: {stats}",
            )

        except Exception as e:
            self.add_result(
                "State Management", False, "State management test failed", str(e)
            )

    def test_semantic_naming(self) -> None:
        """Test semantic naming functionality."""
        print("\n🧪 Testing Semantic Naming...")

        try:
            # Test various naming scenarios
            test_cases = [
                (
                    "Create a React login component",
                    "frontend",
                    "frontend-create-react-login",
                ),
                ("Add user authentication API", "backend", "backend-add-user-auth"),
                ("Write unit tests for auth service", "test", "test-write-unit-auth"),
                ("Document the API endpoints", "doc", "doc-document-api-endpoints"),
                (
                    "Fix login bug in auth.py",
                    "orchestrator",
                    "orchestrator-fix-login-bug",
                ),
            ]

            for task_desc, agent_type, expected_pattern in test_cases:
                name = AgentNamer.generate_name(task_desc, agent_type)

                # Check if name follows expected pattern (contains key words)
                key_words = expected_pattern.split("-")[1:]  # Skip agent type prefix
                contains_key_words = all(
                    word in name.lower() for word in key_words[:2]
                )  # Check first 2 key words

                self.add_result(
                    f"Semantic Naming: {agent_type}",
                    contains_key_words and len(name) <= 50,
                    f"Generated: {name}",
                )

        except Exception as e:
            self.add_result(
                "Semantic Naming", False, "Semantic naming test failed", str(e)
            )

    def test_task_breakdown(self) -> None:
        """Test enhanced task breakdown logic."""
        print("\n🧪 Testing Task Breakdown Logic...")

        try:
            test_dir = self.create_test_workspace()
            session = ManagerSession(test_dir)

            # Test complex authentication task
            complex_task = "Create a React frontend with user authentication using AWS Amplify backend"

            response = asyncio.run(session.send_message(complex_task))

            # Check if plan was created
            plan_created = session.current_plan is not None

            if plan_created:
                num_increments = len(session.current_plan.increments)

                # Complex auth task should generate multiple increments
                self.add_result(
                    "Complex Task Breakdown",
                    num_increments >= 3,
                    f"Generated {num_increments} increments for complex auth task",
                )

                # Check if increments have proper dependencies
                has_dependencies = any(
                    len(inc.dependencies) > 0
                    for inc in session.current_plan.increments[
                        1:
                    ]  # Skip first increment
                )

                self.add_result(
                    "Task Dependencies",
                    has_dependencies,
                    "Task increments have proper dependencies",
                )

            else:
                self.add_result(
                    "Task Breakdown", False, "Failed to create execution plan"
                )

            # Test simple task
            simple_task = "Create a hello.txt file"
            response = asyncio.run(session.send_message(simple_task))

            if session.current_plan:
                simple_increments = len(session.current_plan.increments)
                self.add_result(
                    "Simple Task Breakdown",
                    simple_increments == 1,
                    f"Generated {simple_increments} increment for simple task",
                )

        except Exception as e:
            self.add_result(
                "Task Breakdown", False, "Task breakdown test failed", str(e)
            )

    def test_agent_execution(self) -> None:
        """Test agent execution functionality."""
        print("\n🧪 Testing Agent Execution...")

        try:
            test_dir = self.create_test_workspace()
            state = StateManager(test_dir)
            executor = AgentExecutor(state)

            # Create a simple task
            task = state.create_task(
                description="Create a simple test.txt file with 'Hello Test'",
                priority=TaskPriority.HIGH,
            )

            # Create agent
            agent = state.create_agent(
                agent_name="test-agent",
                task_id=task.id,
                task_description=task.description,
            )

            # Test agent spawning
            try:
                pid = executor.spawn_agent(
                    agent,
                    trust_all_tools=True,
                    autopilot=False,
                )

                self.add_result(
                    "Agent Spawning", pid > 0, f"Agent spawned with PID: {pid}"
                )

                # Monitor agent for completion
                max_wait = 30  # 30 seconds
                for i in range(max_wait):
                    time.sleep(1)
                    status = executor.check_agent_status(agent.id)

                    if status and status.value in ["completed", "failed", "cancelled"]:
                        self.add_result(
                            "Agent Completion",
                            status.value == "completed",
                            f"Agent completed with status: {status.value}",
                        )
                        break
                else:
                    self.add_result(
                        "Agent Completion",
                        False,
                        "Agent did not complete within 30 seconds",
                    )

                # Test log file creation
                log_exists = Path(agent.log_file).exists()
                self.add_result(
                    "Log File Creation", log_exists, "Agent log file created"
                )

            except Exception as spawn_error:
                self.add_result(
                    "Agent Execution", False, "Agent spawning failed", str(spawn_error)
                )

        except Exception as e:
            self.add_result(
                "Agent Execution", False, "Agent execution test failed", str(e)
            )

    def test_dashboard_imports(self) -> None:
        """Test dashboard import functionality."""
        print("\n🧪 Testing Dashboard Imports...")

        try:
            # Test hybrid dashboard import
            from qaw.dashboard_hybrid import run_hybrid_dashboard, HybridDashboardApp

            self.add_result(
                "Hybrid Dashboard Import", True, "Hybrid dashboard imports successfully"
            )

            # Test original dashboard import
            from qaw.dashboard import run_dashboard, DashboardApp

            self.add_result(
                "Original Dashboard Import",
                True,
                "Original dashboard imports successfully",
            )

            # Test CLI integration
            from qaw.cli import dashboard

            self.add_result(
                "CLI Dashboard Integration", True, "CLI dashboard command available"
            )

        except Exception as e:
            self.add_result(
                "Dashboard Imports", False, "Dashboard import test failed", str(e)
            )

    def test_context_management(self) -> None:
        """Test context management functionality."""
        print("\n🧪 Testing Context Management...")

        try:
            test_dir = self.create_test_workspace()

            # Create some test files to analyze
            (test_dir / "package.json").write_text(
                '{"name": "test", "dependencies": {"react": "^18.0.0"}}'
            )
            (test_dir / "src").mkdir()
            (test_dir / "src" / "App.tsx").write_text("import React from 'react';")

            context_mgr = ContextManager(test_dir)
            context = context_mgr.initialize()

            self.add_result(
                "Context Initialization",
                context is not None,
                "Context initialized successfully",
            )

            # Check if React was detected
            react_detected = "React" in context.tech_stack.frameworks
            self.add_result(
                "Technology Detection",
                react_detected,
                f"Detected frameworks: {context.tech_stack.frameworks}",
            )

        except Exception as e:
            self.add_result(
                "Context Management", False, "Context management test failed", str(e)
            )

    def test_error_handling(self) -> None:
        """Test error handling and edge cases."""
        print("\n🧪 Testing Error Handling...")

        try:
            test_dir = self.create_test_workspace()
            state = StateManager(test_dir)

            # Test invalid agent ID
            invalid_agent = state.get_agent("invalid-id")
            self.add_result(
                "Invalid Agent Handling",
                invalid_agent is None,
                "Invalid agent ID handled gracefully",
            )

            # Test invalid task ID
            invalid_task = state.get_task("invalid-task-id")
            self.add_result(
                "Invalid Task Handling",
                invalid_task is None,
                "Invalid task ID handled gracefully",
            )

            # Test executor with invalid agent
            executor = AgentExecutor(state)
            status = executor.check_agent_status("invalid-agent-id")
            self.add_result(
                "Invalid Agent Status Check",
                status is None,
                "Invalid agent status check handled gracefully",
            )

        except Exception as e:
            self.add_result(
                "Error Handling", False, "Error handling test failed", str(e)
            )

    def test_performance(self) -> None:
        """Test performance characteristics."""
        print("\n🧪 Testing Performance...")

        try:
            test_dir = self.create_test_workspace()
            state = StateManager(test_dir)

            # Test creating many agents quickly
            start_time = time.time()
            agents = []

            for i in range(10):
                task = state.create_task(f"Test task {i}", TaskPriority.MEDIUM)
                agent = state.create_agent(
                    agent_name="test-agent",
                    task_id=task.id,
                    task_description=f"Test task {i}",
                )
                agents.append(agent)

            creation_time = time.time() - start_time

            self.add_result(
                "Agent Creation Performance",
                creation_time < 5.0,  # Should create 10 agents in under 5 seconds
                f"Created 10 agents in {creation_time:.2f}s",
            )

            # Test statistics calculation performance
            start_time = time.time()
            stats = state.get_stats()
            stats_time = time.time() - start_time

            self.add_result(
                "Statistics Performance",
                stats_time < 1.0 and stats["total"] == 10,
                f"Statistics calculated in {stats_time:.3f}s",
            )

        except Exception as e:
            self.add_result("Performance", False, "Performance test failed", str(e))

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all validation tests."""
        print("🚀 Q Agentic Workstation - Comprehensive Validation")
        print("=" * 60)

        # Run all test suites
        self.test_state_management()
        self.test_semantic_naming()
        self.test_task_breakdown()
        self.test_agent_execution()
        self.test_dashboard_imports()
        self.test_context_management()
        self.test_error_handling()
        self.test_performance()

        # Calculate results
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests

        print("\n" + "=" * 60)
        print("📊 Validation Results:")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if not result.success:
                    print(f"  • {result.name}: {result.message}")
                    if result.details:
                        print(f"    Details: {result.details}")

        print("\n" + "=" * 60)

        if failed_tests == 0:
            print("🎉 All tests passed! QAW is production-ready.")
        else:
            print(
                f"⚠️  {failed_tests} test(s) failed. Review and fix issues before production."
            )

        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "results": self.results,
        }


def main():
    """Run comprehensive validation."""
    validator = ComprehensiveValidator()
    results = validator.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
