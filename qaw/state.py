"""
State management for Q Agentic Workstation.

Handles persistence and querying of agent states, task queue, and execution history.
"""

import json
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import fcntl
import os
from .naming import AgentNamer


class AgentStatus(Enum):
    """Agent execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentState:
    """State of a single agent execution."""
    id: str
    agent_name: str
    task_id: str
    task_description: str
    status: AgentStatus
    pid: Optional[int] = None
    parent_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    log_file: Optional[str] = None
    result_dir: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    semantic_name: Optional[str] = None  # Human-readable name like 'backend-auth-login'

    def to_dict(self) -> Dict:
        """Convert to dictionary with enum serialization."""
        data = asdict(self)
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentState':
        """Create from dictionary with enum deserialization."""
        data['status'] = AgentStatus(data['status'])
        return cls(**data)


@dataclass
class Task:
    """A task to be executed by agents."""
    id: str
    description: str
    priority: TaskPriority
    status: AgentStatus
    assigned_agent_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary with enum serialization."""
        data = asdict(self)
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """Create from dictionary with enum deserialization."""
        data['priority'] = TaskPriority(data['priority'])
        data['status'] = AgentStatus(data['status'])
        return cls(**data)


class StateManager:
    """Manages persistent state for the workstation."""

    def __init__(self, workspace_dir: Path):
        """
        Initialize state manager.

        Args:
            workspace_dir: Root directory for state storage (.qaw)
        """
        self.workspace_dir = workspace_dir
        self.state_dir = workspace_dir / "state"
        self.agents_dir = self.state_dir / "agents"
        self.tasks_dir = self.state_dir / "tasks"
        self.logs_dir = workspace_dir / "logs"
        self.results_dir = workspace_dir / "results"
        self.pids_dir = workspace_dir / "pids"

        # Create directory structure
        for directory in [
            self.state_dir,
            self.agents_dir,
            self.tasks_dir,
            self.logs_dir,
            self.results_dir,
            self.pids_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def _get_file_lock(self, filepath: Path):
        """Get an exclusive file lock for atomic operations."""
        lock_file = filepath.with_suffix('.lock')
        lock_fd = os.open(str(lock_file), os.O_CREAT | os.O_RDWR)
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        return lock_fd

    def _release_file_lock(self, lock_fd: int):
        """Release a file lock."""
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)

    def generate_id(self, prefix: str = "") -> str:
        """Generate a unique ID."""
        short_uuid = str(uuid.uuid4())[:8]
        if prefix:
            return f"{prefix}-{short_uuid}"
        return short_uuid

    def create_task(
        self,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """
        Create a new task.

        Args:
            description: Task description
            priority: Task priority level
            dependencies: List of task IDs this task depends on
            metadata: Additional task metadata

        Returns:
            Created Task object
        """
        task = Task(
            id=self.generate_id("task"),
            description=description,
            priority=priority,
            status=AgentStatus.PENDING,
            dependencies=dependencies or [],
            created_at=datetime.utcnow().isoformat(),
            metadata=metadata or {},
        )
        self.save_task(task)
        return task

    def save_task(self, task: Task):
        """Save task state to disk."""
        task_file = self.tasks_dir / f"{task.id}.json"
        lock_fd = self._get_file_lock(task_file)
        try:
            with open(task_file, 'w') as f:
                json.dump(task.to_dict(), f, indent=2)
        finally:
            self._release_file_lock(lock_fd)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Load task from disk."""
        task_file = self.tasks_dir / f"{task_id}.json"
        if not task_file.exists():
            return None

        with open(task_file, 'r') as f:
            data = json.load(f)
        return Task.from_dict(data)

    def list_tasks(self, status: Optional[AgentStatus] = None) -> List[Task]:
        """List all tasks, optionally filtered by status."""
        tasks = []
        for task_file in self.tasks_dir.glob("*.json"):
            with open(task_file, 'r') as f:
                data = json.load(f)
            task = Task.from_dict(data)
            if status is None or task.status == status:
                tasks.append(task)
        
        # Sort by priority and creation time
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
        }
        tasks.sort(key=lambda t: (priority_order[t.priority], t.created_at or ""))
        return tasks

    def create_agent(
        self,
        agent_name: str,
        task_id: str,
        task_description: str,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        custom_name: Optional[str] = None,
    ) -> AgentState:
        """
        Create a new agent state.

        Args:
            agent_name: Name of the agent configuration
            task_id: Associated task ID
            task_description: Description of task
            parent_id: Parent agent ID if this is a delegated agent
            metadata: Additional metadata
            custom_name: Optional custom semantic name override

        Returns:
            Created AgentState object
        """
        # Generate semantic name
        semantic_name = AgentNamer.generate_name(
            task_description=task_description,
            agent_type=agent_name.replace('-agent', ''),
            custom_name=custom_name,
        )
        
        agent_id = self.generate_id(semantic_name)
        
        agent = AgentState(
            id=agent_id,
            agent_name=agent_name,
            task_id=task_id,
            task_description=task_description,
            status=AgentStatus.PENDING,
            parent_id=parent_id,
            log_file=str(self.logs_dir / f"{agent_id}.log"),
            result_dir=str(self.results_dir / agent_id),
            metadata=metadata or {},
            semantic_name=semantic_name,
        )
        
        # Create result directory
        Path(agent.result_dir).mkdir(parents=True, exist_ok=True)
        
        self.save_agent(agent)
        return agent

    def save_agent(self, agent: AgentState):
        """Save agent state to disk."""
        agent_file = self.agents_dir / f"{agent.id}.json"
        lock_fd = self._get_file_lock(agent_file)
        try:
            with open(agent_file, 'w') as f:
                json.dump(agent.to_dict(), f, indent=2)
        finally:
            self._release_file_lock(lock_fd)

    def get_agent(self, agent_id: str) -> Optional[AgentState]:
        """Load agent state from disk."""
        agent_file = self.agents_dir / f"{agent_id}.json"
        if not agent_file.exists():
            return None

        with open(agent_file, 'r') as f:
            data = json.load(f)
        return AgentState.from_dict(data)

    def list_agents(self, status: Optional[AgentStatus] = None) -> List[AgentState]:
        """List all agents, optionally filtered by status."""
        agents = []
        for agent_file in self.agents_dir.glob("*.json"):
            with open(agent_file, 'r') as f:
                data = json.load(f)
            agent = AgentState.from_dict(data)
            if status is None or agent.status == status:
                agents.append(agent)
        
        # Sort by start time (most recent first)
        agents.sort(key=lambda a: a.start_time or "", reverse=True)
        return agents

    def update_agent_status(
        self,
        agent_id: str,
        status: AgentStatus,
        error_message: Optional[str] = None,
    ):
        """Update agent status."""
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        agent.status = status
        
        if status == AgentStatus.RUNNING and not agent.start_time:
            agent.start_time = datetime.utcnow().isoformat()
        
        if status in [AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.CANCELLED]:
            agent.end_time = datetime.utcnow().isoformat()
        
        if error_message:
            agent.error_message = error_message

        self.save_agent(agent)

    def save_pid(self, agent_id: str, pid: int):
        """Save agent PID."""
        pid_file = self.pids_dir / f"{agent_id}.pid"
        with open(pid_file, 'w') as f:
            f.write(str(pid))
        
        # Update agent state
        agent = self.get_agent(agent_id)
        if agent:
            agent.pid = pid
            self.save_agent(agent)

    def get_pid(self, agent_id: str) -> Optional[int]:
        """Get agent PID if it exists."""
        pid_file = self.pids_dir / f"{agent_id}.pid"
        if not pid_file.exists():
            return None
        
        with open(pid_file, 'r') as f:
            return int(f.read().strip())

    def cleanup_pid(self, agent_id: str):
        """Remove PID file."""
        pid_file = self.pids_dir / f"{agent_id}.pid"
        if pid_file.exists():
            pid_file.unlink()

    def get_stats(self) -> Dict[str, int]:
        """Get overall statistics."""
        all_agents = self.list_agents()
        
        stats = {
            "total": len(all_agents),
            "pending": sum(1 for a in all_agents if a.status == AgentStatus.PENDING),
            "running": sum(1 for a in all_agents if a.status == AgentStatus.RUNNING),
            "completed": sum(1 for a in all_agents if a.status == AgentStatus.COMPLETED),
            "failed": sum(1 for a in all_agents if a.status == AgentStatus.FAILED),
            "cancelled": sum(1 for a in all_agents if a.status == AgentStatus.CANCELLED),
        }
        
        return stats
