# Integration Guide: Hooks, Agents, and Delegate

## Overview

This document describes how the three core primitives of Q CLI—**hooks**, **agents**, and **delegate**—integrate to enable the hyperdeveloping workflow.

## Core Primitives

### 1. Agents
**What**: Configured AI assistants with specific capabilities and permissions

**How**: JSON config files defining tools, allowed actions, and behavior
```json
{
  "name": "orchestrator-agent",
  "description": "Breaks down tasks and delegates to specialists",
  "tools": ["@builtin"],
  "allowedTools": ["delegate", "todo_list", "fs_read"]
}
```

### 2. Delegate
**What**: Built-in Q CLI tool that allows agents to spawn sub-agents

**How**: Agents use the `delegate` tool to create specialized sub-agents for subtasks
```bash
# Agent internally calls:
delegate --agent test-agent "Write unit tests for Login.tsx"
```

### 3. Hooks
**What**: Lifecycle automation scripts triggered at key execution points

**How**: Shell scripts/programs that run before/after agent events
```bash
# hooks/post-completion/run-tests.sh
./test-suite.sh $RESULT_DIR
```

## Integration Patterns

### Pattern 1: Orchestrator → Delegate → Hooks

**Scenario**: User submits complex task that requires multiple specialists

**Flow**:
```
User: "Build login feature with tests and docs"
  ↓
Orchestrator Agent
  ├─ [PRE-SPAWN HOOK] Validate environment
  ├─ Analyze task & create plan
  ├─ DELEGATE → Dev Agent: "Implement login UI"
  │   ├─ [POST-SPAWN HOOK] Notify start
  │   ├─ Write code
  │   └─ [POST-COMPLETION HOOK] Format code
  ├─ DELEGATE → Test Agent: "Write tests"
  │   ├─ [POST-SPAWN HOOK] Notify start
  │   ├─ Write tests
  │   └─ [POST-COMPLETION HOOK] Run tests
  └─ DELEGATE → Doc Agent: "Update docs"
      ├─ [POST-SPAWN HOOK] Notify start
      ├─ Write docs
      └─ [POST-COMPLETION HOOK] Build docs
```

**Implementation**:
```bash
# User command
qaw submit "Build login feature with tests and docs"

# System spawns orchestrator
q chat --agent orchestrator-agent \
  --no-interactive \
  --trust-all-tools \
  "Build login feature with tests and docs" &

# Orchestrator internally uses delegate
# Q CLI handles spawning sub-agents
# Hooks automatically trigger at each stage
```

### Pattern 2: Sequential Delegation with Dependencies

**Scenario**: Tasks that must run in order (e.g., build → test → deploy)

**Flow**:
```
Orchestrator
  ↓
DELEGATE → Build Agent
  ├─ Build application
  └─ [POST-COMPLETION HOOK] Validate build
      ↓ (on success)
      DELEGATE → Test Agent
        ├─ Run test suite
        └─ [POST-COMPLETION HOOK] Check coverage
            ↓ (on success)
            DELEGATE → Deploy Agent
              ├─ Deploy to staging
              └─ [POST-COMPLETION HOOK] Smoke test
```

**Implementation**:
```json
// Orchestrator agent config
{
  "name": "orchestrator-agent",
  "allowedTools": ["delegate", "todo_list"],
  "hooks": {
    "post-completion": ["hooks/orchestrator/aggregate-results.sh"]
  }
}
```

```bash
# hooks/post-completion/trigger-next-stage.sh
#!/bin/bash
AGENT_ID=$1
STATUS=$(jq -r .status .qaw/state/agents/agent-$AGENT_ID.json)

if [ "$STATUS" = "success" ]; then
  # Trigger next stage
  NEXT_STAGE=$(jq -r .metadata.nextStage .qaw/state/agents/agent-$AGENT_ID.json)
  if [ "$NEXT_STAGE" != "null" ]; then
    qaw spawn --agent $NEXT_STAGE
  fi
fi
```

### Pattern 3: Parallel Delegation with Synchronization

**Scenario**: Independent tasks that can run simultaneously, then merge

**Flow**:
```
Orchestrator
  ├─ DELEGATE → Frontend Agent (parallel)
  ├─ DELEGATE → Backend Agent (parallel)
  └─ DELEGATE → Database Agent (parallel)
      ↓ (all complete)
      [POST-COMPLETION HOOK] Merge & validate
      ↓
      DELEGATE → Integration Test Agent
```

**Implementation**:
```bash
# hooks/orchestrator/sync-parallel-agents.sh
#!/bin/bash

# Wait for all parallel agents to complete
AGENT_IDS=("$@")
while true; do
  all_done=true
  for id in "${AGENT_IDS[@]}"; do
    status=$(jq -r .status .qaw/state/agents/agent-$id.json)
    if [ "$status" != "completed" ]; then
      all_done=false
      break
    fi
  done
  
  if [ "$all_done" = true ]; then
    # All done - spawn integration agent
    qaw spawn --agent integration-test-agent
    break
  fi
  sleep 5
done
```

### Pattern 4: Dynamic Delegation Based on Results

**Scenario**: Next steps depend on what previous agent discovered

**Flow**:
```
Analysis Agent
  ├─ Analyze codebase
  └─ [POST-COMPLETION HOOK] Parse results
      ├─ If bugs found → DELEGATE → Bug Fix Agent
      ├─ If performance issues → DELEGATE → Optimization Agent
      └─ If security concerns → DELEGATE → Security Agent
```

**Implementation**:
```bash
# hooks/analysis-agent/dynamic-delegate.sh
#!/bin/bash
AGENT_ID=$1
RESULT_FILE=.qaw/results/agent-$AGENT_ID/analysis.json

# Parse analysis results
BUGS=$(jq -r '.bugs | length' $RESULT_FILE)
PERF_ISSUES=$(jq -r '.performance | length' $RESULT_FILE)
SECURITY=$(jq -r '.security | length' $RESULT_FILE)

# Spawn appropriate agents
if [ $BUGS -gt 0 ]; then
  qaw spawn --agent bug-fix-agent \
    --context "$(jq .bugs $RESULT_FILE)"
fi

if [ $PERF_ISSUES -gt 0 ]; then
  qaw spawn --agent optimization-agent \
    --context "$(jq .performance $RESULT_FILE)"
fi

if [ $SECURITY -gt 0 ]; then
  qaw spawn --agent security-agent \
    --context "$(jq .security $RESULT_FILE)"
fi
```

### Pattern 5: Retry with Escalation

**Scenario**: Agent fails, retry with hooks, escalate if still failing

**Flow**:
```
Agent starts
  ↓
ERROR
  ↓
[ON-ERROR HOOK] Attempt 1
  ├─ Retry same agent
  ↓ (if fails)
  [ON-ERROR HOOK] Attempt 2
  ├─ Retry with modified config
  ↓ (if fails)
  [ON-ERROR HOOK] Attempt 3
  └─ DELEGATE → Senior Agent (more powerful model)
```

**Implementation**:
```bash
# hooks/on-error/escalate.sh
#!/bin/bash
AGENT_ID=$1
ERROR_MSG=$2
ATTEMPT=$(jq -r .attempt .qaw/state/agents/agent-$AGENT_ID.json)

if [ $ATTEMPT -eq 1 ]; then
  # Retry with same agent
  qaw retry $AGENT_ID
elif [ $ATTEMPT -eq 2 ]; then
  # Retry with more context
  qaw retry $AGENT_ID --add-context "$(cat error-logs.txt)"
else
  # Escalate to senior agent
  TASK=$(jq -r .task.description .qaw/state/agents/agent-$AGENT_ID.json)
  qaw spawn --agent senior-agent \
    --priority critical \
    "Previous agent failed after 3 attempts: $TASK\nError: $ERROR_MSG"
fi
```

## Complete Example: Full-Stack Feature Development

### User Request
```bash
qaw submit "Add user profile page with avatar upload"
```

### Execution Flow

#### 1. Orchestrator Agent Spawns
```bash
q chat --agent orchestrator-agent \
  --no-interactive \
  --trust-all-tools \
  "Add user profile page with avatar upload"
```

**Orchestrator analyzes and creates plan:**
```
1. Frontend: Create profile UI component
2. Backend: Add profile API endpoints
3. Storage: Setup avatar upload to S3
4. Tests: Write E2E tests
5. Docs: Update API documentation
```

#### 2. Pre-Spawn Hooks Run
```bash
# hooks/pre-spawn/create-feature-branch.sh
git checkout -b feature/user-profile

# hooks/pre-spawn/notify-team.sh
slack-send "Starting: User profile feature development"
```

#### 3. Orchestrator Delegates (Parallel)
```bash
# Internally, orchestrator uses delegate tool
# Q CLI spawns these agents in parallel:

Agent A: frontend-agent  "Create profile UI"
Agent B: backend-agent   "Add profile API"
Agent C: storage-agent   "Setup S3 avatar upload"
```

#### 4. Each Agent Runs with Hooks
```
Agent A (Frontend)
  ├─ [POST-SPAWN] Notify start
  ├─ Create ProfilePage.tsx
  ├─ Create AvatarUpload.tsx
  ├─ Add routing
  └─ [POST-COMPLETION]
      ├─ Run ESLint
      ├─ Run Prettier
      └─ Build for type errors

Agent B (Backend)
  ├─ [POST-SPAWN] Notify start
  ├─ Create /api/profile endpoint
  ├─ Add profile controller
  ├─ Update routes
  └─ [POST-COMPLETION]
      ├─ Run linter
      └─ Check Swagger docs

Agent C (Storage)
  ├─ [POST-SPAWN] Notify start
  ├─ Configure S3 client
  ├─ Create upload handler
  ├─ Add image processing
  └─ [POST-COMPLETION]
      └─ Test upload locally
```

#### 5. Synchronization Hook
```bash
# hooks/orchestrator/wait-for-all.sh
# Waits for agents A, B, C to complete
# Then triggers next phase
```

#### 6. Orchestrator Delegates (Sequential)
```bash
Agent D: test-agent  "Write E2E tests for profile page"
  ├─ [POST-COMPLETION]
      └─ Run tests
          └─ [ON-SUCCESS] → Agent E
          └─ [ON-FAILURE] → ON-ERROR HOOK

Agent E: doc-agent  "Update API docs"
  ├─ [POST-COMPLETION]
      └─ Build docs
```

#### 7. Final Aggregation Hook
```bash
# hooks/orchestrator/finalize.sh
# Collect all results
# Create summary
# Run full test suite
# Create commit
# Notify completion
```

#### 8. User Reviews
```bash
# User gets notification
qaw status  # See all completed agents

qaw review orchestrator-agent-123
# Shows:
# - 5 agents completed successfully
# - 12 files created/modified
# - All tests passing
# - Ready for review

qaw diff  # Show all changes

qaw accept  # Merge all changes
# or
qaw reject  # Rollback everything
```

## Configuration Files

### Global Config
```json
// .qaw/config/system.json
{
  "agents": {
    "orchestrator": "orchestrator-agent",
    "maxConcurrent": 5,
    "defaultTimeout": 1800
  },
  "hooks": {
    "enabled": true,
    "timeout": 30,
    "continueOnFailure": false
  },
  "notifications": {
    "slack": true,
    "desktop": true,
    "email": false
  }
}
```

### Agent Registry
```json
// .qaw/config/agents.json
{
  "agents": {
    "orchestrator-agent": {
      "path": "~/.aws/amazonq/cli-agents/orchestrator.json",
      "canDelegate": true,
      "maxDelegations": 10
    },
    "frontend-agent": {
      "path": "agents/frontend-agent.json",
      "specialization": "react,typescript,ui"
    },
    "backend-agent": {
      "path": "agents/backend-agent.json",
      "specialization": "node,api,database"
    }
  }
}
```

### Hook Registry
```json
// .qaw/config/hooks.json
{
  "global": {
    "pre-spawn": ["hooks/pre-spawn/validate-env.sh"],
    "post-completion": ["hooks/post-completion/format-code.sh"]
  },
  "agents": {
    "orchestrator-agent": {
      "post-completion": ["hooks/orchestrator/aggregate-results.sh"]
    },
    "test-agent": {
      "post-completion": ["hooks/test-agent/run-tests.sh"]
    }
  }
}
```

## Best Practices

### 1. Design Agents for Single Responsibilities
```json
// Good: Specialized agents
{"name": "react-component-agent"}
{"name": "api-endpoint-agent"}
{"name": "database-migration-agent"}

// Bad: Generic agents
{"name": "full-stack-agent"}  // Too broad
```

### 2. Use Hooks for Cross-Cutting Concerns
```bash
# Good: Hooks handle automation
hooks/post-completion/format-code.sh
hooks/post-completion/run-linter.sh

# Bad: Agents doing formatting
# (wastes tokens, inconsistent)
```

### 3. Delegate with Clear Instructions
```bash
# Good: Specific delegation
delegate --agent test-agent \
  "Write Jest tests for Login.tsx component covering all user interactions"

# Bad: Vague delegation
delegate --agent test-agent "test the login"
```

### 4. Handle Errors Gracefully
```bash
# hooks/on-error/handle-error.sh
#!/bin/bash
AGENT_ID=$1
ERROR=$2

# Log error
echo "$ERROR" >> .qaw/logs/errors.log

# Attempt recovery
if [[ "$ERROR" == *"timeout"* ]]; then
  qaw retry $AGENT_ID --extend-timeout
elif [[ "$ERROR" == *"permission"* ]]; then
  qaw notify escalate "Permission issue: $AGENT_ID"
fi
```

### 5. Monitor Resource Usage
```bash
# hooks/on-progress/monitor-resources.sh
#!/bin/bash
AGENT_ID=$1
PID=$(cat .qaw/pids/agent-$AGENT_ID.pid)

# Check resource usage
CPU=$(ps -p $PID -o %cpu | tail -1)
MEM=$(ps -p $PID -o %mem | tail -1)

if (( $(echo "$CPU > 80" | bc -l) )); then
  echo "WARN: Agent $AGENT_ID using ${CPU}% CPU"
fi
```

## Debugging Integration Issues

### Enable Debug Logging
```bash
export QAW_DEBUG=1
export QAW_DEBUG_HOOKS=1
export QAW_DEBUG_DELEGATE=1

qaw submit "Test task" --verbose
```

### Trace Delegation Chain
```bash
# View delegation tree
qaw trace orchestrator-agent-123

# Output:
# orchestrator-agent-123
# ├── frontend-agent-456
# ├── backend-agent-789
# │   └── database-agent-101
# └── test-agent-112
```

### Inspect Hook Execution
```bash
# View hook timeline
qaw hooks agent-123

# Output:
# 17:29:15 PRE-SPAWN    validate-env.sh      ✓ 0.2s
# 17:29:15 POST-SPAWN   notify.sh            ✓ 0.1s
# 17:34:22 POST-COMPLETION format-code.sh    ✓ 1.3s
# 17:34:23 POST-COMPLETION run-tests.sh      ✗ 5.2s (exit 1)
```

## Next Steps

1. **Start Simple**: Begin with one orchestrator and 2-3 specialized agents
2. **Add Hooks Gradually**: Start with post-completion hooks for formatting/testing
3. **Measure & Optimize**: Track which patterns work best for your workflow
4. **Scale Up**: Add more specialized agents as patterns emerge
5. **Automate More**: Move repetitive tasks into hooks
