"""
Q Agentic Workstation Dashboard - Manager-First Interface.

A production-quality terminal UI with integrated Manager Agent chat.
Primary interaction through natural language, with live execution monitoring.
"""

from textual.app import App, ComposeResult
from textual.widgets import (
    Header,
    Footer,
    Static,
    DataTable,
    Log,
    Button,
    Label,
    TabbedContent,
    TabPane,
    ProgressBar,
    Input,
    RichLog,
)
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual import on
from textual.message import Message
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import asyncio

from .state import StateManager, AgentStatus
from .executor import AgentExecutor
from .manager import ManagerSession, ExecutionPlan, Increment, IncrementStatus
from .context import ContextManager


class ChatPanel(Static):
    """Chat conversation display."""

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
into small, testable increments with agents executing each step.[/dim italic]

[bold]What would you like to work on today?[/bold]
"""

        chat_text = "[bold cyan]💬 Manager Chat[/bold cyan]\n"
        chat_text += "━" * 42 + "\n\n"

        # Show last 10 messages
        for msg in self.messages[-10:]:
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

[dim]No active plan yet. 
Type a task in the chat to get started![/dim]
"""

        output = f"[bold green]📋 Execution Plan[/bold green]\n"
        output += "━" * 42 + "\n\n"

        # Simplify task display for long tasks
        task_display = self.plan.user_request
        if len(task_display) > 60:
            task_display = task_display[:57] + "..."
        output += f"[bold]Task:[/bold] {task_display}\n\n"

        # Show component breakdown for complex tasks
        num_increments = len(self.plan.increments)
        if num_increments > 3:
            backend_count = sum(
                1 for inc in self.plan.increments if inc.agent_type == "backend"
            )
            frontend_count = sum(
                1 for inc in self.plan.increments if inc.agent_type == "frontend"
            )
            test_count = sum(
                1 for inc in self.plan.increments if inc.agent_type == "test"
            )

            output += f"[bold cyan]Components:[/bold cyan]\n"
            if backend_count:
                output += f"  ⚙️  Backend: {backend_count}\n"
            if frontend_count:
                output += f"  🎨 Frontend: {frontend_count}\n"
            if test_count:
                output += f"  🧪 Testing: {test_count}\n"
            output += "\n"

        output += f"[bold]Steps: {num_increments}[/bold] | "
        output += (
            f"[bold]Complexity:[/bold] ~{self.plan.total_estimated_lines} lines\n\n"
        )

        # Show increments with better formatting
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

            # Shorten long descriptions
            desc_display = inc.description
            if len(desc_display) > 45:
                desc_display = desc_display[:42] + "..."

            output += (
                f"{i}. {status_emoji} [{status_color}]{desc_display}[/{status_color}]\n"
            )

            # Show agent type with emoji
            agent_emoji = {
                "backend": "⚙️",
                "frontend": "🎨",
                "test": "🧪",
                "orchestrator": "🎯",
            }.get(inc.agent_type, "📦")

            output += (
                f"   [dim]{agent_emoji} {inc.agent_type} | ~{inc.estimated_lines}L"
            )

            if inc.dependencies:
                dep_nums = [int(d.split("-")[1]) for d in inc.dependencies]
                output += f" | needs: {','.join(map(str, dep_nums))}"

            if inc.retry_count > 0:
                output += f" | retry: {inc.retry_count}/{inc.max_retries}"

            output += "[/dim]\n"

            if inc.verification_feedback:
                output += (
                    f"   [yellow]⚠️  {inc.verification_feedback[:40]}...[/yellow]\n"
                )

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

    agent_id = reactive(None)
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
            "completed": "✓",
            "failed": "✗",
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


class RecentAgentsPanel(Static):
    """Display recent agents in a compact list."""

    agents: reactive[List] = reactive(list, init=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agents = []

    def render(self) -> str:
        """Render recent agents."""
        output = "[bold yellow]🤖 Recent Agents[/bold yellow]\n"
        output += "━" * 42 + "\n\n"

        if not self.agents:
            output += "[dim]No agents yet[/dim]"
            return output

        # Show last 8 agents
        for agent in self.agents[:8]:
            status_emoji = {
                AgentStatus.PENDING: "⏳",
                AgentStatus.RUNNING: "🔄",
                AgentStatus.COMPLETED: "✅",
                AgentStatus.FAILED: "❌",
                AgentStatus.CANCELLED: "⊘",
            }.get(agent.status, "?")

            name = agent.semantic_name or agent.id[:10]
            task_preview = agent.task_description[:30]
            if len(agent.task_description) > 30:
                task_preview += "..."

            output += f"{status_emoji} [dim]{name}[/dim]\n"
            output += f"   {task_preview}\n"

        return output


class DashboardApp(App):
    """Q Agentic Workstation - Manager-First Dashboard."""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 3;
        grid-gutter: 1;
        padding: 1;
    }
    
    /* Chat container - left column, spans 3 rows */
    #chat-container {
        column-span: 1;
        row-span: 3;
        border: solid cyan;
        padding: 1;
        layout: vertical;
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
    
    /* Execution plan - right column, top row */
    #plan {
        column-span: 1;
        row-span: 1;
        border: solid green;
        padding: 1;
        overflow-y: auto;
    }
    
    /* Stats - right column, middle row */
    #stats {
        column-span: 1;
        row-span: 1;
        border: solid magenta;
        padding: 1;
        overflow-y: auto;
    }
    
    /* Recent agents - right column, bottom row */
    #agents {
        column-span: 1;
        row-span: 1;
        border: solid yellow;
        padding: 1;
        overflow-y: auto;
    }
    
    Input {
        width: 100%;
    }
    
    Button {
        min-width: 16;
    }
    
    Vertical {
        height: 100%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+r", "refresh", "Refresh"),
        ("?", "help", "Help"),
    ]

    TITLE = "Q Agentic Workstation"
    SUB_TITLE = "Manager-First Interface"

    def __init__(self, workspace_dir: Path):
        """Initialize dashboard."""
        super().__init__()
        self.workspace_dir = workspace_dir
        self.state = StateManager(workspace_dir)
        self.executor = AgentExecutor(self.state)
        self.context_manager = ContextManager(workspace_dir)
        self.update_interval = 0.5  # seconds - faster refresh for better responsiveness

        # Manager session
        self.manager_session: Optional[ManagerSession] = None
        self.executing_plan = False

    def compose(self) -> ComposeResult:
        """Create application layout."""
        yield Header()

        # Chat panel with input (left side, 2 rows)
        with Vertical(id="chat-container"):
            yield ChatPanel(id="chat")

            with Horizontal(id="chat-input-container"):
                yield Input(
                    placeholder="Describe your task... (e.g., 'Add a user login feature')",
                    id="chat-input",
                )
                yield Button("🚀 Send", id="send-button", variant="primary")
                yield Button(
                    "▶️ Execute", id="execute-button", variant="success", disabled=True
                )

        # Execution plan panel (right top)
        yield ExecutionPlanPanel(id="plan")

        # Stats panel (right middle)
        yield StatsPanel(id="stats")

        # Recent agents panel (right bottom)
        yield RecentAgentsPanel(id="agents")

        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        # Initialize manager session
        self.run_worker(self._initialize_manager(), exclusive=True)

        # Start periodic refresh
        self.set_interval(self.update_interval, self.refresh_data)

        # Initial refresh
        self.refresh_data()

        # Focus on input
        self.query_one("#chat-input", Input).focus()

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

            # Update recent agents
            agents = self.state.list_agents()
            agents_panel = self.query_one("#agents", RecentAgentsPanel)
            agents_panel.agents = agents
            agents_panel.refresh()

            # Update execution plan if active
            if self.manager_session and self.manager_session.current_plan:
                plan_panel = self.query_one("#plan", ExecutionPlanPanel)
                plan_panel.plan = self.manager_session.current_plan
                plan_panel.refresh()
        except Exception:
            pass  # Ignore errors during refresh

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
                plan_panel = self.query_one("#plan", ExecutionPlanPanel)
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
                    plan_panel = self.query_one("#plan", ExecutionPlanPanel)
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

    def action_refresh(self) -> None:
        """Refresh data manually."""
        self.refresh_data()
        self.notify("Data refreshed", severity="information")

    def action_help(self) -> None:
        """Show help."""
        help_text = """
Manager-First Dashboard Help:

1. Type your task in natural language
2. Manager breaks it into small increments
3. Click 'Execute' to run the plan
4. Watch live progress in the Execution Plan panel
5. View agent stats and recent activity

Keyboard Shortcuts:
  q          - Quit dashboard
  Ctrl+R     - Refresh data
  ?          - Show this help
  Enter      - Submit chat message

Examples:
  "Add a user authentication system"
  "Fix the login bug in auth.py"
  "Refactor the database queries"
  "Add tests for the API endpoints"
"""
        self.notify(help_text, timeout=20)


def run_dashboard(workspace_dir: Path) -> None:
    """Launch the dashboard application."""
    app = DashboardApp(workspace_dir)
    app.run()
