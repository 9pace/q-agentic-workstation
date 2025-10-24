# Quick Start Guide

## Installation (One Time)

```bash
cd /Users/paceben/PERSONAL/q-agentic-workstation
./install.sh
```

## Basic Workflow

### 1. Initialize Workspace
```bash
cd your-project
qaw init
```

### 2. Submit a Task
```bash
# Use orchestrator for complex tasks
qaw submit "Add user authentication with login form and API" --agent orchestrator-agent

# Use specialist agents for specific tasks
qaw submit "Create a React navbar component" --agent frontend-agent
qaw submit "Add GET /users endpoint" --agent backend-agent
qaw submit "Write tests for auth service" --agent test-agent
```

### 3. Monitor Progress
```bash
# View all agents
qaw status

# View specific agent
qaw status agent-abc123

# View with recent logs
qaw status agent-abc123 --verbose
```

### 4. View Logs
```bash
# Show last 50 lines
qaw logs agent-abc123

# Show last 100 lines
qaw logs agent-abc123 --lines 100

# Follow live (like tail -f)
qaw logs agent-abc123 --follow
```

### 5. Stop Agent (if needed)
```bash
# Graceful stop
qaw stop agent-abc123

# Force kill
qaw stop agent-abc123 --force
```

## Common Patterns

### Frontend Development
```bash
qaw submit "Create a user profile page with avatar upload" --agent frontend-agent
```

### Backend Development
```bash
qaw submit "Add REST API endpoint for user profile CRUD operations" --agent backend-agent
```

### Testing
```bash
qaw submit "Write comprehensive unit tests for UserService class" --agent test-agent
```

### Documentation
```bash
qaw submit "Document all API endpoints in the auth router" --agent doc-agent
```

### Full Feature (Orchestrator)
```bash
qaw submit "Add search functionality with UI, API, and tests" --agent orchestrator-agent
```

## Advanced Usage

### Wait for Completion
```bash
qaw submit "Create component" --agent frontend-agent --wait
# Blocks until agent completes
```

### Higher Priority
```bash
qaw submit "URGENT: Fix login bug" --agent backend-agent --priority critical
```

### Trust All Tools (No Confirmation)
```bash
qaw submit "Refactor auth module" --agent backend-agent --trust-all-tools
```

## Checking Results

### View Created Files
```bash
# Files are created in your current directory
ls -la

# Or check agent's result directory
ls -la .qaw/results/agent-abc123/
```

### Read Agent Logs
```bash
# Direct file access
cat .qaw/logs/agent-abc123.log

# Or use qaw command
qaw logs agent-abc123
```

## Troubleshooting

### Agent Not Found
```bash
# List available agents
q agent list
```

### Check Workspace
```bash
# Verify .qaw directory exists
ls -la .qaw/

# Reinitialize if needed
qaw init
```

### Cleanup Stale Agents
```bash
qaw cleanup
```

### View All Agent History
```bash
qaw status --all
```

## Tips

1. **Use specific instructions**: Instead of "create a component", say "create a React functional component with TypeScript, props for title and onClick handler"

2. **Check status frequently**: Agents run in background, check `qaw status` to see when they complete

3. **Review before using**: Always review agent output before using in production:
   ```bash
   qaw logs agent-abc123
   cat created-file.tsx
   ```

4. **Use the right agent**:
   - Frontend work → `frontend-agent`
   - Backend/API → `backend-agent`
   - Tests → `test-agent`
   - Docs → `doc-agent`
   - Complex multi-part → `orchestrator-agent`

5. **Keep tasks focused**: Break large tasks into smaller, specific subtasks for better results

## Example Session

```bash
# Start fresh
cd ~/my-app
qaw init

# Submit frontend task
qaw submit "Create login form with email/password fields and submit button" --agent frontend-agent

# Submit backend task (runs in parallel!)
qaw submit "Create POST /api/login endpoint with JWT" --agent backend-agent

# Check status
qaw status
# 🔄 agent-abc123  running   frontend-agent   30s   Create login form...
# 🔄 agent-def456  running   backend-agent    25s   Create POST /api/login...

# Wait a bit...
sleep 60
qaw status
# ✓ agent-abc123  completed frontend-agent   1m 15s   Create login form...
# ✓ agent-def456  completed backend-agent    1m 20s   Create POST /api/login...

# Review output
qaw logs agent-abc123
qaw logs agent-def456

# Check created files
ls -la
# LoginForm.tsx
# api/auth.js

# Use the code!
```

## Next Steps

- Read [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) for detailed guide
- See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
- Check [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) for what's available now

## Getting Help

```bash
# Command help
qaw --help
qaw submit --help
qaw status --help

# Check version
qaw --version
```
