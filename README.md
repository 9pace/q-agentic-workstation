# Q Agentic Workstation

An experimental framework for parallel, asynchronous agent-driven development using Amazon Q CLI.

## Vision

**Hyperdeveloping**: Instead of sequential, context-consuming interactions, spawn multiple specialized agents that work on subtasks in parallel. Review their work asynchronously at your convenience.

## Key Concepts

- **Parallel Agent Spawning**: Each subtask gets its own agent instance
- **Async Execution**: Agents work independently without blocking your workflow
- **Control Center**: Monitor all active agents, their status, and outputs
- **Delegate Pattern**: Agents can spawn sub-agents for complex tasks
- **Hooks Integration**: Automate agent lifecycle and response handling

## Repository Structure

```
q-agentic-workstation/
├── docs/              # Design documentation
├── agents/            # Agent configurations
├── hooks/             # Automation scripts and hooks
├── control-center/    # Monitoring and control dashboard
└── examples/          # Example workflows and use cases
```

## Getting Started

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design details.

## 🤖 Manager-First Interface

**NEW**: Natural language development with intelligent orchestration!

```bash
qaw app
```

**Revolutionary Workflow**:
1. 💬 **Describe your task** in plain English
2. 🧠 **Manager breaks it down** into small, testable increments
3. 🚀 **Agents execute** each step automatically
4. 👀 **Watch live progress** in beautiful TUI

**Key Features**:
- 💬 Integrated chat with Manager Agent
- 📋 Live execution plan with status tracking
- 🔄 Real-time agent monitoring
- ✅ Automatic retry and verification
- 🧠 Context-aware task decomposition
- 🎨 Production-quality terminal UI

See [docs/MANAGER_DASHBOARD.md](docs/MANAGER_DASHBOARD.md) for complete guide.

## Quick Start

### The Manager-First Way (Recommended)

```bash
# Install
./install.sh

# Navigate to your project
cd my-project

# Initialize workspace
qaw init

# Launch the Manager-first interface
qaw app

# In the dashboard:
# 1. Type: "Add user authentication with login and signup"
# 2. Review the plan (Manager breaks it into increments)
# 3. Click "Execute" and watch agents work!
```

### Manual Control (Advanced)

```bash
# Submit specific tasks to agents
qaw submit "Create login component" --agent frontend-agent
qaw submit "Add /api/auth endpoint" --agent backend-agent

# Monitor with CLI
qaw status
qaw logs <agent-id>

# Or chat interface
qaw chat "What should I work on?"
```

See [QUICKSTART.md](QUICKSTART.md) for more examples.

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[DASHBOARD.md](DASHBOARD.md)** - TUI dashboard guide
- **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)** - Detailed tutorial
- **[TEST_RESULTS.md](TEST_RESULTS.md)** - Comprehensive testing report
- **[PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)** - What's available now
- **[PHASE2_PLAN.md](PHASE2_PLAN.md)** - What's coming next

## Status

✅ **Phase 1 Complete - Production Ready**

Fully functional MVP with:
- CLI interface (`qaw` command)
- **TUI Dashboard** (interactive monitoring)
- Parallel agent execution
- State management & persistence
- Process monitoring & control
- Comprehensive documentation
- 18/18 tests passing
