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

## ✨ Beautiful TUI Dashboard

**NEW**: Launch the interactive control center!

```bash
qaw dashboard
```

**Features**:
- 📊 Live statistics with auto-refresh (every 2s)
- 🤖 Interactive agent table with selection
- 🔍 Detailed agent information panel
- ⚡ Quick actions (refresh, cleanup, stop, kill, view logs)
- ⌨️  Full keyboard shortcuts
- 🎨 Professional UI with color coding
- 🚀 Real-time monitoring without polling

See [DASHBOARD.md](DASHBOARD.md) for complete documentation.

## Quick Start

```bash
# Install
./install.sh

# Navigate to your project
cd my-project

# Initialize workspace
qaw init

# Submit tasks
qaw submit "Create login component" --agent frontend-agent
qaw submit "Add /api/auth endpoint" --agent backend-agent

# Launch dashboard
qaw dashboard

# Or use CLI
qaw status
qaw logs <agent-id>
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
