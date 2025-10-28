# Semantic Naming & Autopilot Mode

Two powerful new features that make agent management more intuitive and enable long-running autonomous tasks.

---

## Semantic Agent Naming

### Problem Solved
Previously, agents had random hash IDs like `agent-7f3a9b2c`, making it hard to identify what each agent was doing at a glance.

### Solution
Agents now get **meaningful names** automatically generated from their task description:

```bash
# Before
agent-7f3a9b2c

# After
backend-auth-login
frontend-navbar-refactor
test-verify-api
```

### How It Works

The `AgentNamer` class:
1. **Extracts key terms** from task descriptions (stops words removed)
2. **Prioritizes action words** (add, fix, refactor, etc.)
3. **Abbreviates** common technical terms (authentication → auth, database → db)
4. **Combines** agent type + key terms into semantic name

#### Examples

| Task Description | Agent Type | Generated Name |
|---|---|---|
| "Add user authentication with JWT" | backend | `backend-auth-user-jwt` |
| "Fix navbar scrolling bug" | frontend | `frontend-fix-navbar-scroll` |
| "Refactor database queries" | backend | `backend-refactor-db-queries` |
| "Write tests for API endpoints" | test | `test-api-endpoints` |
| "Update documentation" | doc | `doc-update` |

### Usage

#### Automatic Naming (Default)
```bash
qaw submit "Add user authentication" --agent backend-agent
# Creates: backend-auth-user
```

#### Custom Names
```bash
qaw submit "Add auth" --agent backend-agent --name my-auth-feature
# Creates: my-auth-feature
```

#### In Python Code
```python
from qaw.naming import AgentNamer

# Generate name
name = AgentNamer.generate_name(
    task_description="Fix login bug",
    agent_type="backend",
)
# Result: "backend-fix-login-bug"

# With custom override
name = AgentNamer.generate_name(
    task_description="Add feature",
    agent_type="frontend",
    custom_name="custom-feature",
)
# Result: "custom-feature"
```

### Dashboard Display

The dashboard now shows semantic names everywhere:

```
┌────────────────────────────────────────┐
│ 🤖 Active Agents                       │
├────────────────────────────────────────┤
│ Status │ ID                  │ Task    │
├────────────────────────────────────────┤
│ 🔄     │ backend-auth-login  │ Add...  │
│ ✓      │ frontend-nav-fix    │ Fix...  │
│ ⏳     │ test-verify-api     │ Write...│
└────────────────────────────────────────┘

🔍 Agent Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name:        backend-auth-login
Status:      🔄 RUNNING
Agent:       backend-agent
Duration:    2m 15s
```

### Benefits

1. **Instant Recognition**: Know what each agent is doing at a glance
2. **Easier Debugging**: Logs and results are in folders with meaningful names
3. **Better Organization**: Group related agents by name pattern
4. **Historical Context**: Understand past work without checking task descriptions

---

## Autopilot Mode

### Problem Solved
Q CLI sessions can timeout during long-running tasks, requiring manual intervention. For complex multi-step tasks, you need to stay engaged.

### Solution
**Autopilot mode** enables agents to run indefinitely with automatic keep-alive monitoring, perfect for:
- Long refactoring tasks
- Multi-file changes
- Complex feature implementation
- Batch testing
- Manager-orchestrated workflows

### How It Works

When autopilot is enabled:
1. **Background thread** monitors agent process every 30 seconds
2. **Keeps process alive** to prevent timeout
3. **Auto-detects completion** when agent finishes
4. **Cleans up automatically** - updates status and logs

#### Architecture

```
Main Process
    │
    ├─ Spawn Agent (with --autopilot)
    │     │
    │     └─ Q CLI Agent Process
    │           (runs task)
    │
    └─ Keep-Alive Thread
          │
          └─ Monitors PID every 30s
             └─ Logs status
             └─ Detects completion
             └─ Updates state
```

### Usage

#### CLI
```bash
# Enable autopilot mode
qaw submit "Large refactoring task" --agent backend-agent --autopilot

# Combined with auto-approval (recommended)
qaw submit "Deploy changes" --agent orchestrator-agent --autopilot --trust-all-tools

# With custom name
qaw submit "Complex feature" --agent backend-agent --autopilot --name feature-x
```

#### What You'll See
```bash
$ qaw submit "Add auth system" --agent backend-agent --autopilot --trust-all-tools

✓ Created task: task-a3b4c5d6
✓ Spawning agent: backend-auth-system (backend-agent)
🤖 Autopilot mode enabled - agent will run until completion

✓ Agent running (PID: 12345)

Log file: .qaw/logs/backend-auth-system.log
Result dir: .qaw/results/backend-auth-system

Monitor with: qaw status backend-auth-system
View logs with: qaw logs backend-auth-system
```

#### Python API
```python
from qaw.executor import AgentExecutor
from qaw.state import StateManager

state = StateManager(workspace_dir)
executor = AgentExecutor(state)

# Create agent
agent = state.create_agent(
    agent_name="backend-agent",
    task_id=task.id,
    task_description="Long-running task",
)

# Spawn with autopilot
pid = executor.spawn_agent(
    agent,
    trust_all_tools=True,
    autopilot=True,  # Enable keep-alive
)

# Agent runs independently
# Keep-alive thread monitors it
# State automatically updated on completion
```

### Keep-Alive Mechanism

The keep-alive thread:
- **Interval**: Checks process every 30 seconds
- **Action**: Logs agent status, verifies process is alive
- **Detection**: Immediately detects when agent completes
- **Cleanup**: Updates agent status (COMPLETED/FAILED) and cleans up PID file
- **Thread Safety**: Daemon thread that automatically terminates with main process

#### Logs
```
2025-01-24 10:15:30 [INFO] Agent backend-auth-system spawned successfully (PID: 12345)
2025-01-24 10:15:30 [INFO] Autopilot mode enabled for agent backend-auth-system
2025-01-24 10:15:30 [INFO] Started keep-alive thread for agent backend-auth-system

2025-01-24 10:16:00 [DEBUG] Keep-alive ping: Agent backend-auth-system still running
2025-01-24 10:16:30 [DEBUG] Keep-alive ping: Agent backend-auth-system still running
2025-01-24 10:17:00 [DEBUG] Keep-alive ping: Agent backend-auth-system still running

2025-01-24 10:20:45 [INFO] Keep-alive: Agent backend-auth-system process ended
2025-01-24 10:20:45 [INFO] Keep-alive thread stopping for agent backend-auth-system
```

### Stopping Autopilot Agents

Autopilot agents can still be stopped manually:

```bash
# Graceful stop
qaw stop backend-auth-system

# Force kill
qaw stop backend-auth-system --force
```

Or from dashboard:
- Select agent
- Click "Stop Agent" or press `s`
- Click "Kill Agent" or press `k` (force)

The keep-alive thread will automatically detect the stop and clean up.

### Use Cases

#### 1. Manager-Orchestrated Workflows
```bash
# Manager spawns multiple agents in autopilot
# Each runs independently until done
qaw submit "Implement feature X with full testing" \
  --agent manager-agent \
  --autopilot \
  --trust-all-tools
```

#### 2. Long Refactoring
```bash
# Large codebase refactoring that takes 30+ minutes
qaw submit "Refactor entire API layer" \
  --agent backend-agent \
  --autopilot \
  --trust-all-tools
```

#### 3. Batch Operations
```bash
# Process many files
qaw submit "Update copyright headers in all files" \
  --agent orchestrator-agent \
  --autopilot
```

#### 4. Step Away Development
```bash
# Start task, go get coffee, come back to completed work
qaw submit "Add comprehensive test suite" \
  --agent test-agent \
  --autopilot \
  --trust-all-tools

# Check status later
qaw status test-verify-comprehensive
# Status: ✓ COMPLETED
```

### Benefits

1. **No Babysitting**: Start task and walk away
2. **No Timeouts**: Agents run as long as needed
3. **Automatic Monitoring**: Process health tracked continuously
4. **Clean Completion**: Proper cleanup when done
5. **Manager-Ready**: Essential for autonomous orchestration
6. **Reliable**: Thread-safe, error-handled, logged

---

## Combined Example: Full Workflow

Let's use both features together:

```bash
# Initialize workspace
cd my-project
qaw init

# Submit a complex task with meaningful name and autopilot
qaw submit "Implement user authentication system with tests" \
  --agent orchestrator-agent \
  --name auth-system-implementation \
  --autopilot \
  --trust-all-tools

# Output:
# ✓ Created task: task-f8e9a1b2
# ✓ Spawning agent: auth-system-implementation (orchestrator-agent)
# 🤖 Autopilot mode enabled - agent will run until completion
# ✓ Agent running (PID: 54321)

# Open dashboard to monitor
qaw dashboard
```

Dashboard shows:
```
┌──────────────────────────────────────────────────┐
│ 🤖 Active Agents                                 │
├──────────────────────────────────────────────────┤
│ Status │ ID                           │ Duration │
├──────────────────────────────────────────────────┤
│ 🔄     │ auth-system-implementation   │ 5m 23s   │
└──────────────────────────────────────────────────┘

🔍 Agent Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name:        auth-system-implementation
Status:      🔄 RUNNING
Agent:       orchestrator-agent
Duration:    5m 23s

Task:
  Implement user authentication system with tests
```

Walk away, come back later:

```bash
qaw status auth-system-implementation

# auth-system-implementation
# Status: ✓ COMPLETED
# Agent: orchestrator-agent
# Task: Implement user authentication system with tests
# Duration: 28m 42s
#
# Log: .qaw/logs/auth-system-implementation.log
# Results: .qaw/results/auth-system-implementation
```

---

## Manager Agent Integration

These features are **essential** for the upcoming Manager Agent system:

### Manager Will Use:
```python
# Manager creates agents with semantic names
increment = "Add User model with email/password"
agent = state.create_agent(
    agent_name="backend-agent",
    task_id=task.id,
    task_description=increment,
    # Auto-generated: backend-add-user-model
)

# Manager spawns in autopilot mode
executor.spawn_agent(
    agent,
    trust_all_tools=True,
    autopilot=True,  # Long-running tasks supported
)

# Manager monitors multiple agents
agents = [
    "backend-add-user-model",      # 🔄 RUNNING
    "backend-add-password-hash",   # ⏳ PENDING
    "test-verify-user-model",      # ⏳ PENDING
    "alignment-check-user-model",  # ⏳ PENDING
]
```

### Benefits for Manager:
1. **Clear hierarchy**: manager-auth-system spawns backend-auth-login, test-verify-auth, etc.
2. **No timeouts**: Manager can orchestrate 20+ increments without timing out
3. **Easy tracking**: Semantic names make verification agent assignments obvious
4. **Historical audit**: Full history with readable agent names

---

## Implementation Details

### File Structure
```
qaw/
├── naming.py         # NEW: Semantic naming logic
├── state.py          # UPDATED: Stores semantic_name field
├── executor.py       # UPDATED: Autopilot keep-alive threads
├── cli.py            # UPDATED: --name and --autopilot flags
└── dashboard.py      # UPDATED: Display semantic names
```

### State Schema Changes
```python
@dataclass
class AgentState:
    id: str                      # Now uses semantic name as base
    semantic_name: Optional[str] # Human-readable name
    # ... rest unchanged
```

### Backwards Compatibility
- **Old agents** (without semantic_name): Display `id[:12]` as before
- **New agents**: Display semantic_name
- **No migration needed**: Old state files work fine

---

## Configuration

### Naming Customization
Edit stop words and abbreviations in `qaw/naming.py`:

```python
class AgentNamer:
    STOP_WORDS = {
        'the', 'a', 'an', ...
        # Add your stop words
    }
    
    ACTION_WORDS = {
        'add', 'create', 'fix', ...
        # Add your action words
    }
    
    abbreviations = {
        'authentication': 'auth',
        # Add your abbreviations
    }
```

### Autopilot Tuning
Edit keep-alive interval in `qaw/executor.py`:

```python
def keepalive_loop():
    interval = 30  # Change to desired seconds
    # ...
```

---

## Testing

### Test Semantic Naming
```python
from qaw.naming import AgentNamer

# Test various tasks
test_cases = [
    ("Add user authentication", "backend", "backend-auth-user"),
    ("Fix navbar bug", "frontend", "frontend-fix-navbar-bug"),
    ("Refactor database", "backend", "backend-refactor-db"),
]

for task, agent_type, expected in test_cases:
    result = AgentNamer.generate_name(task, agent_type)
    assert result == expected, f"Expected {expected}, got {result}"
```

### Test Autopilot
```bash
# Terminal 1: Start long-running agent
qaw submit "Sleep for 5 minutes" --agent test-agent --autopilot

# Terminal 2: Monitor status
watch -n 5 'qaw status test-sleep'

# Should see:
# - Agent stays RUNNING
# - Duration increments
# - Eventually completes
# - Keep-alive logs every 30s
```

---

## Future Enhancements

### Naming
- [ ] Machine learning for better term extraction
- [ ] Project-specific naming patterns (configured per workspace)
- [ ] Name conflict resolution (append counter if duplicate)
- [ ] Name templates (e.g., `{agent_type}-{date}-{action}`)

### Autopilot
- [ ] Configurable keep-alive intervals
- [ ] Progress indicators (heartbeat messages)
- [ ] Resource monitoring (CPU, memory)
- [ ] Automatic restart on unexpected crash
- [ ] Timeout limits (max autopilot duration)

---

## Summary

**Semantic Naming** and **Autopilot Mode** transform QAW from a manual agent runner to an autonomous development system:

✅ **Human-readable agent names** (backend-auth-login vs agent-7f3a9b2c)  
✅ **No timeout limits** (agents run until completion)  
✅ **Automatic monitoring** (keep-alive threads track health)  
✅ **Manager-ready** (foundation for autonomous orchestration)  
✅ **Dashboard-friendly** (clear, meaningful displays)  
✅ **Production-grade** (error handling, logging, thread safety)

These features are **essential prerequisites** for the Manager Agent system, enabling true autonomous agent teams that work while you're away.

**Next Steps**: Implement Manager Agent with context system and verification pipeline (see `MANAGER_AGENT_DESIGN.md`).
