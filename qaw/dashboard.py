"""
Q Agentic Workstation Dashboard - Beautiful TUI Interface.

A production-quality terminal UI for monitoring and controlling agents.
"""

from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Static, DataTable, Log, Button, 
    Label, TabbedContent, TabPane, ProgressBar
)
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual import on
from datetime import datetime
from pathlib import Path
from typing import Optional
import asyncio

from .state import StateManager, AgentStatus
from .executor import AgentExecutor


class StatsPanel(Static):
    """Display overall statistics."""
    
    stats = reactive({
        "total": 0,
        "running": 0,
        "pending": 0,
        "completed": 0,
        "failed": 0,
    })
    
    def render(self) -> str:
        """Render statistics."""
        s = self.stats
        return f"""
[bold cyan]📊 Overview[/bold cyan]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Agents:     [bold]{s['total']:>3}[/bold]
🔄 Running:       [blue]{s['running']:>3}[/blue]
⏳ Pending:       [yellow]{s['pending']:>3}[/yellow]
✓  Completed:     [green]{s['completed']:>3}[/green]
✗  Failed:        [red]{s['failed']:>3}[/red]
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


class QuickActionsPanel(Static):
    """Quick action buttons."""
    
    selected_agent_id = reactive(None)
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("[bold cyan]⚡ Quick Actions[/bold cyan]")
        yield Button("🔄 Refresh", id="refresh", variant="primary")
        yield Button("🗑️  Cleanup", id="cleanup", variant="default")
        yield Button("⏸️  Stop Agent", id="stop", variant="warning", disabled=True)
        yield Button("❌ Kill Agent", id="kill", variant="error", disabled=True)
        yield Button("📋 View Logs", id="logs", variant="default", disabled=True)
        yield Button("❓ Help", id="help", variant="default")


class DashboardApp(App):
    """Q Agentic Workstation Dashboard."""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 2;
        grid-gutter: 1;
        padding: 1;
    }
    
    #stats {
        column-span: 1;
        row-span: 2;
        border: solid $primary;
        padding: 1;
    }
    
    #agents-container {
        column-span: 2;
        row-span: 1;
        border: solid $accent;
        padding: 0 1;
    }
    
    #detail-panel {
        column-span: 1;
        row-span: 1;
        border: solid $success;
        padding: 1;
    }
    
    #actions-panel {
        column-span: 1;
        row-span: 1;
        border: solid $warning;
        padding: 1;
    }
    
    #agents-table {
        height: 100%;
    }
    
    DataTable {
        height: 100%;
    }
    
    Button {
        margin: 1 0;
        width: 100%;
    }
    
    .status-running {
        color: $primary;
    }
    
    .status-completed {
        color: $success;
    }
    
    .status-failed {
        color: $error;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("c", "cleanup", "Cleanup"),
        ("s", "stop_agent", "Stop"),
        ("k", "kill_agent", "Kill"),
        ("l", "view_logs", "Logs"),
        ("?", "help", "Help"),
    ]
    
    TITLE = "Q Agentic Workstation"
    SUB_TITLE = "Parallel Agent Control Center"
    
    def __init__(self, workspace_dir: Path):
        """Initialize dashboard."""
        super().__init__()
        self.workspace_dir = workspace_dir
        self.state = StateManager(workspace_dir)
        self.executor = AgentExecutor(self.state)
        self.selected_agent_id: Optional[str] = None
        self.update_interval = 2.0  # seconds
        
    def compose(self) -> ComposeResult:
        """Create application layout."""
        yield Header()
        
        # Statistics panel (left)
        stats_panel = StatsPanel(id="stats")
        yield stats_panel
        
        # Agent list (top right)
        with Container(id="agents-container"):
            yield Label("[bold cyan]🤖 Active Agents[/bold cyan]")
            agents_table = DataTable(id="agents-table", cursor_type="row")
            agents_table.add_columns("Status", "ID", "Agent", "Duration", "Task")
            yield agents_table
        
        # Agent details (middle right)
        yield AgentDetailPanel(id="detail-panel")
        
        # Quick actions (bottom right)
        with Container(id="actions-panel"):
            yield QuickActionsPanel(id="actions")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.refresh_data()
        self.set_interval(self.update_interval, self.refresh_data)
    
    def refresh_data(self) -> None:
        """Refresh all data from state manager."""
        # Cleanup stale agents
        self.executor.cleanup_stale_agents()
        
        # Update statistics
        stats = self.state.get_stats()
        stats_panel = self.query_one("#stats", StatsPanel)
        stats_panel.stats = stats
        
        # Update agent table
        agents = self.state.list_agents()
        table = self.query_one("#agents-table", DataTable)
        
        # Clear and repopulate table
        table.clear()
        
        for agent in agents[:20]:  # Limit to 20 most recent
            # Status emoji
            status_emoji = {
                AgentStatus.PENDING: "⏳",
                AgentStatus.RUNNING: "🔄",
                AgentStatus.COMPLETED: "✓",
                AgentStatus.FAILED: "✗",
                AgentStatus.CANCELLED: "⊘",
            }.get(agent.status, "?")
            
            # Duration
            duration = self._format_duration(agent.start_time, agent.end_time)
            
            # Use semantic name if available
            agent_display = agent.semantic_name if agent.semantic_name else agent.id[:12]
            
            # Task preview
            task = agent.task_description
            task_preview = task[:40] + "..." if len(task) > 40 else task
            
            # Add row with style class
            status_class = f"status-{agent.status.value}"
            table.add_row(
                status_emoji,
                agent_display[:25],  # Show semantic name or truncated ID
                agent.agent_name[:18],
                duration,
                task_preview,
                key=agent.id,
            )
        
        # Update selected agent details if one is selected
        if self.selected_agent_id:
            agent = self.state.get_agent(self.selected_agent_id)
            if agent:
                detail_panel = self.query_one("#detail-panel", AgentDetailPanel)
                detail_panel.agent_data = agent
    
    def _format_duration(self, start: Optional[str], end: Optional[str]) -> str:
        """Format duration string."""
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
                return f"{hours}h {minutes}m"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        except:
            return "N/A"
    
    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in agent table."""
        table = event.data_table
        row_key = event.row_key
        
        self.selected_agent_id = str(row_key.value)
        
        # Update detail panel
        agent = self.state.get_agent(self.selected_agent_id)
        if agent:
            detail_panel = self.query_one("#detail-panel", AgentDetailPanel)
            detail_panel.agent_data = agent
            
            # Enable action buttons
            actions = self.query_one("#actions", QuickActionsPanel)
            actions.selected_agent_id = self.selected_agent_id
            
            # Enable/disable buttons based on agent state
            is_running = agent.status == AgentStatus.RUNNING
            self.query_one("#stop", Button).disabled = not is_running
            self.query_one("#kill", Button).disabled = not is_running
            self.query_one("#logs", Button).disabled = False
    
    @on(Button.Pressed, "#refresh")
    def action_refresh(self) -> None:
        """Refresh data manually."""
        self.refresh_data()
        self.notify("Data refreshed", severity="information")
    
    @on(Button.Pressed, "#cleanup")
    def action_cleanup(self) -> None:
        """Cleanup stale agents."""
        self.executor.cleanup_stale_agents()
        self.refresh_data()
        self.notify("Cleanup complete", severity="success")
    
    @on(Button.Pressed, "#stop")
    def action_stop_agent(self) -> None:
        """Stop selected agent gracefully."""
        if not self.selected_agent_id:
            self.notify("No agent selected", severity="warning")
            return
        
        if self.executor.stop_agent(self.selected_agent_id, force=False):
            self.notify(f"Agent {self.selected_agent_id[:12]} stopped", severity="success")
            self.refresh_data()
        else:
            self.notify("Could not stop agent", severity="error")
    
    @on(Button.Pressed, "#kill")
    def action_kill_agent(self) -> None:
        """Force kill selected agent."""
        if not self.selected_agent_id:
            self.notify("No agent selected", severity="warning")
            return
        
        if self.executor.stop_agent(self.selected_agent_id, force=True):
            self.notify(f"Agent {self.selected_agent_id[:12]} killed", severity="warning")
            self.refresh_data()
        else:
            self.notify("Could not kill agent", severity="error")
    
    @on(Button.Pressed, "#logs")
    async def action_view_logs(self) -> None:
        """View logs for selected agent."""
        if not self.selected_agent_id:
            self.notify("No agent selected", severity="warning")
            return
        
        agent = self.state.get_agent(self.selected_agent_id)
        if not agent or not Path(agent.log_file).exists():
            self.notify("No logs available", severity="warning")
            return
        
        # Show logs in a modal (for now, just notify - can enhance later)
        try:
            with open(agent.log_file) as f:
                lines = f.readlines()
                last_lines = "".join(lines[-30:])
                self.notify(f"Last 30 lines:\n{last_lines}", timeout=10)
        except Exception as e:
            self.notify(f"Error reading logs: {e}", severity="error")
    
    @on(Button.Pressed, "#help")
    def action_help(self) -> None:
        """Show help."""
        help_text = """
Keyboard Shortcuts:
  q - Quit dashboard
  r - Refresh data
  c - Cleanup stale agents
  s - Stop selected agent
  k - Kill selected agent
  l - View logs
  ? - Show this help

Mouse:
  Click rows to select agents
  Click buttons for actions
"""
        self.notify(help_text, timeout=15)


def run_dashboard(workspace_dir: Path) -> None:
    """Launch the dashboard application."""
    app = DashboardApp(workspace_dir)
    app.run()
