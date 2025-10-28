"""
Q Agentic Workstation Dashboard - Hybrid Interface.

Combines Manager-First chat interface with Interactive Agent Table.
Production-quality terminal UI with both natural language planning and live agent monitoring.
"""

from textual.app import App, ComposeResult
from textual.widgets import (
    Header,
    Footer,
    Static,
    DataTable,
    Button,
    Input,
    TabbedContent,
    TabPane,
)
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual import on
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
import asyncio

from .state import StateManager, AgentStatus, AgentState
from .executor import AgentExecutor
from .manager import ManagerSession, ExecutionPlan, Increment, IncrementStatus
from .context import ContextManager


class ChatPanel(Static):
    """Chat conversation display for Manager interface."""

    messages: reactive[List] = reactive(list, init=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = []

    def render(self) -> str:
        """Render chat messages."""
        if not self.messages:
            return """
[bold cyan]💬 Manager Chat[/bold cyan]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[dim italic]Welcome! I'm your Manager Agent.
Describe what you'd like to build, and I'll break it down
into small, testable increments.[/dim italic]

[bold]What would you like to work on today?[/bold]
"""

        chat_text = "[bold cyan]💬 Manager Chat[/bold cyan]\n"
        chat_text += "━" * 42 + "\n\n"

        # Show last 8 messages to save space
        for msg in self.messages[-8:]:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                chat_text += f"[bold white]👤 You:[/bold white]\n{content}\n\n"
            else:
                chat_text += f"[bold cyan]🤖 Manager:[/bold cyan]\n{content}\n\n"

        return chat_text

    def add_message(self, role: str, content: str):
        """Add a message to the chat."""
        self.messages.append({"role": role, "content": content})
        self.refresh()


class ExecutionPlanPanel(Static):
    """Display current execution plan with increments."""

    plan: reactive[Optional[ExecutionPlan]] = reactive(None)

    def render(self) -> str:
        """Render execution plan."""
        if not self.plan:
            return """
[bold green]📋 Execution Plan[/bold green]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[dim]No active plan[/dim]
"""

        output = f"[bold green]📋 Execution Plan[/bold green]\n"
        output += "━" * 42 + "\n\n"
        output += f"[bold]Task:[/bold] {self.plan.user_request}\n\n"
        output += f"[bold]Increments:[/bold] {len(self.plan.increments)} | "
        output += f"[bold]Est. Lines:[/bold] ~{self.plan.total_estimated_lines}\n\n"

        # Show increments with status
        for i, inc in enumerate(self.plan.increments, 1):
            status_emoji = {
                IncrementStatus.PENDING: "⏳",
                IncrementStatus.IN_PROGRESS: "🔄",
                IncrementStatus.VERIFYING: "🔍",
                IncrementStatus.COMPLETED: "✅",
                IncrementStatus.FAILED: "❌",
                IncrementStatus.RETRY: "🔁",
            }.get(inc.status, "?")

            status_color = {
                IncrementStatus.PENDING: "yellow",
                IncrementStatus.IN_PROGRESS: "blue",
                IncrementStatus.VERIFYING: "cyan",
                IncrementStatus.COMPLETED: "green",
                IncrementStatus.FAILED: "red",
                IncrementStatus.RETRY: "yellow",
            }.get(inc.status, "white")

            output += f"{i}. {status_emoji} [{status_color}]{inc.description}[/{status_color}]\n"
            output += f"   [dim]Agent: {inc.agent_type} | ~{inc.estimated_lines} lines"

            if inc.retry_count > 0:
                output += f" | Retry: {inc.retry_count}/{inc.max_retries}"

            output += "[/dim]\n"

            if inc.verification_feedback:
                output += f"   [yellow]⚠️  {inc.verification_feedback}[/yellow]\n"

        return output


class StatsPanel(Static):
    """Display overall agent statistics."""

    stats = reactive(
        {
            "total": 0,
            "running": 0,
            "pending": 0,
            "completed": 0,
            "failed": 0,
        }
    )

    def render(self) -> str:
        """Render statistics."""
        s = self.stats
        return f"""
[bold magenta]📊 Agent Stats[/bold magenta]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total:       [bold]{s['total']:>3}[/bold]
🔄 Running:  [blue]{s['running']:>3}[/blue]
⏳ Pending:  [yellow]{s['pending']:>3}[/yellow]
✅ Done:     [green]{s['completed']:>3}[/green]
❌ Failed:   [red]{s['failed']:>3}[/red]
"""


class AgentDetailPanel(Static):
    """Display detailed agent information."""

    agent_data = reactive(None)

    def render(self) -> str:
        """Render agent details."""
        if not self.agent_data:
            return """
[bold cyan]🔍 Agent Details[/bold cyan]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[dim]Select an agent to view details[/dim]
"""

        a = self.agent_data
        status_color = {
            "pending": "yellow",
            "running": "blue",
            "completed": "green",
            "failed": "red",
            "cancelled": "yellow",
        }.get(a.status.value, "white")

        status_emoji = {
            "pending": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "⊘",
        }.get(a.status.value, "?")

        duration = self._format_duration(a.start_time, a.end_time)

        # Display semantic name if available
        display_name = a.semantic_name or a.id

        detail = f"""
[bold cyan]🔍 Agent Details[/bold cyan]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[bold]Name:[/bold]        {display_name}
[bold]Status:[/bold]      [{status_color}]{status_emoji} {a.status.value.upper()}[/{status_color}]
[bold]Agent:[/bold]       {a.agent_name}
[bold]Duration:[/bold]    {duration}
"""

        if a.pid:
            detail += f"[bold]PID:[/bold]         {a.pid}\n"

        detail += f"""
[bold]Task:[/bold]
  {a.task_description}

[bold]Files:[/bold]
  Log:     {Path(a.log_file).name}
  Results: {Path(a.result_dir).name}
"""

        if a.error_message:
            detail += f"\n[bold red]Error:[/bold red]\n  {a.error_message}\n"

        return detail

    def _format_duration(self, start: Optional[str], end: Optional[str]) -> str:
        """Format duration."""
        if not start:
            return "N/A"

        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end) if end else datetime.utcnow()
            delta = end_dt - start_dt

            total_seconds = int(delta.total_seconds())
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


class QuickActionsPanel(Static):
    """Quick action buttons for agent control."""

    selected_agent = reactive(None)

    def compose(self) -> ComposeResult:
        """Create action buttons."""
        yield Button("🔄 Refresh", id="refresh-btn", variant="primary")
        yield Button("🗑️ Cleanup", id="cleanup-btn", variant="default")
        yield Button("⏸️ Stop Agent", id="stop-btn", variant="warning", disabled=True)
        yield Button("❌ Kill Agent", id="kill-btn", variant="error", disabled=True)
        yield Button("📋 View Logs", id="logs-btn", variant="default", disabled=True)
        yield Button("❓ Help", id="help-btn", variant="default")

    def watch_selected_agent(self, agent: Optional[AgentState]) -> None:
        """Update button states based on selected agent."""
        if not agent:
            self.query_one("#stop-btn", Button).disabled = True
            self.query_one("#kill-btn", Button).disabled = True
            self.query_one("#logs-btn", Button).disabled = True
            return

        # Enable/disable based on agent status
        can_stop = agent.status == AgentStatus.RUNNING
        has_logs = agent.log_file and Path(agent.log_file).exists()

        self.query_one("#stop-btn", Button).disabled = not can_stop
        self.query_one("#kill-btn", Button).disabled = not can_stop
        self.query_one("#logs-btn", Button).disabled = not has_logs


class HybridDashboardApp(App):
    """Q Agentic Workstation - Hybrid Dashboard with Manager + Agent Table."""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 3;
        grid-gutter: 1;
        padding: 1;
    }
    
    /* Manager Tab - spans full width when active */
    #manager-tab {
        column-span: 3;
        row-span: 3;
    }
    
    /* Agent Monitor Tab - 3x3 grid layout */
    #monitor-tab {
        column-span: 3;
        row-span: 3;
        layout: grid;
        grid-size: 3 3;
        grid-gutter: 1;
    }
    
    /* Stats panel - top left */
    #stats {
        column-span: 1;
        row-span: 1;
        border: solid magenta;
        padding: 1;
    }
    
    /* Agent table - spans 2 columns, 2 rows (main focus) */
    #agent-table {
        column-span: 2;
        row-span: 2;
        border: solid blue;
        padding: 1;
    }
    
    /* Agent details - bottom left */
    #agent-details {
        column-span: 1;
        row-span: 2;
        border: solid cyan;
        padding: 1;
    }
    
    /* Quick actions - bottom right */
    #quick-actions {
        column-span: 2;
        row-span: 1;
        border: solid green;
        padding: 1;
        layout: horizontal;
    }
    
    /* Manager interface layout */
    #chat-container {
        layout: vertical;
        height: 100%;
    }
    
    #chat {
        height: 1fr;
        margin-bottom: 1;
        overflow-y: auto;
    }
    
    #chat-input-container {
        height: auto;
        layout: horizontal;
    }
    
    #chat-input {
        width: 1fr;
    }
    
    #send-button {
        width: auto;
        margin-left: 1;
    }
    
    #execute-button {
        width: auto;
        margin-left: 1;
    }
    
    #plan-panel {
        height: 1fr;
        border: solid green;
        padding: 1;
        overflow-y: auto;
    }
    
    DataTable {
        height: 100%;
    }
    
    Button {
        margin-right: 1;
        min-width: 12;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+r", "refresh", "Refresh"),
        ("s", "stop_agent", "Stop Agent"),
        ("k", "kill_agent", "Kill Agent"),
        ("l", "view_logs", "View Logs"),
        ("c", "cleanup", "Cleanup"),
        ("?", "help", "Help"),
        ("1", "switch_to_manager", "Manager"),
        ("2", "switch_to_monitor", "Monitor"),
    ]

    TITLE = "Q Agentic Workstation"
    SUB_TITLE = "Hybrid Interface - Manager + Agent Monitor"

    def __init__(self, workspace_dir: Path):
        """Initialize dashboard."""
        super().__init__()
        self.workspace_dir = workspace_dir
        self.state = StateManager(workspace_dir)
        self.executor = AgentExecutor(self.state)
        self.context_manager = ContextManager(workspace_dir)
        self.update_interval = 0.5  # Fast refresh for responsiveness

        # Manager session
        self.manager_session: Optional[ManagerSession] = None
        self.executing_plan = False

        # Agent monitoring
        self.selected_agent: Optional[AgentState] = None

    def compose(self) -> ComposeResult:
        """Create application layout."""
        yield Header()

        with TabbedContent(initial="manager"):
            # Manager Tab - Natural language interface
            with TabPane("Manager", id="manager-tab"):
                with Horizontal():
                    # Left side - Chat interface
                    with Vertical(id="chat-container"):
                        yield ChatPanel(id="chat")
                        with Horizontal(id="chat-input-container"):
                            yield Input(
                                placeholder="Describe your task... (e.g., 'Add a user login feature')",
                                id="chat-input",
                            )
                            yield Button("🚀 Send", id="send-button", variant="primary")
                            yield Button(
                                "▶️ Execute",
                                id="execute-button",
                                variant="success",
                                disabled=True,
                            )

                    # Right side - Execution plan
                    yield ExecutionPlanPanel(id="plan-panel")

            # Monitor Tab - Agent table interface
            with TabPane("Monitor", id="monitor-tab"):
                # Stats panel (top left)
                yield StatsPanel(id="stats")

                # Agent table (main area - 2x2)
                with Container(id="agent-table"):
                    yield DataTable(id="agents-datatable")

                # Agent details (bottom left)
                yield AgentDetailPanel(id="agent-details")

                # Quick actions (bottom right)
                with Container(id="quick-actions"):
                    yield QuickActionsPanel(id="actions-panel")

        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        # Initialize manager session
        self.run_worker(self._initialize_manager(), exclusive=True)

        # Set up agent table
        self._setup_agent_table()

        # Start periodic refresh
        self.set_interval(self.update_interval, self.refresh_data)

        # Initial refresh
        self.refresh_data()

        # Focus on input
        self.query_one("#chat-input", Input).focus()

    def _setup_agent_table(self) -> None:
        """Set up the agent DataTable."""
        table = self.query_one("#agents-datatable", DataTable)
        table.add_columns("Status", "Name", "Agent", "Duration", "Task")
        table.cursor_type = "row"
        table.zebra_stripes = True

    async def _initialize_manager(self):
        """Initialize manager session asynchronously."""
        try:
            # Get or initialize context
            context = self.context_manager.get_context()
            if not context:
                self.notify("Initializing project context...", severity="information")
                context = self.context_manager.initialize()
                self.notify("Project context ready", severity="success")

            # Create manager session
            self.manager_session = ManagerSession(self.workspace_dir)

            # Add welcome message to chat
            chat_panel = self.query_one("#chat", ChatPanel)
            welcome = f"""Project initialized!
Detected: {', '.join(context.tech_stack.languages)}"""
            if context.tech_stack.frameworks:
                welcome += f"\nFrameworks: {', '.join(context.tech_stack.frameworks)}"
            chat_panel.add_message("manager", welcome)

        except Exception as e:
            self.notify(f"Error initializing manager: {e}", severity="error")

    def refresh_data(self) -> None:
        """Refresh all data from state manager."""
        try:
            # Cleanup stale agents
            self.executor.cleanup_stale_agents()

            # Update statistics
            stats = self.state.get_stats()
            stats_panel = self.query_one("#stats", StatsPanel)
            stats_panel.stats = stats

            # Update agent table
            self._update_agent_table()

            # Update execution plan if active
            if self.manager_session and self.manager_session.current_plan:
                plan_panel = self.query_one("#plan-panel", ExecutionPlanPanel)
                plan_panel.plan = self.manager_session.current_plan
                plan_panel.refresh()

        except Exception:
            pass  # Ignore errors during refresh

    def _update_agent_table(self) -> None:
        """Update the agent table with current data."""
        table = self.query_one("#agents-datatable", DataTable)
        agents = self.state.list_agents()

        # Clear and repopulate table
        table.clear()

        for agent in agents:
            # Status emoji
            status_emoji = {
                AgentStatus.PENDING: "⏳",
                AgentStatus.RUNNING: "🔄",
                AgentStatus.COMPLETED: "✅",
                AgentStatus.FAILED: "❌",
                AgentStatus.CANCELLED: "⊘",
            }.get(agent.status, "?")

            # Name (semantic or short ID)
            name = agent.semantic_name or agent.id[:12]

            # Agent type
            agent_type = agent.agent_name.replace("-agent", "")

            # Duration
            duration = self._format_duration(agent.start_time, agent.end_time)

            # Task preview
            task_preview = agent.task_description[:40]
            if len(agent.task_description) > 40:
                task_preview += "..."

            # Add row with agent ID as key
            table.add_row(
                status_emoji, name, agent_type, duration, task_preview, key=agent.id
            )

    def _format_duration(self, start: Optional[str], end: Optional[str]) -> str:
        """Format duration for table display."""
        if not start:
            return "N/A"

        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end) if end else datetime.utcnow()
            delta = end_dt - start_dt

            total_seconds = int(delta.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            if hours > 0:
                return f"{hours}h{minutes}m"
            elif minutes > 0:
                return f"{minutes}m{seconds}s"
            else:
                return f"{seconds}s"
        except:
            return "N/A"

    # Manager interface event handlers
    @on(Input.Submitted, "#chat-input")
    async def on_chat_submit(self, event: Input.Submitted):
        """Handle chat input submission."""
        await self.send_message(event.value)

    @on(Button.Pressed, "#send-button")
    async def on_send_button(self):
        """Handle send button press."""
        chat_input = self.query_one("#chat-input", Input)
        message = chat_input.value.strip()
        if message:
            await self.send_message(message)

    async def send_message(self, message: str):
        """Send message to manager and update UI."""
        if not self.manager_session:
            self.notify("Manager not ready yet", severity="warning")
            return

        if self.executing_plan:
            self.notify("Plan is currently executing", severity="warning")
            return

        # Clear input
        chat_input = self.query_one("#chat-input", Input)
        chat_input.value = ""

        # Add user message to chat
        chat_panel = self.query_one("#chat", ChatPanel)
        chat_panel.add_message("user", message)

        # Show processing
        self.notify("Processing request...", severity="information")

        # Get response from manager
        try:
            response = await self.manager_session.send_message(message)

            # Add manager response to chat
            chat_panel.add_message("manager", response)

            # Update plan panel
            if self.manager_session.current_plan:
                plan_panel = self.query_one("#plan-panel", ExecutionPlanPanel)
                plan_panel.plan = self.manager_session.current_plan
                plan_panel.refresh()

                # Enable execute button
                execute_btn = self.query_one("#execute-button", Button)
                execute_btn.disabled = False

        except Exception as e:
            self.notify(f"Error: {e}", severity="error")
            chat_panel.add_message("manager", f"Error processing request: {e}")

    @on(Button.Pressed, "#execute-button")
    async def on_execute_button(self):
        """Execute the current plan."""
        if not self.manager_session or not self.manager_session.current_plan:
            self.notify("No plan to execute", severity="warning")
            return

        if self.executing_plan:
            self.notify("Plan is already executing", severity="warning")
            return

        self.executing_plan = True
        execute_btn = self.query_one("#execute-button", Button)
        execute_btn.disabled = True

        chat_panel = self.query_one("#chat", ChatPanel)
        chat_panel.add_message("manager", "🚀 Executing plan...")

        # Execute in background
        self.run_worker(self._execute_plan(), exclusive=False)

    async def _execute_plan(self):
        """Execute plan in background."""
        try:

            def progress_callback(increment):
                # Update plan display
                if self.manager_session and self.manager_session.current_plan:
                    plan_panel = self.query_one("#plan-panel", ExecutionPlanPanel)
                    plan_panel.plan = self.manager_session.current_plan
                    plan_panel.refresh()

            success = await self.manager_session.execute_current_plan(progress_callback)

            chat_panel = self.query_one("#chat", ChatPanel)

            if success:
                chat_panel.add_message(
                    "manager", "✅ All increments completed successfully!"
                )
                self.notify("Plan executed successfully", severity="success")
            else:
                chat_panel.add_message(
                    "manager", "❌ Plan execution failed. Check logs for details."
                )
                self.notify("Plan execution failed", severity="error")

        except Exception as e:
            chat_panel = self.query_one("#chat", ChatPanel)
            chat_panel.add_message("manager", f"❌ Error: {e}")
            self.notify(f"Execution error: {e}", severity="error")

        finally:
            self.executing_plan = False
            execute_btn = self.query_one("#execute-button", Button)
            execute_btn.disabled = True

    # Agent monitor event handlers
    @on(DataTable.RowSelected, "#agents-datatable")
    def on_agent_selected(self, event: DataTable.RowSelected) -> None:
        """Handle agent selection in table."""
        agent_id = event.row_key.value
        self.selected_agent = self.state.get_agent(agent_id)

        # Update details panel
        details_panel = self.query_one("#agent-details", AgentDetailPanel)
        details_panel.agent_data = self.selected_agent

        # Update action buttons
        actions_panel = self.query_one("#actions-panel", QuickActionsPanel)
        actions_panel.selected_agent = self.selected_agent

    # Action button handlers
    @on(Button.Pressed, "#refresh-btn")
    def on_refresh_button(self):
        """Handle refresh button."""
        self.refresh_data()
        self.notify("Data refreshed", severity="information")

    @on(Button.Pressed, "#cleanup-btn")
    def on_cleanup_button(self):
        """Handle cleanup button."""
        self.executor.cleanup_stale_agents()
        self.refresh_data()
        self.notify("Stale agents cleaned up", severity="success")

    @on(Button.Pressed, "#stop-btn")
    def on_stop_button(self):
        """Handle stop agent button."""
        if self.selected_agent:
            success = self.executor.stop_agent(self.selected_agent.id)
            if success:
                self.notify(
                    f"Agent {self.selected_agent.semantic_name or self.selected_agent.id} stopped",
                    severity="success",
                )
            else:
                self.notify("Failed to stop agent", severity="error")

    @on(Button.Pressed, "#kill-btn")
    def on_kill_button(self):
        """Handle kill agent button."""
        if self.selected_agent:
            success = self.executor.stop_agent(self.selected_agent.id, force=True)
            if success:
                self.notify(
                    f"Agent {self.selected_agent.semantic_name or self.selected_agent.id} killed",
                    severity="warning",
                )
            else:
                self.notify("Failed to kill agent", severity="error")

    @on(Button.Pressed, "#logs-btn")
    def on_logs_button(self):
        """Handle view logs button."""
        if self.selected_agent and self.selected_agent.log_file:
            try:
                log_content = self.executor.get_agent_output(
                    self.selected_agent.id, tail_lines=20
                )
                if log_content:
                    # Show logs in notification (simplified for now)
                    self.notify(
                        f"Last 20 lines of {self.selected_agent.semantic_name or self.selected_agent.id} logs",
                        timeout=10,
                    )
                else:
                    self.notify("No log content available", severity="warning")
            except Exception as e:
                self.notify(f"Error reading logs: {e}", severity="error")

    @on(Button.Pressed, "#help-btn")
    def on_help_button(self):
        """Handle help button."""
        self.action_help()

    # Keyboard shortcuts
    def action_refresh(self) -> None:
        """Refresh data manually."""
        self.refresh_data()
        self.notify("Data refreshed", severity="information")

    def action_stop_agent(self) -> None:
        """Stop selected agent."""
        if self.selected_agent and self.selected_agent.status == AgentStatus.RUNNING:
            success = self.executor.stop_agent(self.selected_agent.id)
            if success:
                self.notify(
                    f"Agent {self.selected_agent.semantic_name or self.selected_agent.id} stopped",
                    severity="success",
                )
            else:
                self.notify("Failed to stop agent", severity="error")
        else:
            self.notify("No running agent selected", severity="warning")

    def action_kill_agent(self) -> None:
        """Kill selected agent."""
        if self.selected_agent and self.selected_agent.status == AgentStatus.RUNNING:
            success = self.executor.stop_agent(self.selected_agent.id, force=True)
            if success:
                self.notify(
                    f"Agent {self.selected_agent.semantic_name or self.selected_agent.id} killed",
                    severity="warning",
                )
            else:
                self.notify("Failed to kill agent", severity="error")
        else:
            self.notify("No running agent selected", severity="warning")

    def action_view_logs(self) -> None:
        """View logs for selected agent."""
        if self.selected_agent and self.selected_agent.log_file:
            try:
                log_content = self.executor.get_agent_output(
                    self.selected_agent.id, tail_lines=20
                )
                if log_content:
                    self.notify(
                        f"Last 20 lines of {self.selected_agent.semantic_name or self.selected_agent.id} logs",
                        timeout=10,
                    )
                else:
                    self.notify("No log content available", severity="warning")
            except Exception as e:
                self.notify(f"Error reading logs: {e}", severity="error")
        else:
            self.notify("No agent selected or no log file", severity="warning")

    def action_cleanup(self) -> None:
        """Cleanup stale agents."""
        self.executor.cleanup_stale_agents()
        self.refresh_data()
        self.notify("Stale agents cleaned up", severity="success")

    def action_switch_to_manager(self) -> None:
        """Switch to manager tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "manager-tab"

    def action_switch_to_monitor(self) -> None:
        """Switch to monitor tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "monitor-tab"

    def action_help(self) -> None:
        """Show help."""
        help_text = """
Hybrid Dashboard Help:

MANAGER TAB:
1. Type your task in natural language
2. Manager breaks it into small increments
3. Click 'Execute' to run the plan
4. Watch live progress

MONITOR TAB:
1. View all agents in interactive table
2. Click any agent to see details
3. Use buttons or keyboard shortcuts for control
4. Monitor real-time status updates

Keyboard Shortcuts:
  q          - Quit dashboard
  Ctrl+R     - Refresh data
  s          - Stop selected agent
  k          - Kill selected agent
  l          - View logs
  c          - Cleanup stale agents
  1          - Switch to Manager tab
  2          - Switch to Monitor tab
  ?          - Show this help

Examples:
  "Add a user authentication system"
  "Fix the login bug in auth.py"
  "Create a React component for user profile"
"""
        self.notify(help_text, timeout=20)


def run_hybrid_dashboard(workspace_dir: Path) -> None:
    """Launch the hybrid dashboard application."""
    app = HybridDashboardApp(workspace_dir)
    app.run()
