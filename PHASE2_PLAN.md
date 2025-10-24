# Phase 2: Hooks & Enhanced Monitoring

**Duration**: 2-3 weeks
**Start**: After Phase 1 usage feedback
**Goal**: Automate repetitive tasks and improve observability

## Overview

Phase 2 transforms the workstation from a basic agent runner into an automated development workflow system. The focus is on eliminating manual steps and providing better visibility into agent activity.

## Core Additions

### 1. Hooks System (Week 1)

Add lifecycle automation to eliminate repetitive manual tasks.

#### Hook Types to Implement

**Pre-Spawn Hooks** - Run before agent starts
```bash
hooks/pre-spawn/
├── validate-env.sh       # Check dependencies
├── create-branch.sh      # Git branch creation
└── backup-state.sh       # Save current state
```

**Post-Completion Hooks** - Run after agent succeeds
```bash
hooks/post-completion/
├── format-code.sh        # Run prettier/black
├── lint.sh               # Run ESLint/pylint
├── run-tests.sh          # Execute test suite
├── commit.sh             # Auto-commit changes
└── notify.sh             # Send notification
```

**On-Error Hooks** - Run when agent fails
```bash
hooks/on-error/
├── log-error.sh          # Enhanced error logging
├── retry.sh              # Retry logic
├── notify-failure.sh     # Alert on failure
└── rollback.sh           # Revert changes
```

#### Implementation

**Hook Configuration (`qaw/hooks.py`)**
```python
class HookManager:
    def __init__(self, workspace_dir: Path):
        self.hooks_dir = workspace_dir / "hooks"
        self.config = self._load_config()
    
    def run_hook(self, hook_type: str, agent: AgentState):
        """Execute hooks for given lifecycle event."""
        hooks = self.config.get(hook_type, [])
        for hook_script in hooks:
            self._execute_hook(hook_script, agent)
    
    def _execute_hook(self, script: str, agent: AgentState):
        """Run single hook script with proper environment."""
        env = {
            'AGENT_ID': agent.id,
            'AGENT_NAME': agent.agent_name,
            'TASK_DESCRIPTION': agent.task_description,
            'LOG_FILE': agent.log_file,
            'RESULT_DIR': agent.result_dir,
        }
        subprocess.run([script], env=env, timeout=30)
```

**Hook Configuration File (`.qaw/config/hooks.json`)**
```json
{
  "hooks": {
    "pre-spawn": [
      "hooks/pre-spawn/validate-env.sh"
    ],
    "post-completion": [
      "hooks/post-completion/format-code.sh",
      "hooks/post-completion/run-tests.sh"
    ],
    "on-error": [
      "hooks/on-error/log-error.sh"
    ]
  },
  "hookTimeout": 30,
  "continueOnFailure": true
}
```

**Integration with Executor**
```python
# In executor.py - spawn_agent()
hook_manager.run_hook('pre-spawn', agent)
pid = self._spawn_process(agent)
hook_manager.run_hook('post-spawn', agent)

# In executor.py - _update_completed_agent()
if agent.status == AgentStatus.COMPLETED:
    hook_manager.run_hook('post-completion', agent)
elif agent.status == AgentStatus.FAILED:
    hook_manager.run_hook('on-error', agent)
```

#### Example Hooks

**Format Code Hook**
```bash
#!/bin/bash
# hooks/post-completion/format-code.sh

RESULT_DIR=$1

# Format Python files
find "$RESULT_DIR" -name "*.py" -exec black {} \;

# Format JavaScript/TypeScript
find "$RESULT_DIR" -name "*.ts" -o -name "*.tsx" -o -name "*.js" | \
  xargs prettier --write

echo "✓ Code formatted"
```

**Run Tests Hook**
```bash
#!/bin/bash
# hooks/post-completion/run-tests.sh

# Detect project type and run appropriate tests
if [ -f "package.json" ]; then
  npm test
elif [ -f "pytest.ini" ]; then
  pytest
fi
```

#### CLI Commands

```bash
# Manage hooks
qaw hooks list                    # Show configured hooks
qaw hooks enable format-code      # Enable a hook
qaw hooks disable format-code     # Disable a hook
qaw hooks run post-completion agent-123  # Manually run hooks
```

### 2. Enhanced Monitoring (Week 2)

Improve visibility and debugging capabilities.

#### Watch Mode

**Auto-refreshing status display**
```bash
qaw status --watch
# Refreshes every 2 seconds
# Shows live duration updates
# Highlights changes since last refresh
```

**Implementation**
```python
@cli.command()
@click.option('--watch', is_flag=True)
def status(watch: bool):
    if watch:
        while True:
            os.system('clear')
            display_status()
            time.sleep(2)
```

#### Better Log Parsing

**Structured log analysis**
```python
class LogAnalyzer:
    def analyze(self, log_file: str) -> LogSummary:
        """Extract key information from logs."""
        summary = LogSummary()
        
        with open(log_file) as f:
            for line in f:
                # Detect file operations
                if 'Creating:' in line:
                    summary.files_created.append(extract_path(line))
                
                # Detect tool usage
                if 'Using tool:' in line:
                    summary.tools_used.append(extract_tool(line))
                
                # Detect errors/warnings
                if any(word in line.lower() for word in ['error', 'failed']):
                    summary.errors.append(line)
        
        return summary
```

**Enhanced status display**
```bash
qaw status agent-123 --analyze

agent-123 (completed)
Duration: 2m 15s
Files: 3 created, 2 modified
Tools: fs_write (5x), grep (2x), execute_bash (1x)
Errors: None
```

#### Progress Indicators

**Show agent progress**
```python
class ProgressTracker:
    def estimate_progress(self, agent: AgentState) -> int:
        """Estimate completion percentage."""
        log_file = agent.log_file
        
        # Heuristics:
        # - Count tool uses
        # - Measure log file growth rate
        # - Parse progress indicators in logs
        
        return estimated_percentage
```

**Display**
```bash
qaw status

Agent ID        Status       Progress  Duration  Task
------------------------------------------------------------
🔄 agent-abc123 running      ▓▓▓▓▓░░░  1m 30s   Create login form...
                             60%
```

#### Resource Monitoring

**Track CPU and memory usage**
```python
class ResourceMonitor:
    def get_agent_resources(self, pid: int) -> ResourceUsage:
        """Get CPU/memory usage for agent process."""
        process = psutil.Process(pid)
        
        return ResourceUsage(
            cpu_percent=process.cpu_percent(interval=0.1),
            memory_mb=process.memory_info().rss / 1024 / 1024,
            num_threads=process.num_threads(),
        )
```

**Display**
```bash
qaw status agent-123 --resources

Resources:
  CPU: 45%
  Memory: 234 MB
  Threads: 12
```

### 3. Result Management (Week 2)

Better handling of agent outputs.

#### Diff Viewing

**Show what changed**
```bash
qaw diff agent-123
# Shows git-style diff of all changes

Modified files:
  src/Login.tsx      (+45, -0)
  src/api/auth.ts    (+23, -5)

Created files:
  src/types/auth.ts  (+15, -0)
```

**Implementation**
```python
class ResultManager:
    def generate_diff(self, agent_id: str) -> str:
        """Generate diff of agent changes."""
        # Track files before/after
        # Generate unified diff
        # Highlight key changes
```

#### Accept/Reject Workflow

**Review and apply changes**
```bash
# Review
qaw review agent-123
# Shows: files changed, tests status, linter results

# Accept all changes
qaw accept agent-123
# Copies files from result dir to working dir

# Reject (rollback)
qaw reject agent-123
# Discards all changes

# Partial accept
qaw accept agent-123 --only src/Login.tsx
```

## Technical Implementation

### New Files to Create

```
qaw/
├── hooks.py           # Hook management (200 lines)
├── monitor.py         # Resource monitoring (150 lines)
├── analyzer.py        # Log analysis (180 lines)
└── results.py         # Result management (160 lines)

hooks/                 # Hook scripts directory
├── pre-spawn/
│   ├── validate-env.sh
│   └── create-branch.sh
├── post-completion/
│   ├── format-code.sh
│   ├── lint.sh
│   └── run-tests.sh
└── on-error/
    ├── log-error.sh
    └── retry.sh
```

### Configuration Structure

```
.qaw/
├── config/
│   ├── hooks.json       # Hook configuration
│   ├── monitor.json     # Monitoring settings
│   └── system.json      # System settings
├── state/
├── logs/
├── results/
└── hooks/               # Symlink to project hooks/
```

### CLI Additions

```bash
# New commands
qaw hooks <subcommand>   # Manage hooks
qaw watch                # Live monitoring
qaw diff <agent-id>      # View changes
qaw review <agent-id>    # Review results
qaw accept <agent-id>    # Accept changes
qaw reject <agent-id>    # Reject changes

# Enhanced commands
qaw status --watch       # Auto-refresh
qaw status --analyze     # Deep analysis
qaw status --resources   # Show CPU/mem
qaw logs --analyze       # Structured analysis
```

## Success Metrics

### Week 1 (Hooks)
- [ ] 5+ useful hooks implemented
- [ ] Hook execution reliable
- [ ] 90% of formatting/testing automated
- [ ] Zero manual intervention for common tasks

### Week 2 (Monitoring)
- [ ] Watch mode functional
- [ ] Log analysis accurate
- [ ] Progress estimation reasonable
- [ ] Resource tracking working

### Week 3 (Polish)
- [ ] All commands stable
- [ ] Documentation complete
- [ ] Examples provided
- [ ] Ready for Phase 3

## Migration Path

Phase 1 users can upgrade seamlessly:
1. Run `./install.sh` to update
2. Existing workspaces continue working
3. Hooks are opt-in (disabled by default)
4. New commands don't break old workflows

## Phase 3 Preview

After Phase 2, the next focus will be:
1. **TUI Dashboard** - Live terminal UI with curses/textual
2. **Delegation** - True orchestrator pattern with sub-agents
3. **Dependencies** - Task graphs with wait conditions
4. **Persistence** - Resume interrupted workflows

## Estimated Timeline

```
Week 1: Hooks System
  Day 1-2: Hook manager implementation
  Day 3-4: Example hooks
  Day 5: Testing and docs

Week 2: Enhanced Monitoring
  Day 1-2: Watch mode and log analysis
  Day 3-4: Progress tracking and resources
  Day 5: Result management

Week 3: Polish & Integration
  Day 1-2: Bug fixes
  Day 3-4: Documentation
  Day 5: Release prep
```

## Why Phase 2 Matters

**Current Pain Points** (from Phase 1):
1. Manual code formatting after each agent
2. Must manually check if tests pass
3. Need to remember to commit changes
4. Hard to know "how far along" an agent is
5. Must manually review all changes

**Phase 2 Solutions**:
1. ✅ Format-code hook runs automatically
2. ✅ Run-tests hook validates output
3. ✅ Commit hook handles git operations
4. ✅ Progress indicator shows completion %
5. ✅ `qaw review` provides structured analysis

**Result**: 10x productivity boost for iterative development

## Getting Started with Phase 2

Once Phase 2 is available:

```bash
# Enable default hooks
qaw hooks init

# Submit with automatic formatting
qaw submit "Create login form" --hooks default

# Monitor with live updates
qaw watch

# Review structured output
qaw review agent-123

# Accept if good
qaw accept agent-123
```

This is the foundation for true "hyperdeveloping" where agents handle the tedious parts while you focus on the creative work.
