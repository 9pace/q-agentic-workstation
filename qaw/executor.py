"""
Agent executor for Q Agentic Workstation.

Handles spawning and managing Q CLI agent processes.
"""

import subprocess
import signal
import psutil
import os
import threading
import time
from pathlib import Path
from typing import Optional, List, Dict
from .state import StateManager, AgentState, AgentStatus
import logging


logger = logging.getLogger(__name__)


class AgentExecutor:
    """Executes and manages Q CLI agents."""

    def __init__(self, state_manager: StateManager):
        """
        Initialize executor.

        Args:
            state_manager: State manager instance
        """
        self.state = state_manager
        self._keepalive_threads: Dict[str, threading.Thread] = {}  # Track keep-alive threads
        self._keepalive_active: Dict[str, bool] = {}  # Control flags for threads

    def spawn_agent(
        self,
        agent: AgentState,
        no_interactive: bool = True,
        trust_all_tools: bool = False,
        additional_args: Optional[List[str]] = None,
        autopilot: bool = False,
    ) -> int:
        """
        Spawn a Q CLI agent process.

        Args:
            agent: Agent state object
            no_interactive: Run in non-interactive mode
            trust_all_tools: Trust all tools without confirmation
            additional_args: Additional arguments to pass to q chat
            autopilot: If True, enable long-running mode with keep-alive

        Returns:
            Process ID of spawned agent

        Raises:
            RuntimeError: If agent spawn fails
        """
        # Build q chat command
        cmd = ["q", "chat", "--agent", agent.agent_name]

        if no_interactive:
            cmd.append("--no-interactive")

        if trust_all_tools:
            cmd.append("--trust-all-tools")

        if additional_args:
            cmd.extend(additional_args)

        # Prepare log file
        log_file = Path(agent.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Spawning agent {agent.id} ({agent.agent_name})")
        logger.debug(f"Command: {' '.join(cmd)}")
        logger.debug(f"Task: {agent.task_description}")
        logger.debug(f"Log file: {agent.log_file}")

        try:
            # Open log file for writing
            log_fd = open(log_file, 'w')

            # Spawn process with task description as stdin
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=log_fd,
                stderr=subprocess.STDOUT,
                cwd=os.getcwd(),
                text=True,
            )

            # Send task description to stdin
            try:
                process.stdin.write(agent.task_description + "\n")
                process.stdin.flush()
                process.stdin.close()
            except Exception as e:
                logger.error(f"Failed to write task to stdin: {e}")
                process.kill()
                raise

            # Save PID
            self.state.save_pid(agent.id, process.pid)

            # Update agent status to running
            self.state.update_agent_status(agent.id, AgentStatus.RUNNING)

            logger.info(f"Agent {agent.id} spawned successfully (PID: {process.pid})")
            
            # Start keep-alive thread if autopilot mode
            if autopilot:
                self._start_keepalive(agent.id, process.pid)
                logger.info(f"Autopilot mode enabled for agent {agent.id}")

            return process.pid

        except Exception as e:
            logger.error(f"Failed to spawn agent {agent.id}: {e}")
            self.state.update_agent_status(
                agent.id,
                AgentStatus.FAILED,
                error_message=str(e)
            )
            raise RuntimeError(f"Failed to spawn agent: {e}")

    def check_agent_status(self, agent_id: str) -> Optional[AgentStatus]:
        """
        Check if an agent is still running.

        Args:
            agent_id: Agent ID

        Returns:
            Current agent status, or None if agent not found
        """
        agent = self.state.get_agent(agent_id)
        if not agent:
            return None

        # If already in terminal state, return current status
        if agent.status in [AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.CANCELLED]:
            return agent.status

        # Check if process is still running
        if agent.pid:
            if self._is_process_running(agent.pid):
                return AgentStatus.RUNNING
            else:
                # Process ended, check exit code via log
                self._update_completed_agent(agent)
                agent = self.state.get_agent(agent_id)  # Reload
                return agent.status if agent else None

        return agent.status

    def _is_process_running(self, pid: int) -> bool:
        """Check if process with given PID is running."""
        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            return False

    def _update_completed_agent(self, agent: AgentState):
        """
        Update agent status when process completes.

        Checks log file for errors to determine success/failure.
        """
        # Check log file for errors
        log_file = Path(agent.log_file)
        if log_file.exists():
            with open(log_file, 'r') as f:
                log_content = f.read()

            # Simple heuristic: check for error indicators
            error_indicators = ['error:', 'failed:', 'exception:', 'traceback']
            has_error = any(indicator in log_content.lower() for indicator in error_indicators)

            if has_error:
                self.state.update_agent_status(
                    agent.id,
                    AgentStatus.FAILED,
                    error_message="Agent process completed with errors (check logs)"
                )
            else:
                self.state.update_agent_status(agent.id, AgentStatus.COMPLETED)
        else:
            # No log file, assume success
            self.state.update_agent_status(agent.id, AgentStatus.COMPLETED)

        # Cleanup PID file
        self.state.cleanup_pid(agent.id)

    def stop_agent(self, agent_id: str, force: bool = False) -> bool:
        """
        Stop a running agent.

        Args:
            agent_id: Agent ID
            force: If True, use SIGKILL instead of SIGTERM

        Returns:
            True if agent was stopped, False otherwise
        """
        agent = self.state.get_agent(agent_id)
        if not agent or not agent.pid:
            logger.warning(f"Cannot stop agent {agent_id}: no PID found")
            return False

        if not self._is_process_running(agent.pid):
            logger.info(f"Agent {agent_id} is not running")
            self._update_completed_agent(agent)
            return False

        try:
            sig = signal.SIGKILL if force else signal.SIGTERM
            os.kill(agent.pid, sig)
            logger.info(f"Sent {'SIGKILL' if force else 'SIGTERM'} to agent {agent_id} (PID: {agent.pid})")

            # Update status
            self.state.update_agent_status(agent.id, AgentStatus.CANCELLED)
            self.state.cleanup_pid(agent.id)

            return True

        except ProcessLookupError:
            logger.warning(f"Process {agent.pid} not found")
            self._update_completed_agent(agent)
            return False
        except Exception as e:
            logger.error(f"Failed to stop agent {agent_id}: {e}")
            return False
    
    def _start_keepalive(self, agent_id: str, pid: int):
        """
        Start a keep-alive thread for autopilot mode.
        
        Periodically checks if agent is still running and performs
        minimal activity to prevent timeout.
        
        Args:
            agent_id: Agent ID
            pid: Process ID to monitor
        """
        self._keepalive_active[agent_id] = True
        
        def keepalive_loop():
            """Keep-alive thread main loop."""
            interval = 30  # Check every 30 seconds
            
            while self._keepalive_active.get(agent_id, False):
                try:
                    # Check if process is still alive
                    if not self._is_process_running(pid):
                        logger.info(f"Keep-alive: Agent {agent_id} process ended")
                        self._keepalive_active[agent_id] = False
                        break
                    
                    # Process is alive - log status
                    agent = self.state.get_agent(agent_id)
                    if agent:
                        logger.debug(f"Keep-alive ping: Agent {agent_id} still running")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Keep-alive error for agent {agent_id}: {e}")
                    self._keepalive_active[agent_id] = False
                    break
            
            # Cleanup
            logger.info(f"Keep-alive thread stopping for agent {agent_id}")
            agent = self.state.get_agent(agent_id)
            if agent:
                self._update_completed_agent(agent)
        
        # Start thread
        thread = threading.Thread(target=keepalive_loop, daemon=True, name=f"keepalive-{agent_id}")
        thread.start()
        self._keepalive_threads[agent_id] = thread
        logger.info(f"Started keep-alive thread for agent {agent_id}")
    
    def stop_keepalive(self, agent_id: str):
        """
        Stop the keep-alive thread for an agent.
        
        Args:
            agent_id: Agent ID
        """
        if agent_id in self._keepalive_active:
            self._keepalive_active[agent_id] = False
            logger.info(f"Stopping keep-alive for agent {agent_id}")
            
            # Wait for thread to finish (with timeout)
            thread = self._keepalive_threads.get(agent_id)
            if thread and thread.is_alive():
                thread.join(timeout=5)
            
            # Cleanup
            self._keepalive_threads.pop(agent_id, None)
            self._keepalive_active.pop(agent_id, None)

    def wait_for_agent(self, agent_id: str, timeout: Optional[int] = None) -> AgentStatus:
        """
        Wait for agent to complete.

        Args:
            agent_id: Agent ID
            timeout: Timeout in seconds (None = wait forever)

        Returns:
            Final agent status
        """
        agent = self.state.get_agent(agent_id)
        if not agent or not agent.pid:
            raise ValueError(f"Agent {agent_id} not found or has no PID")

        try:
            process = psutil.Process(agent.pid)
            process.wait(timeout=timeout)
        except psutil.TimeoutExpired:
            logger.warning(f"Agent {agent_id} did not complete within {timeout}s")
            return AgentStatus.RUNNING
        except psutil.NoSuchProcess:
            logger.info(f"Agent {agent_id} process already completed")

        # Update and return final status
        self._update_completed_agent(agent)
        agent = self.state.get_agent(agent_id)
        return agent.status if agent else AgentStatus.FAILED

    def cleanup_stale_agents(self):
        """
        Clean up agents that are marked as running but process has died.
        """
        running_agents = self.state.list_agents(status=AgentStatus.RUNNING)

        for agent in running_agents:
            if agent.pid and not self._is_process_running(agent.pid):
                logger.info(f"Cleaning up stale agent {agent.id}")
                self._update_completed_agent(agent)

    def get_agent_output(self, agent_id: str, tail_lines: Optional[int] = None) -> str:
        """
        Get agent log output.

        Args:
            agent_id: Agent ID
            tail_lines: If specified, return only last N lines

        Returns:
            Log content
        """
        agent = self.state.get_agent(agent_id)
        if not agent or not agent.log_file:
            return ""

        log_file = Path(agent.log_file)
        if not log_file.exists():
            return ""

        with open(log_file, 'r') as f:
            if tail_lines:
                lines = f.readlines()
                return ''.join(lines[-tail_lines:])
            return f.read()
