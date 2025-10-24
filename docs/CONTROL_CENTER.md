# Control Center Design

## Overview

The Control Center is the central hub for monitoring, managing, and reviewing all agent activity. It provides real-time visibility into parallel agent execution and enables manual intervention when needed.

## Core Features

### 1. Dashboard
Real-time overview of all agent activity

### 2. Agent Management
Start, stop, pause, resume agents

### 3. Log Streaming
Live output from all agents

### 4. Task Queue Visualization
See pending, running, and completed tasks

### 5. Result Review
Inspect agent outputs and artifacts

### 6. Manual Intervention
Override or guide agents when needed

## Implementation Options

### Option A: Terminal UI (Recommended for MVP)
**Pros**:
- Native terminal experience
- Fast and lightweight
- No browser dependency
- Works over SSH

**Tech Stack**:
- Python with `rich` or `textual` library
- Bash with `ncurses`
- Go with `bubbletea`

### Option B: Web Dashboard
**Pros**:
- Rich UI capabilities
- Multi-device access
- Better for complex visualizations
- Easier to share/demo

**Tech Stack**:
- Backend: Node.js/Python FastAPI
- Frontend: React/Vue/Svelte
- WebSockets for real-time updates

### Option C: Hybrid
**Best of both worlds**:
- CLI for quick status checks
- TUI for interactive monitoring
- Web dashboard for detailed analysis

## Terminal UI Design

### Main Dashboard View
```
┌─ Q Agentic Workstation ────────────────────────────────────┐
│ Status: 3 active | 2 pending | 5 completed | 1 failed      │
│ Uptime: 2h 15m | Total Tasks: 11                            │
└────────────────────────────────────────────────────────────┘

┌─ Active Agents ────────────────────────────────────────────┐
│ ID      │ Agent         │ Task              │ Status │ Time│
├─────────┼───────────────┼───────────────────┼────────┼─────┤
│ a7f2c31 │ dev-agent     │ Add login feature │ 🟢 RUN │ 5m  │
│ b3d8e42 │ test-agent    │ Write unit tests  │ 🟢 RUN │ 3m  │
│ c1f9a53 │ doc-agent     │ Update README     │ 🟡 WAIT│ 8m  │
└─────────┴───────────────┴───────────────────┴────────┴─────┘

┌─ Task Queue ───────────────────────────────────────────────┐
│ [2] Fix auth bug                                   [HIGH]   │
│ [1] Refactor user model                            [MED]    │
└────────────────────────────────────────────────────────────┘

┌─ Recent Activity ──────────────────────────────────────────┐
│ 17:34:22 ✓ Agent a7f2c31 completed task                    │
│ 17:33:45 ⚠ Agent b3d8e42 requested approval for fs_write   │
│ 17:32:11 ▶ Agent c1f9a53 spawned                           │
└────────────────────────────────────────────────────────────┘

[1] View Agent [2] Logs [3] Queue [4] Submit Task [q] Quit
```

### Agent Detail View
```
┌─ Agent Detail: a7f2c31 ────────────────────────────────────┐
│ Agent: dev-agent                                            │
│ Task: Add login feature                                     │
│ Status: 🟢 RUNNING                                          │
│ Started: 17:29:15 (5m 12s ago)                              │
│ PID: 42731                                                  │
└────────────────────────────────────────────────────────────┘

┌─ Live Output ──────────────────────────────────────────────┐
│ Reading authentication module...                            │
│ Creating login component at src/components/Login.tsx        │
│ Writing authentication service...                           │
│ Running type checker... ✓                                   │
│ Current action: Writing tests...                            │
│ █                                                           │
└────────────────────────────────────────────────────────────┘

┌─ Files Modified ───────────────────────────────────────────┐
│ ✏️  src/components/Login.tsx (new)                          │
│ ✏️  src/services/auth.ts (modified)                         │
│ ✏️  src/types/user.ts (modified)                            │
└────────────────────────────────────────────────────────────┘

┌─ Actions ──────────────────────────────────────────────────┐
│ [p] Pause [s] Stop [f] Follow logs [r] Review files        │
│ [i] Inject message [b] Back                                 │
└────────────────────────────────────────────────────────────┘
```

### Log Viewer
```
┌─ Agent Logs: a7f2c31 ──────────────────────────────────────┐
│ Filter: [all] [info] [warning] [error]     [f] Follow: ON  │
└────────────────────────────────────────────────────────────┘

17:29:15 [INFO] Agent started with task: Add login feature
17:29:16 [INFO] Reading codebase structure...
17:29:18 [INFO] Found 3 related files
17:29:20 [INFO] Planning implementation...
17:30:02 [INFO] Creating src/components/Login.tsx
17:30:45 [WARN] Type error in auth.ts - fixing...
17:31:12 [INFO] Type check passed
17:32:30 [INFO] Writing tests...
17:34:05 [INFO] All tests passing (12/12)
17:34:22 [SUCCESS] Task completed successfully

[/] Search [c] Clear [x] Export [b] Back
```

### Task Queue View
```
┌─ Task Queue ───────────────────────────────────────────────┐
│ Pending: 2 | Running: 3 | Completed: 5                      │
└────────────────────────────────────────────────────────────┘

PENDING
┌────────────────────────────────────────────────────────────┐
│ □ fix-auth-bug          [HIGH] Created: 10m ago            │
│   Fix authentication token expiration bug                   │
│   Dependencies: None                                        │
│                                                             │
│ □ refactor-user-model   [MED]  Created: 15m ago            │
│   Refactor user model to use TypeScript                    │
│   Dependencies: None                                        │
└────────────────────────────────────────────────────────────┘

RUNNING
┌────────────────────────────────────────────────────────────┐
│ ▶ add-login-feature     [HIGH] Agent: a7f2c31 (5m)         │
│   Add login feature with OAuth support                      │
│   Progress: ████████░░ 80%                                 │
└────────────────────────────────────────────────────────────┘

[a] Add task [e] Edit [d] Delete [r] Reorder [Enter] Details
```

## CLI Commands

### Status Commands
```bash
# Overview
qaw status

# Detailed status with logs
qaw status --verbose

# Watch mode (live updates)
qaw status --watch

# Specific agent
qaw status a7f2c31
```

### Agent Management
```bash
# List all agents
qaw agents

# View agent details
qaw agent a7f2c31

# Stop agent
qaw stop a7f2c31

# Pause/resume agent
qaw pause a7f2c31
qaw resume a7f2c31

# Kill agent (force)
qaw kill a7f2c31
```

### Log Commands
```bash
# Stream logs from agent
qaw logs a7f2c31

# Follow mode
qaw logs -f a7f2c31

# All agents combined
qaw logs --all

# Filter by level
qaw logs --level error

# Export logs
qaw logs a7f2c31 --export agent-logs.txt
```

### Task Queue Commands
```bash
# View queue
qaw queue

# Add task
qaw submit "Fix authentication bug" --priority high

# Cancel task
qaw cancel task-id

# Reorder tasks
qaw reorder task-id --position 1
```

### Review Commands
```bash
# Review agent results
qaw review a7f2c31

# Show file changes
qaw diff a7f2c31

# Accept changes
qaw accept a7f2c31

# Reject and rollback
qaw reject a7f2c31 --rollback

# Request modifications
qaw modify a7f2c31 "Add error handling to login"
```

## Data Models

### Agent State
```json
{
  "id": "a7f2c31",
  "name": "dev-agent",
  "status": "running",
  "task": {
    "id": "task-123",
    "description": "Add login feature",
    "priority": "high"
  },
  "pid": 42731,
  "startTime": "2025-10-24T17:29:15Z",
  "lastUpdate": "2025-10-24T17:34:22Z",
  "progress": {
    "percentage": 80,
    "currentAction": "Writing tests"
  },
  "files": {
    "created": ["src/components/Login.tsx"],
    "modified": ["src/services/auth.ts", "src/types/user.ts"],
    "deleted": []
  },
  "logs": ".qaw/logs/agent-a7f2c31.log",
  "results": ".qaw/results/agent-a7f2c31/"
}
```

### Task Model
```json
{
  "id": "task-123",
  "description": "Add login feature with OAuth support",
  "priority": "high",
  "status": "running",
  "assignedAgent": "a7f2c31",
  "dependencies": [],
  "createdAt": "2025-10-24T17:24:00Z",
  "startedAt": "2025-10-24T17:29:15Z",
  "completedAt": null,
  "metadata": {
    "estimatedDuration": "10m",
    "tags": ["auth", "frontend", "feature"]
  }
}
```

## Real-Time Updates

### WebSocket Events (for Web Dashboard)
```javascript
// Agent status updates
{
  "type": "agent.status",
  "agentId": "a7f2c31",
  "status": "running",
  "progress": 80
}

// Log entries
{
  "type": "agent.log",
  "agentId": "a7f2c31",
  "level": "info",
  "message": "Writing tests...",
  "timestamp": "2025-10-24T17:32:30Z"
}

// Task queue changes
{
  "type": "queue.update",
  "pending": 2,
  "running": 3,
  "completed": 5
}
```

### File System Watching (for TUI)
```bash
# Watch state directory for changes
inotifywait -m -r .qaw/state/ | while read path action file; do
  # Update TUI on state changes
  update_dashboard
done
```

## Notifications

### Desktop Notifications
```bash
# On task completion
notify-send "Agent Completed" \
  "Agent a7f2c31 finished: Add login feature"

# On error
notify-send -u critical "Agent Error" \
  "Agent b3d8e42 encountered an error"
```

### Slack/Discord Integration
```bash
# Post to Slack
curl -X POST $SLACK_WEBHOOK \
  -d '{"text": "✅ Agent completed: Add login feature"}'
```

### Email Notifications
```bash
# Send email on completion
echo "Agent completed task" | mail -s "Task Complete" user@example.com
```

## Manual Intervention

### Inject Message to Agent
```bash
# Send instruction to running agent
qaw inject a7f2c31 "Use bcrypt for password hashing"
```

### Approval Gates
```bash
# Agent requests approval for risky operation
qaw approvals list

# Approve or reject
qaw approve a7f2c31 fs_write
qaw reject a7f2c31 execute_bash
```

## Performance Metrics

### Dashboard Metrics
- Active agents count
- Task throughput (tasks/hour)
- Average task duration
- Success/failure rate
- Resource usage (CPU, memory)
- Cost per task (API calls)

### Historical Analysis
```bash
# View metrics for past week
qaw metrics --period 7d

# Export metrics
qaw metrics --export metrics.csv

# Compare agent performance
qaw metrics --compare dev-agent,test-agent
```

## Future Enhancements

1. **Visual Task Graph**: Show task dependencies as a graph
2. **Agent Collaboration View**: See how agents interact
3. **Predictive Analytics**: Estimate completion times
4. **Cost Dashboard**: Track API usage and costs
5. **A/B Testing**: Compare different agent strategies
6. **Replay Mode**: Re-execute past tasks for debugging
