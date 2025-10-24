"""
Q Agentic Workstation CLI.

Main command-line interface for managing agent workflows.
"""

import click
import sys
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
from .state import StateManager, AgentStatus, TaskPriority
from .executor import AgentExecutor
from . import __version__


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_workspace_dir() -> Path:
    """Get or create workspace directory (.qaw in current directory)."""
    workspace = Path.cwd() / ".qaw"
    if not workspace.exists():
        workspace.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created workspace directory: {workspace}")
    return workspace


def get_state_manager() -> StateManager:
    """Get state manager for current workspace."""
    return StateManager(get_workspace_dir())


def get_executor() -> AgentExecutor:
    """Get executor for current workspace."""
    return AgentExecutor(get_state_manager())


def format_duration(start_time: Optional[str], end_time: Optional[str] = None) -> str:
    """Format duration between two timestamps."""
    if not start_time:
        return "N/A"
    
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time) if end_time else datetime.utcnow()
        duration = end - start
        
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    except:
        return "N/A"


@click.group()
@click.version_option(version=__version__)
def cli():
    """Q Agentic Workstation - Parallel agent execution for hyperdeveloping."""
    pass


@cli.command()
@click.argument('task_description')
@click.option('--agent', default='orchestrator-agent', help='Agent to use')
@click.option('--priority', type=click.Choice(['low', 'medium', 'high', 'critical']), 
              default='medium', help='Task priority')
@click.option('--name', default=None, help='Custom agent name (auto-generated if not provided)')
@click.option('--trust-all-tools', is_flag=True, help='Trust all tools without confirmation')
@click.option('--autopilot', is_flag=True, help='Enable autopilot mode (no timeout, keep-alive)')
@click.option('--wait', is_flag=True, help='Wait for agent to complete')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def submit(task_description: str, agent: str, priority: str, name: Optional[str],
           trust_all_tools: bool, autopilot: bool, wait: bool, verbose: bool):
    """Submit a new task to be executed by an agent."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        state = get_state_manager()
        executor = get_executor()
        
        # Create task
        task_priority = TaskPriority(priority)
        task = state.create_task(task_description, priority=task_priority)
        
        # Create agent
        agent_state = state.create_agent(
            agent_name=agent,
            task_id=task.id,
            task_description=task_description,
            custom_name=name,
        )
        
        # Update task with assigned agent
        task.assigned_agent_id = agent_state.id
        task.status = AgentStatus.RUNNING
        task.started_at = datetime.utcnow().isoformat()
        state.save_task(task)
        
        click.echo(f"✓ Created task: {task.id}")
        if agent_state.semantic_name:
            click.echo(f"✓ Spawning agent: {agent_state.semantic_name} ({agent})")
        else:
            click.echo(f"✓ Spawning agent: {agent_state.id} ({agent})")
        
        if autopilot:
            click.secho("🤖 Autopilot mode enabled - agent will run until completion", fg='cyan')
        
        # Spawn agent
        pid = executor.spawn_agent(
            agent_state, 
            trust_all_tools=trust_all_tools,
            autopilot=autopilot,
        )
        
        click.echo(f"✓ Agent running (PID: {pid})")
        click.echo(f"\nLog file: {agent_state.log_file}")
        click.echo(f"Result dir: {agent_state.result_dir}")
        click.echo(f"\nMonitor with: qaw status {agent_state.id}")
        click.echo(f"View logs with: qaw logs {agent_state.id}")
        
        if wait:
            click.echo(f"\nWaiting for agent to complete...")
            final_status = executor.wait_for_agent(agent_state.id)
            
            if final_status == AgentStatus.COMPLETED:
                click.secho(f"\n✓ Agent completed successfully", fg='green', bold=True)
                sys.exit(0)
            else:
                click.secho(f"\n✗ Agent {final_status.value}", fg='red', bold=True)
                sys.exit(1)
        
    except Exception as e:
        logger.error(f"Failed to submit task: {e}")
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
@click.argument('agent_id', required=False)
@click.option('--all', 'show_all', is_flag=True, help='Show all agents (not just recent)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def status(agent_id: Optional[str], show_all: bool, verbose: bool):
    """Show status of agents."""
    try:
        state = get_state_manager()
        executor = get_executor()
        
        # Cleanup stale agents
        executor.cleanup_stale_agents()
        
        if agent_id:
            # Show specific agent
            agent = state.get_agent(agent_id)
            if not agent:
                click.secho(f"Agent {agent_id} not found", fg='red', err=True)
                sys.exit(1)
            
            # Refresh status
            current_status = executor.check_agent_status(agent_id)
            agent = state.get_agent(agent_id)  # Reload
            
            status_color = {
                AgentStatus.PENDING: 'yellow',
                AgentStatus.RUNNING: 'blue',
                AgentStatus.COMPLETED: 'green',
                AgentStatus.FAILED: 'red',
                AgentStatus.CANCELLED: 'yellow',
            }.get(agent.status, 'white')
            
            click.secho(f"\n{agent.id}", bold=True)
            click.secho(f"Status: {agent.status.value.upper()}", fg=status_color)
            click.echo(f"Agent: {agent.agent_name}")
            click.echo(f"Task: {agent.task_description}")
            
            if agent.pid:
                click.echo(f"PID: {agent.pid}")
            
            if agent.start_time:
                duration = format_duration(agent.start_time, agent.end_time)
                click.echo(f"Duration: {duration}")
            
            if agent.error_message:
                click.secho(f"Error: {agent.error_message}", fg='red')
            
            click.echo(f"\nLog: {agent.log_file}")
            click.echo(f"Results: {agent.result_dir}")
            
            if verbose and agent.log_file:
                click.echo(f"\n--- Recent Log Output ---")
                output = executor.get_agent_output(agent_id, tail_lines=20)
                if output:
                    click.echo(output)
                else:
                    click.echo("(no output yet)")
        else:
            # Show all agents summary
            stats = state.get_stats()
            agents = state.list_agents()
            
            if not show_all:
                # Only show recent agents
                agents = agents[:10]
            
            click.echo(f"\n{'='*60}")
            click.echo(f"Q Agentic Workstation Status")
            click.echo(f"{'='*60}\n")
            
            click.echo(f"Total: {stats['total']} | ", nl=False)
            click.secho(f"Running: {stats['running']}", fg='blue', nl=False)
            click.echo(f" | Pending: {stats['pending']} | ", nl=False)
            click.secho(f"Completed: {stats['completed']}", fg='green', nl=False)
            click.echo(f" | ", nl=False)
            click.secho(f"Failed: {stats['failed']}", fg='red')
            
            if agents:
                click.echo(f"\n{'Agent ID':<15} {'Status':<12} {'Agent':<20} {'Duration':<12} {'Task':<}")
                click.echo(f"{'-'*60}")
                
                for agent in agents:
                    status_emoji = {
                        AgentStatus.PENDING: '⏳',
                        AgentStatus.RUNNING: '🔄',
                        AgentStatus.COMPLETED: '✓',
                        AgentStatus.FAILED: '✗',
                        AgentStatus.CANCELLED: '⊘',
                    }.get(agent.status, '?')
                    
                    duration = format_duration(agent.start_time, agent.end_time)
                    task_preview = agent.task_description[:40] + '...' if len(agent.task_description) > 40 else agent.task_description
                    
                    agent_id_str = f"{status_emoji} {agent.id[:12]}"
                    
                    click.echo(f"{agent_id_str:<15} {agent.status.value:<12} {agent.agent_name[:18]:<20} {duration:<12} {task_preview}")
            else:
                click.echo("\nNo agents found. Submit a task with: qaw submit \"your task\"")
            
            click.echo()
    
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
@click.argument('agent_id')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.option('--lines', '-n', type=int, default=50, help='Number of lines to show')
def logs(agent_id: str, follow: bool, lines: int):
    """View agent logs."""
    try:
        state = get_state_manager()
        executor = get_executor()
        
        agent = state.get_agent(agent_id)
        if not agent:
            click.secho(f"Agent {agent_id} not found", fg='red', err=True)
            sys.exit(1)
        
        log_file = Path(agent.log_file)
        if not log_file.exists():
            click.echo("(no log output yet)")
            return
        
        if follow:
            # Follow mode - use tail -f
            import subprocess
            try:
                subprocess.run(['tail', '-f', str(log_file)])
            except KeyboardInterrupt:
                pass
        else:
            # Show last N lines
            output = executor.get_agent_output(agent_id, tail_lines=lines)
            click.echo(output)
    
    except Exception as e:
        logger.error(f"Failed to view logs: {e}")
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
@click.argument('agent_id')
@click.option('--force', is_flag=True, help='Force kill (SIGKILL)')
def stop(agent_id: str, force: bool):
    """Stop a running agent."""
    try:
        executor = get_executor()
        
        if executor.stop_agent(agent_id, force=force):
            click.secho(f"✓ Agent {agent_id} stopped", fg='green')
        else:
            click.secho(f"Agent {agent_id} is not running or already stopped", fg='yellow')
    
    except Exception as e:
        logger.error(f"Failed to stop agent: {e}")
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
def init():
    """Initialize workspace in current directory."""
    try:
        workspace = get_workspace_dir()
        state = get_state_manager()
        
        click.echo(f"✓ Initialized Q Agentic Workstation in: {workspace}")
        click.echo(f"\nWorkspace structure:")
        click.echo(f"  .qaw/")
        click.echo(f"    state/     - Agent and task state")
        click.echo(f"    logs/      - Agent log files")
        click.echo(f"    results/   - Agent output files")
        click.echo(f"    pids/      - Process IDs")
        click.echo(f"\nReady to submit tasks!")
        click.echo(f"Try: qaw submit \"Create a hello world React component\"")
    
    except Exception as e:
        logger.error(f"Failed to initialize workspace: {e}")
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
def cleanup():
    """Clean up completed agents and old logs."""
    try:
        executor = get_executor()
        
        click.echo("Cleaning up stale agents...")
        executor.cleanup_stale_agents()
        
        click.secho("✓ Cleanup complete", fg='green')
    
    except Exception as e:
        logger.error(f"Failed to cleanup: {e}")
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
@click.argument('message', required=False)
@click.option('--execute', '-e', is_flag=True, help='Auto-execute the plan')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def chat(message: Optional[str], execute: bool, verbose: bool):
    """
    Chat with manager agent for natural language task orchestration.
    
    If no message provided, enters interactive mode.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        import asyncio
        from .manager import ManagerSession
        from .context import ContextManager
        
        workspace = get_workspace_dir()
        
        # Initialize context if needed
        context_mgr = ContextManager(workspace)
        context = context_mgr.get_context()
        if not context:
            click.secho("⚠️  Analyzing project for first time...", fg='cyan')
            context = context_mgr.initialize()
            click.secho("✓ Project context initialized\n", fg='green')
            
            # Show context summary
            click.echo(f"Detected: {', '.join(context.tech_stack.languages)}")
            if context.tech_stack.frameworks:
                click.echo(f"Frameworks: {', '.join(context.tech_stack.frameworks)}")
            click.echo(f"Architecture: {context.architecture}\n")
        
        # Create session
        session = ManagerSession(workspace)
        
        if message:
            # Single message mode
            async def run_single():
                click.secho(f"👤 You: {message}", fg='white')
                click.echo()
                
                response = await session.send_message(message)
                click.secho(f"🤖 Manager:", fg='cyan', bold=True)
                click.echo(response)
                click.echo()
                
                if execute:
                    click.secho("🚀 Executing plan...", fg='green')
                    click.echo()
                    
                    def progress_callback(increment):
                        status = increment.status.value
                        emoji = {"in_progress": "🔄", "verifying": "🔍", "completed": "✓", "failed": "✗"}.get(status, "⏳")
                        click.echo(f"{emoji} {increment.description} [{status}]")
                    
                    success = await session.execute_current_plan(progress_callback)
                    
                    if success:
                        click.secho("\n✓ All increments completed successfully!", fg='green', bold=True)
                    else:
                        click.secho("\n✗ Plan execution failed", fg='red', bold=True)
                        sys.exit(1)
            
            asyncio.run(run_single())
        
        else:
            # Interactive mode
            click.secho("💬  QAW Manager Chat (interactive mode)", fg='cyan', bold=True)
            click.echo("Type your request, 'status' for current plan, 'execute' to run plan, or 'quit' to exit\n")
            
            async def run_interactive():
                while True:
                    try:
                        user_input = click.prompt('👤 You', type=str)
                        
                        if user_input.lower() in ['quit', 'exit', 'q']:
                            click.echo("Goodbye!")
                            break
                        
                        if user_input.lower() == 'status':
                            status = session.get_status_summary()
                            click.echo(f"\n{status}\n")
                            continue
                        
                        if user_input.lower() in ['execute', 'exec', 'run']:
                            if not session.current_plan:
                                click.secho("⚠️  No plan to execute. Send a request first.", fg='yellow')
                                continue
                            
                            click.secho("🚀 Executing plan...", fg='green')
                            
                            def progress_callback(increment):
                                status = increment.status.value
                                emoji = {"in_progress": "🔄", "verifying": "🔍", "completed": "✓", "failed": "✗"}.get(status, "⏳")
                                click.echo(f"{emoji} {increment.description} [{status}]")
                            
                            success = await session.execute_current_plan(progress_callback)
                            
                            if success:
                                click.secho("\n✓ All increments completed!", fg='green', bold=True)
                            else:
                                click.secho("\n✗ Plan execution failed", fg='red', bold=True)
                            
                            click.echo()
                            continue
                        
                        # Process as manager request
                        response = await session.send_message(user_input)
                        click.echo()
                        click.secho("🤖 Manager:", fg='cyan', bold=True)
                        click.echo(response)
                        click.echo()
                    
                    except (KeyboardInterrupt, EOFError):
                        click.echo("\nGoodbye!")
                        break
            
            asyncio.run(run_interactive())
    
    except Exception as e:
        logger.error(f"Manager chat error: {e}")
        click.secho(f"Error: {e}", fg='red', err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
def dashboard():
    """Launch interactive dashboard (TUI)."""
    try:
        from .dashboard import run_dashboard
        
        workspace = get_workspace_dir()
        
        # Check if workspace exists
        if not (workspace / "state").exists():
            click.secho("Workspace not initialized. Run 'qaw init' first.", fg='yellow', err=True)
            sys.exit(1)
        
        click.echo("Launching dashboard...")
        click.echo("Press 'q' to quit, '?' for help")
        click.echo()
        
        run_dashboard(workspace)
    
    except ImportError:
        click.secho("Dashboard requires 'textual'. Install with: pip install textual", fg='red', err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to launch dashboard: {e}")
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()
