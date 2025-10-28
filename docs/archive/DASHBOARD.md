# Q Agentic Workstation Dashboard

## Beautiful TUI Control Center

A production-quality terminal UI for monitoring and controlling your agents in real-time.

## Features

### 📊 Live Statistics Panel
- **Total Agents**: Overall count
- **🔄 Running**: Active agents  
- **⏳ Pending**: Queued agents
- **✓ Completed**: Successfully finished
- **✗ Failed**: Agents with errors

Updates automatically every 2 seconds.

### 🤖 Agent List (Interactive Table)
- **Status**: Visual emoji indicators
- **ID**: Short agent identifier
- **Agent**: Which agent config
- **Duration**: Time elapsed
- **Task**: Task description preview

Click any row to select and view details.

### 🔍 Agent Details Panel
When you select an agent, see:
- Full agent ID
- Current status with color coding
- Agent type
- Precise duration
- Process ID (PID)
- Complete task description
- Log and result file locations
- Error messages (if any)

### ⚡ Quick Actions
Interactive buttons for common operations:
- **🔄 Refresh**: Manually refresh data
- **🗑️ Cleanup**: Remove stale agents
- **⏸️ Stop Agent**: Graceful shutdown (selected agent)
- **❌ Kill Agent**: Force terminate (selected agent)
- **📋 View Logs**: Show recent log output
- **❓ Help**: Display keyboard shortcuts

Buttons enable/disable based on context.

## Keyboard Shortcuts

| Key | Action | Description |
|-----|--------|-------------|
| `q` | Quit | Exit dashboard |
| `r` | Refresh | Manually refresh data |
| `c` | Cleanup | Remove stale agents |
| `s` | Stop | Gracefully stop selected agent |
| `k` | Kill | Force kill selected agent |
| `l` | Logs | View logs for selected agent |
| `?` | Help | Show help |
| `↑/↓` | Navigate | Move between table rows |
| `Enter` | Select | Select agent row |

## Launch Dashboard

```bash
# From any workspace
qaw dashboard

# Or with shorthand
qaw dash  # (if alias created)
```

## Usage Flow

1. **Launch**: `qaw dashboard`
2. **View Status**: See all agents at a glance
3. **Select Agent**: Click or arrow-key navigate to an agent
4. **View Details**: Right panel shows full info
5. **Take Action**: Use buttons or keyboard shortcuts
6. **Monitor**: Auto-refreshes every 2 seconds
7. **Quit**: Press `q` when done

## Visual Design

```
┌─────────────────────────────────────────────────────────────┐
│ Q Agentic Workstation │ Parallel Agent Control Center      │
├─────────────┬───────────────────────────────────────────────┤
│             │                                               │
│ 📊 Overview │    🤖 Active Agents                          │
│             │    ┌────────────────────────────────────────┐│
│ Total: 5    │    │Status│ID  │Agent│Duration│Task        ││
│ Running: 2  │    ├──────┼────┼─────┼────────┼────────────┤│
│ Pending: 0  │    │🔄    │abc │front│30s     │Create UI...││
│ Completed: 3│    │✓     │def │back │1m 15s  │Add API...  ││
│ Failed: 0   │    └────────────────────────────────────────┘│
│             ├───────────────────────────────────────────────┤
│             │ 🔍 Agent Details    │ ⚡ Quick Actions        │
│             │                     │ [🔄 Refresh]           │
│             │ ID: agent-abc123    │ [🗑️ Cleanup]           │
│             │ Status: RUNNING     │ [⏸️ Stop Agent]        │
│             │ Agent: frontend-a.. │ [❌ Kill Agent]        │
│             │ Duration: 30s       │ [📋 View Logs]         │
│             │ PID: 12345          │ [❓ Help]              │
└─────────────┴───────────────────────────────────────────────┘
│ q:Quit r:Refresh c:Cleanup s:Stop k:Kill l:Logs ?:Help    │
└─────────────────────────────────────────────────────────────┘
```

## Color Coding

- **Blue**: Running agents and active elements
- **Green**: Completed agents and success messages
- **Red**: Failed agents and errors
- **Yellow**: Pending agents and warnings
- **Cyan**: Headers and labels

## Real-Time Updates

The dashboard automatically:
- Refreshes every 2 seconds
- Detects agent state changes
- Updates durations
- Cleans up stale agents
- Maintains your selection

No manual intervention needed!

## Interactive Features

### Agent Selection
- **Mouse**: Click any row in the table
- **Keyboard**: Arrow keys + Enter
- **Result**: Details panel updates, action buttons enable

### Button Actions
- **Mouse**: Click buttons
- **Keyboard**: Use shortcuts (faster!)
- **Feedback**: Notifications appear for 3 seconds

### Notifications
Bottom-right corner shows:
- ℹ️ Information (blue)
- ✓ Success (green)
- ⚠️ Warning (yellow)
- ✗ Error (red)

## Tips

1. **Keep it running**: Dashboard is designed to stay open while agents work
2. **Multiple terminals**: Run `qaw dashboard` in one, submit tasks in another
3. **Quick stop**: Press `s` to stop a misbehaving agent
4. **Regular cleanup**: Press `c` to keep state tidy
5. **Help always available**: Press `?` anytime

## Performance

- **Lightweight**: Uses minimal CPU
- **Responsive**: Instant interactions
- **Scalable**: Handles 20+ agents smoothly
- **Efficient**: Only updates what changed

## Requirements

- Python 3.8+
- textual >= 0.47.0 (installed automatically)
- Terminal with 256 colors (most modern terminals)
- Minimum size: 80x24 characters

## Troubleshooting

### Dashboard won't launch
```bash
# Check textual is installed
pip install textual

# Verify workspace
qaw init  # If needed
```

### Colors look wrong
- Use a modern terminal (iTerm2, Warp, Windows Terminal)
- Enable 256-color support
- Try a different theme

### Dashboard is laggy
- Reduce number of agents (cleanup old ones)
- Increase update interval (currently 2s)
- Close other resource-intensive apps

## Future Enhancements

Coming in future versions:
- Log viewer modal with syntax highlighting
- Agent performance graphs
- Custom theme support
- Split-pane log streaming
- Agent spawn from dashboard
- Filtering and search

## Comparison with CLI

| Feature | CLI (`qaw status`) | Dashboard |
|---------|-------------------|-----------|
| Updates | Manual | Automatic (2s) |
| Agent details | Requires command | Click to view |
| Actions | Type commands | Click buttons |
| Logs | Separate command | Built-in viewer |
| Visual | Text only | Rich UI |
| Shortcuts | N/A | Full keyboard |
| Monitoring | Polling | Live |

**Use CLI for**: Quick checks, scripting, automation
**Use Dashboard for**: Active monitoring, interactive control, long sessions

## Demo

Try this to see the dashboard in action:

```bash
# Terminal 1: Launch dashboard
qaw dashboard

# Terminal 2: Submit tasks
qaw submit "Create component 1" --agent frontend-agent
qaw submit "Create component 2" --agent frontend-agent  
qaw submit "Create API endpoint" --agent backend-agent

# Watch the dashboard automatically update!
```

Enjoy your beautiful control center! 🚀
