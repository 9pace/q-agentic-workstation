# Getting Started with Q Agentic Workstation

## Prerequisites

1. **Amazon Q CLI** installed and configured
   ```bash
   # Check installation
   q --version
   
   # Login if needed
   q login
   ```

2. **Git** for version control
   ```bash
   git --version
   ```

3. **Node.js/Python** (depending on your project)

## Quick Start (5 minutes)

### 1. Install Agent Configs

Copy the agent configurations to Q CLI's agent directory:

```bash
# From q-agentic-workstation directory
cp agents/*.json ~/.aws/amazonq/cli-agents/

# Verify agents are available
q agent list
```

You should see:
- `orchestrator-agent`
- `frontend-agent`
- `backend-agent`
- `test-agent`
- `doc-agent`

### 2. Test Basic Agent Execution

Try running a simple task with an agent:

```bash
# Test the frontend agent
q chat --agent frontend-agent \
  --no-interactive \
  "Create a simple Hello World React component in hello.tsx"
```

Watch the output - you should see the agent:
1. Analyze the request
2. Create the file
3. Write the component code
4. Complete the task

### 3. Test Orchestrator with Delegation

Now test the orchestrator's ability to delegate:

```bash
q chat --agent orchestrator-agent \
  "Create a simple TODO list component with a backend API endpoint"
```

The orchestrator should:
1. Break down the task
2. Identify need for frontend + backend work
3. Use the `delegate` tool to spawn specialized agents
4. Coordinate their work

### 4. Set Up Your First Project

```bash
# Navigate to your project directory
cd /path/to/your/project

# Initialize Q Agentic Workstation structure
mkdir -p .qaw/{state,logs,results,config}

# Create basic config
cat > .qaw/config/system.json <<EOF
{
  "agents": {
    "orchestrator": "orchestrator-agent",
    "maxConcurrent": 3,
    "defaultTimeout": 1800
  }
}
EOF
```

## Your First Hyperdeveloping Session

### Scenario: Add a Feature

Let's say you want to add a user profile feature to your app.

#### Traditional Approach (Sequential)
```
You: "Add user profile"
Agent: [creates UI]
You: "Now add the API"
Agent: [creates API]
You: "Now add tests"
Agent: [creates tests]
...runs out of context or goes on tangent...
You: Start over with new chat
```

**Time**: 30-45 minutes
**Context switches**: Multiple
**Risk**: High (loses context, tangents)

#### Hyperdeveloping Approach (Parallel)
```bash
q chat --agent orchestrator-agent \
  "Add user profile feature with UI, API, tests, and docs"
```

The orchestrator:
1. **Analyzes** (30 seconds)
2. **Delegates** to specialists (parallel):
   - Frontend agent → UI (5 minutes)
   - Backend agent → API (5 minutes)
   - Test agent → Tests (after code complete, 3 minutes)
   - Doc agent → Docs (parallel with tests, 2 minutes)
3. **Coordinates** results

**Time**: 8-12 minutes
**Context switches**: Zero (agents work autonomously)
**Risk**: Low (specialized agents, clear boundaries)

### Running Your First Hyperdeveloping Task

```bash
# Start with a real task from your project
q chat --agent orchestrator-agent \
  --no-interactive \
  "Add a settings page where users can update their email and password"
```

Watch what happens:
1. Orchestrator analyzes and plans
2. Spawns frontend-agent for UI
3. Spawns backend-agent for API
4. After both complete, spawns test-agent
5. Spawns doc-agent for documentation

Each agent works independently, you can:
- Continue other work
- Check status anytime
- Review results when done

## Understanding Agent Execution

### Interactive Mode (Default)
```bash
q chat --agent orchestrator-agent "Your task"
```
- You stay connected to the chat
- See output in real-time
- Can provide guidance/corrections
- Good for: Learning, debugging, complex decisions

### Non-Interactive Mode (Autonomous)
```bash
q chat --agent orchestrator-agent \
  --no-interactive \
  --trust-all-tools \
  "Your task" > output.log 2>&1 &
```
- Agent runs in background
- No human intervention needed
- Saves output to log file
- Good for: Hyperdeveloping, batch processing

## Best Practices for Beginners

### 1. Start Small
```bash
# Good first task
q chat --agent frontend-agent "Create a loading spinner component"

# Too complex for first time
q chat --agent orchestrator-agent "Rebuild entire application architecture"
```

### 2. Be Specific
```bash
# Good - specific and clear
"Create a React login form with email and password fields, using TypeScript and styled-components"

# Bad - vague
"make a login thing"
```

### 3. Use the Right Agent
```bash
# Frontend work? Use frontend-agent
q chat --agent frontend-agent "Create navigation bar"

# Full feature? Use orchestrator
q chat --agent orchestrator-agent "Add user authentication"

# Just tests? Use test-agent
q chat --agent test-agent "Write tests for Login.tsx"
```

### 4. Review Before Accepting
Don't blindly accept agent output:
```bash
# Review the changes
cat src/components/LoginForm.tsx

# Test it
npm test

# Then decide
# - Accept if good
# - Modify if needs tweaking
# - Reject if wrong approach
```

## Common Patterns

### Pattern 1: Feature Development
```bash
q chat --agent orchestrator-agent \
  "Add [feature name] with UI, API, tests, and documentation"
```

### Pattern 2: Bug Fix
```bash
q chat --agent backend-agent \
  "Fix the authentication bug where tokens expire too early"
```

### Pattern 3: Refactoring
```bash
q chat --agent frontend-agent \
  "Refactor UserProfile component to use hooks instead of class components"
```

### Pattern 4: Testing
```bash
q chat --agent test-agent \
  "Write comprehensive tests for the AuthService class"
```

### Pattern 5: Documentation
```bash
q chat --agent doc-agent \
  "Document all API endpoints in the auth router"
```

## Troubleshooting

### Agent Not Found
```bash
# Error: agent 'frontend-agent' not found

# Solution: Check agent list
q agent list

# Make sure agent config is in the right place
ls ~/.aws/amazonq/cli-agents/frontend-agent.json
```

### Agent Runs But Does Nothing
```bash
# Possible causes:
# 1. Task too vague
# 2. Missing context
# 3. Agent lacks necessary tools

# Solution: Be more specific
q chat --agent frontend-agent \
  "In the src/components directory, create a new file Button.tsx with a reusable button component"
```

### Agent Creates Wrong Files
```bash
# Solution: Specify paths explicitly
q chat --agent backend-agent \
  "In the src/api/routes directory, create auth.ts with login and logout endpoints"
```

### Delegate Tool Not Working
```bash
# Make sure orchestrator has delegate in allowedTools
cat ~/.aws/amazonq/cli-agents/orchestrator-agent.json

# Should include:
# "allowedTools": ["delegate", ...]
```

## Next Steps

1. **Read the Architecture** - [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **Study Integration Patterns** - [INTEGRATION.md](./INTEGRATION.md)
3. **Learn About Hooks** - [HOOKS.md](./HOOKS.md)
4. **Try Example Workflow** - [examples/full-stack-feature.md](../examples/full-stack-feature.md)
5. **Set Up Control Center** - [CONTROL_CENTER.md](./CONTROL_CENTER.md)

## Getting Help

1. **Check agent logs** - Agents output detailed logs
2. **Use verbose mode** - Add `-v` or `--verbose` flags
3. **Start simple** - Test with small tasks first
4. **Experiment** - The best way to learn is by trying

## Feedback & Iteration

The Q Agentic Workstation is designed to evolve with your workflow:

1. Start with basic agents
2. Notice patterns in your work
3. Create specialized agents for your needs
4. Add hooks for repetitive tasks
5. Share successful patterns with team

Happy Hyperdeveloping! 🚀
