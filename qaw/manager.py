"""
Manager Agent for Q Agentic Workstation.

Intelligent orchestrator that breaks down tasks, spawns agents, and verifies results.
"""

import asyncio
import subprocess
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

from .state import StateManager, AgentState, AgentStatus, TaskPriority
from .executor import AgentExecutor
from .context import ContextManager, ProjectContext
from .naming import generate_manager_name

logger = logging.getLogger(__name__)


class IncrementStatus(Enum):
    """Status of a single increment."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class Increment:
    """A single increment of work."""
    id: str
    description: str
    agent_type: str
    estimated_lines: int
    dependencies: List[str] = field(default_factory=list)
    status: IncrementStatus = IncrementStatus.PENDING
    agent_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    verification_feedback: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'description': self.description,
            'agent_type': self.agent_type,
            'estimated_lines': self.estimated_lines,
            'dependencies': self.dependencies,
            'status': self.status.value,
            'agent_id': self.agent_id,
            'retry_count': self.retry_count,
            'verification_feedback': self.verification_feedback,
        }


@dataclass
class ExecutionPlan:
    """Plan for executing a user request."""
    user_request: str
    increments: List[Increment]
    total_estimated_lines: int
    context: ProjectContext
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'user_request': self.user_request,
            'increments': [inc.to_dict() for inc in self.increments],
            'total_estimated_lines': self.total_estimated_lines,
        }


class ManagerAgent:
    """
    Intelligent manager that orchestrates agent teams.
    
    Responsibilities:
    - Analyze user requests
    - Break down into minimal increments
    - Spawn appropriate agents
    - Monitor progress
    - Coordinate verification
    - Handle retries
    """
    
    def __init__(
        self,
        workspace_dir: Path,
        auto_approve: bool = True,
        max_increment_lines: int = 50,
    ):
        """
        Initialize manager.
        
        Args:
            workspace_dir: QAW workspace directory
            auto_approve: Auto-approve all tool use
            max_increment_lines: Maximum lines per increment
        """
        self.workspace_dir = workspace_dir
        self.auto_approve = auto_approve
        self.max_increment_lines = max_increment_lines
        
        self.state = StateManager(workspace_dir)
        self.executor = AgentExecutor(self.state)
        self.context_manager = ContextManager(workspace_dir)
        
        # Get or initialize project context
        self.context = self.context_manager.get_context()
        if not self.context:
            logger.info("No project context found, initializing...")
            self.context = self.context_manager.initialize()
    
    async def process_request(self, user_request: str) -> ExecutionPlan:
        """
        Process user request and create execution plan.
        
        Args:
            user_request: Natural language request from user
            
        Returns:
            ExecutionPlan with increments to execute
        """
        logger.info(f"Processing request: {user_request}")
        
        # Analyze request and create plan
        plan = await self._create_plan(user_request)
        
        logger.info(f"Created plan with {len(plan.increments)} increments")
        return plan
    
    async def execute_plan(
        self,
        plan: ExecutionPlan,
        progress_callback: Optional[callable] = None,
    ) -> bool:
        """
        Execute the plan increment by increment.
        
        Args:
            plan: ExecutionPlan to execute
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if all increments completed successfully
        """
        logger.info(f"Executing plan for: {plan.user_request}")
        
        for increment in plan.increments:
            success = await self._execute_increment(increment, progress_callback)
            
            if not success:
                logger.error(f"Increment {increment.id} failed after retries")
                return False
        
        logger.info("Plan execution complete!")
        return True
    
    async def _create_plan(self, user_request: str) -> ExecutionPlan:
        """
        Create execution plan by breaking down request.
        
        Uses Q CLI orchestrator-agent to analyze and decompose.
        """
        # For now, use a simple breakdown strategy
        # In production, this would use Q CLI orchestrator-agent
        
        increments = await self._break_down_task(user_request)
        total_lines = sum(inc.estimated_lines for inc in increments)
        
        return ExecutionPlan(
            user_request=user_request,
            increments=increments,
            total_estimated_lines=total_lines,
            context=self.context,
        )
    
    async def _break_down_task(self, task: str) -> List[Increment]:
        """
        Break down task into minimal increments.
        
        Strategy:
        1. Detect task type (add feature, fix bug, refactor, etc.)
        2. Consider project context
        3. Create <50 line increments
        4. Assign appropriate agent types
        """
        # Simple heuristic-based breakdown for now
        # In production, use LLM-based analysis
        
        task_lower = task.lower()
        increments = []
        
        # Detect task type
        if any(word in task_lower for word in ['add', 'create', 'implement', 'build']):
            # Feature addition - break into layers
            increments.extend(self._plan_feature_addition(task))
        
        elif any(word in task_lower for word in ['fix', 'bug', 'issue', 'problem']):
            # Bug fix - simpler breakdown
            increments.extend(self._plan_bug_fix(task))
        
        elif any(word in task_lower for word in ['refactor', 'improve', 'optimize']):
            # Refactoring - careful increments
            increments.extend(self._plan_refactoring(task))
        
        elif any(word in task_lower for word in ['test', 'verify']):
            # Testing task
            increments.extend(self._plan_testing(task))
        
        else:
            # Generic task - single increment
            increments.append(Increment(
                id=f"inc-{len(increments)+1}",
                description=task,
                agent_type="orchestrator",
                estimated_lines=30,
            ))
        
        return increments
    
    def _plan_feature_addition(self, task: str) -> List[Increment]:
        """Plan increments for feature addition."""
        increments = []
        
        # Check if it's data-related
        if any(word in task.lower() for word in ['model', 'database', 'schema', 'table']):
            increments.append(Increment(
                id=f"inc-1",
                description=f"Add data model/schema: {task}",
                agent_type="backend",
                estimated_lines=40,
            ))
        
        # Check if it's API-related
        if any(word in task.lower() for word in ['api', 'endpoint', 'route', 'controller']):
            increments.append(Increment(
                id=f"inc-{len(increments)+1}",
                description=f"Add API endpoint: {task}",
                agent_type="backend",
                estimated_lines=45,
                dependencies=[increments[0].id] if increments else [],
            ))
        
        # Check if it's UI-related
        if any(word in task.lower() for word in ['ui', 'page', 'component', 'form', 'button']):
            increments.append(Increment(
                id=f"inc-{len(increments)+1}",
                description=f"Add UI component: {task}",
                agent_type="frontend",
                estimated_lines=50,
            ))
        
        # Add tests if test framework detected
        if self.context.patterns.test_framework:
            increments.append(Increment(
                id=f"inc-{len(increments)+1}",
                description=f"Add tests for: {task}",
                agent_type="test",
                estimated_lines=35,
                dependencies=[inc.id for inc in increments],
            ))
        
        # If no specific breakdown, use generic
        if not increments:
            increments.append(Increment(
                id="inc-1",
                description=task,
                agent_type="orchestrator",
                estimated_lines=40,
            ))
        
        return increments
    
    def _plan_bug_fix(self, task: str) -> List[Increment]:
        """Plan increments for bug fix."""
        return [
            Increment(
                id="inc-1",
                description=f"Investigate and fix: {task}",
                agent_type="backend",  # or frontend based on keywords
                estimated_lines=30,
            ),
            Increment(
                id="inc-2",
                description=f"Add regression test for: {task}",
                agent_type="test",
                estimated_lines=25,
                dependencies=["inc-1"],
            ),
        ]
    
    def _plan_refactoring(self, task: str) -> List[Increment]:
        """Plan increments for refactoring."""
        # Refactoring needs careful small steps
        return [
            Increment(
                id="inc-1",
                description=f"Refactor (step 1): {task}",
                agent_type="backend",
                estimated_lines=40,
            ),
            Increment(
                id="inc-2",
                description=f"Verify refactoring with tests: {task}",
                agent_type="test",
                estimated_lines=30,
                dependencies=["inc-1"],
            ),
        ]
    
    def _plan_testing(self, task: str) -> List[Increment]:
        """Plan increments for testing task."""
        return [
            Increment(
                id="inc-1",
                description=task,
                agent_type="test",
                estimated_lines=45,
            ),
        ]
    
    async def _execute_increment(
        self,
        increment: Increment,
        progress_callback: Optional[callable] = None,
    ) -> bool:
        """
        Execute a single increment with retry logic.
        
        Returns:
            True if increment completed successfully
        """
        while increment.retry_count <= increment.max_retries:
            logger.info(f"Executing increment {increment.id}: {increment.description}")
            
            # Update status
            increment.status = IncrementStatus.IN_PROGRESS
            if progress_callback:
                progress_callback(increment)
            
            # Create task
            task = self.state.create_task(
                description=increment.description,
                priority=TaskPriority.HIGH,
            )
            
            # Spawn agent
            agent = self.state.create_agent(
                agent_name=f"{increment.agent_type}-agent",
                task_id=task.id,
                task_description=increment.description,
            )
            increment.agent_id = agent.id
            
            try:
                # Spawn with autopilot + auto-approval
                pid = self.executor.spawn_agent(
                    agent,
                    trust_all_tools=self.auto_approve,
                    autopilot=True,
                )
                
                # Wait for completion
                status = await self._wait_for_agent(agent.id)
                
                if status == AgentStatus.COMPLETED:
                    # Verify if verification is enabled
                    if self._should_verify(increment):
                        increment.status = IncrementStatus.VERIFYING
                        if progress_callback:
                            progress_callback(increment)
                        
                        verification_passed = await self._verify_increment(increment, agent.id)
                        
                        if verification_passed:
                            increment.status = IncrementStatus.COMPLETED
                            logger.info(f"Increment {increment.id} completed and verified")
                            return True
                        else:
                            # Verification failed - retry with feedback
                            increment.retry_count += 1
                            increment.status = IncrementStatus.RETRY
                            logger.warning(f"Increment {increment.id} verification failed, retrying...")
                            continue
                    else:
                        # No verification needed
                        increment.status = IncrementStatus.COMPLETED
                        logger.info(f"Increment {increment.id} completed")
                        return True
                else:
                    # Agent failed
                    increment.retry_count += 1
                    increment.status = IncrementStatus.RETRY
                    logger.warning(f"Increment {increment.id} agent failed, retrying...")
                    continue
            
            except Exception as e:
                logger.error(f"Error executing increment {increment.id}: {e}")
                increment.retry_count += 1
                increment.status = IncrementStatus.RETRY
                continue
        
        # Max retries exceeded
        increment.status = IncrementStatus.FAILED
        return False
    
    async def _wait_for_agent(self, agent_id: str, timeout: int = 600) -> AgentStatus:
        """
        Wait for agent to complete.
        
        Args:
            agent_id: Agent ID
            timeout: Timeout in seconds (default 10 minutes)
            
        Returns:
            Final agent status
        """
        elapsed = 0
        check_interval = 5  # seconds
        
        while elapsed < timeout:
            agent = self.state.get_agent(agent_id)
            if not agent:
                return AgentStatus.FAILED
            
            status = self.executor.check_agent_status(agent_id)
            
            if status in [AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.CANCELLED]:
                return status
            
            await asyncio.sleep(check_interval)
            elapsed += check_interval
        
        # Timeout
        logger.warning(f"Agent {agent_id} timed out after {timeout}s")
        return AgentStatus.FAILED
    
    def _should_verify(self, increment: Increment) -> bool:
        """Check if increment should be verified."""
        # For now, verify all non-test increments
        # In production, make this configurable
        return increment.agent_type != "test"
    
    async def _verify_increment(self, increment: Increment, agent_id: str) -> bool:
        """
        Verify increment with basic checks.
        
        In production, this would use the full 3-stage verification pipeline.
        For now, just check if agent completed successfully.
        """
        agent = self.state.get_agent(agent_id)
        if not agent:
            return False
        
        # Check agent status
        if agent.status != AgentStatus.COMPLETED:
            increment.verification_feedback = "Agent did not complete successfully"
            return False
        
        # Check for errors in log
        if agent.log_file:
            try:
                with open(agent.log_file) as f:
                    log_content = f.read()
                    
                    # Simple heuristic: look for error indicators
                    error_indicators = ['error:', 'failed:', 'exception:', 'traceback']
                    if any(indicator in log_content.lower() for indicator in error_indicators):
                        increment.verification_feedback = "Errors detected in agent log"
                        return False
            except:
                pass
        
        # Basic verification passed
        return True


class ManagerSession:
    """
    Interactive session with manager agent.
    
    Maintains conversation history and state.
    """
    
    def __init__(self, workspace_dir: Path):
        """Initialize session."""
        self.workspace_dir = workspace_dir
        self.manager = ManagerAgent(workspace_dir)
        self.conversation_history: List[Dict[str, str]] = []
        self.current_plan: Optional[ExecutionPlan] = None
    
    async def send_message(self, message: str) -> str:
        """
        Send message to manager and get response.
        
        Args:
            message: User message
            
        Returns:
            Manager response
        """
        # Add to conversation
        self.conversation_history.append({
            'role': 'user',
            'content': message,
        })
        
        # Process request
        plan = await self.manager.process_request(message)
        self.current_plan = plan
        
        # Format response
        response = self._format_plan_response(plan)
        
        self.conversation_history.append({
            'role': 'manager',
            'content': response,
        })
        
        return response
    
    async def execute_current_plan(self, progress_callback: Optional[callable] = None) -> bool:
        """Execute the current plan."""
        if not self.current_plan:
            return False
        
        return await self.manager.execute_plan(self.current_plan, progress_callback)
    
    def _format_plan_response(self, plan: ExecutionPlan) -> str:
        """Format plan as text response."""
        response = f"I'll break this into {len(plan.increments)} increment(s):\n\n"
        
        for i, increment in enumerate(plan.increments, 1):
            status_emoji = "⏳"
            response += f"{i}. {status_emoji} {increment.description} (~{increment.estimated_lines} lines)\n"
        
        response += f"\nTotal estimated: ~{plan.total_estimated_lines} lines\n"
        response += "\nReady to proceed?"
        
        return response
    
    def get_status_summary(self) -> str:
        """Get status summary of current plan."""
        if not self.current_plan:
            return "No active plan"
        
        summary = f"Plan: {self.current_plan.user_request}\n\n"
        
        for i, increment in enumerate(self.current_plan.increments, 1):
            status_emoji = {
                IncrementStatus.PENDING: "⏳",
                IncrementStatus.IN_PROGRESS: "🔄",
                IncrementStatus.VERIFYING: "🔍",
                IncrementStatus.COMPLETED: "✓",
                IncrementStatus.FAILED: "✗",
                IncrementStatus.RETRY: "🔁",
            }.get(increment.status, "?")
            
            summary += f"{i}. {status_emoji} {increment.description}\n"
        
        return summary
