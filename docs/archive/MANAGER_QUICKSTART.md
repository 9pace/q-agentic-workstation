# Manager Agent Quick Start

**Natural language task orchestration is here!** 🚀

## What You Get

The Manager Agent provides:
- ✅ Natural language interface (`qaw chat`)
- ✅ Automatic task decomposition into <50 line increments  
- ✅ Project-aware context system (analyzes your codebase)
- ✅ Autonomous agent spawning with autopilot mode
- ✅ Basic verification and retry logic
- ✅ Interactive and non-interactive modes

## Installation

Ensure you have QAW installed with the latest features:

```bash
cd /path/to/q-agentic-workstation
pip install -e .
```

## Usage

### 1. Initialize in Your Project

```bash
cd your-project
qaw init
```

This creates `.qaw/` workspace in your project.

### 2. Chat with Manager

#### Interactive Mode

```bash
qaw chat
```

**Example session**:
```
💬  QAW Manager Chat (interactive mode)
Type your request, 'status' for current plan, 'execute' to run plan, or 'quit' to exit

👤 You: Add user authentication with JWT
 
🤖 Manager:
I'll break this into 3 increment(s):

1. ⏳ Add data model/schema: Add user authentication with JWT (~40 lines)
2. ⏳ Add API endpoint: Add user authentication with JWT (~45 lines)
3. ⏳ Add tests for: Add user authentication with JWT (~35 lines)

Total estimated: ~120 lines

Ready to proceed?

👤 You: execute

🚀 Executing plan...
🔄 Add data model/schema: Add user authentication with JWT [in_progress]
✓ Add data model/schema: Add user authentication with JWT [completed]
🔄 Add API endpoint: Add user authentication with JWT [in_progress]
...

✓ All increments completed!
```

#### Single Command Mode

```bash
# Just plan (no execution)
qaw chat "Add user authentication"

# Plan and execute automatically
qaw chat "Add login endpoint" --execute
```

### 3. Monitor Progress

While agents are running:

```bash
# In another terminal
qaw status

# Or launch dashboard
qaw dashboard
```

## How It Works

### Step 1: Context Analysis

On first run, Manager analyzes your project:

```
⚠️  Analyzing project for first time...
✓ Project context initialized

Detected: Python, JavaScript
Frameworks: React, Flask
Architecture: Component-based (likely frontend)
```

This creates:
- `.qaw/context/project_rules.md` - Tech stack, structure
- `.qaw/context/architecture.md` - Architecture patterns
- `.qaw/context/coding_standards.md` - Style guidelines
- `.qaw/context/constraints.md` - What NOT to do
- `.qaw/context/verification_rules.md` - Success criteria

### Step 2: Task Decomposition

Manager breaks your request into minimal increments:

**Your request**: "Add user authentication"

**Manager's plan**:
1. Add User model (backend, ~40 lines)
2. Add password hashing (backend, ~30 lines)
3. Add login endpoint (backend, ~45 lines)
4. Add JWT generation (backend, ~35 lines)
5. Add tests (test, ~40 lines)

Each increment:
- **<50 lines** (scope controlled)
- **Single responsibility**
- **Independently testable**
- **Dependencies tracked**

### Step 3: Execution with Autopilot

For each increment:
1. Spawns appropriate agent (backend-agent, frontend-agent, etc.)
2. **Autopilot mode enabled** - no timeout
3. **Auto-approval** - no interactive prompts
4. Monitors completion
5. Basic verification (checks logs for errors)
6. **Retries up to 3 times** if verification fails

### Step 4: Verification

Basic verification currently:
- ✅ Agent completed successfully
- ✅ No errors in log files
- ✅ Process exited cleanly

*(Full 3-stage verification with alignment/review/test agents coming in Phase 3)*

## Examples

### Example 1: Feature Addition

```bash
qaw chat "Add a todo list API with CRUD operations" --execute
```

Manager will:
1. Analyze: Detects API feature
2. Break down: Model → Routes → Tests
3. Execute: Spawns backend-agent for each
4. Verify: Checks completion

### Example 2: Bug Fix

```bash
qaw chat "Fix the login validation bug"
```

Manager's plan:
1. Investigate and fix (backend)
2. Add regression test (test)

Then type `execute` to run.

### Example 3: Refactoring

```bash
qaw chat "Refactor the user service to use async/await"
```

Manager ensures:
- Small incremental changes
- Tests verify behavior unchanged
- No scope creep

## Interactive Commands

In `qaw chat` interactive mode:

| Command | Action |
|---------|--------|
| `[your request]` | Create plan for request |
| `execute` or `run` | Execute current plan |
| `status` | Show current plan status |
| `quit` or `exit` | Exit chat |

## Advanced Options

```bash
# Verbose output (see detailed logs)
qaw chat --verbose

# One-shot execution
qaw chat "Add feature X" --execute

# Check what was done
qaw status
qaw logs backend-add-feature-x
```

## Project Context

Manager uses context from `.qaw/context/` to:
- **Match your tech stack** (spawns right agent types)
- **Follow your patterns** (naming conventions, style)
- **Respect constraints** (<50 lines, no refactoring without request)
- **Use your test framework** (pytest, jest, etc.)

You can edit these files to customize Manager's behavior!

## Configuration

All auto-generated context in `.qaw/context/`:
- `project_context.json` - Full context data
- `*.md` - Human-readable steering documents

Regenerate context:
```bash
rm .qaw/context/project_context.json
qaw chat "test"  # Will re-analyze
```

## Limitations (Current MVP)

✅ **What Works**:
- Natural language task breakdown
- Heuristic-based decomposition (add/fix/refactor/test)
- Project context analysis
- Autonomous execution with autopilot
- Basic verification and retry
- Semantic agent naming

⚠️ **What's Coming**:
- Full 3-stage verification (alignment, review, tests)
- LLM-based task decomposition (vs heuristics)
- Chat interface in dashboard
- Verification agent configs
- Advanced scope control
- Dependency-aware execution

## Troubleshooting

**"Workspace not initialized"**:
```bash
qaw init
```

**"No agents directory found"**:
Make sure Q CLI agent configs are installed:
```bash
ls ~/.aws/amazonq/cli-agents/
# Should see: orchestrator-agent.json, backend-agent.json, etc.
```

**Agent fails repeatedly**:
Check logs:
```bash
qaw logs [agent-id]
```

**Want to see what Manager is thinking**:
```bash
qaw chat --verbose
```

## Real World Example

Let's build a feature end-to-end:

```bash
$ cd my-flask-react-app
$ qaw init
✓ Initialized Q Agentic Workstation

$ qaw chat

💬  QAW Manager Chat
👤 You: Add user registration with email validation

🤖 Manager:
I'll break this into 4 increment(s):

1. ⏳ Add data model/schema: Add user registration with email validation (~40 lines)
2. ⏳ Add API endpoint: Add user registration with email validation (~45 lines)
3. ⏳ Add UI component: Add user registration with email validation (~50 lines)
4. ⏳ Add tests for: Add user registration with email validation (~35 lines)

Total estimated: ~170 lines

Ready to proceed?

👤 You: execute

🚀 Executing plan...
🔄 Add data model/schema [in_progress]
✓ Add data model/schema [completed]
🔄 Add API endpoint [in_progress]
✓ Add API endpoint [completed]
🔄 Add UI component [in_progress]
✓ Add UI component [completed]
🔄 Add tests [in_progress]
✓ Add tests [completed]

✓ All increments completed!

👤 You: quit
```

Check results:
```bash
$ qaw status
# Shows all agents completed

$ ls .qaw/results/
backend-add-data-model/
backend-add-api-ep/
frontend-add-ui-comp/
test-add-tests/

$ git diff
# See all changes made by agents
```

## Next Steps

1. **Try it out**: `qaw chat` in your project
2. **Customize**: Edit `.qaw/context/*.md` files
3. **Monitor**: Use `qaw dashboard` for live updates
4. **Integrate**: Add to your workflow

**The Manager Agent handles the orchestration, you focus on reviewing and merging!** 🎉

## Tips

- **Start small**: Try simple requests first ("Fix bug X", "Add test for Y")
- **Be specific**: "Add JWT authentication" is better than "improve security"
- **Review changes**: Always `git diff` before committing
- **Iterate**: If plan isn't right, try rewording your request
- **Use status**: Check progress with `qaw status` or `qaw chat` → `status`

---

**Ready to delegate to your AI team?** 

```bash
qaw chat "Let's build something amazing"
```
