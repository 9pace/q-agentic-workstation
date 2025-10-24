# Hooks System Design

## Overview

Hooks enable automation throughout the agent lifecycle, allowing you to customize behavior at critical execution points without modifying core logic.

## Hook Types

### 1. Pre-Spawn Hooks
**Triggered**: Before agent starts execution

**Use Cases**:
- Environment validation
- Dependency checking
- Context preparation
- Resource allocation
- Git branch creation

**Example**:
```bash
# hooks/pre-spawn/validate-env.sh
#!/bin/bash
# Ensure required tools are available
command -v git >/dev/null || exit 1
command -v node >/dev/null || exit 1

# Check disk space
available=$(df -h . | awk 'NR==2 {print $4}')
echo "Available space: $available"
```

### 2. Post-Spawn Hooks
**Triggered**: Immediately after agent starts

**Use Cases**:
- Notification sending
- Status updates
- Logging initialization
- Resource monitoring setup

**Example**:
```bash
# hooks/post-spawn/notify.sh
#!/bin/bash
AGENT_ID=$1
TASK_DESC=$2
echo "🚀 Agent $AGENT_ID spawned for: $TASK_DESC" | notify
```

### 3. On-Progress Hooks
**Triggered**: Periodically during agent execution

**Use Cases**:
- Progress updates
- Resource usage monitoring
- Checkpoint creation
- Live output streaming

**Example**:
```bash
# hooks/on-progress/stream-logs.sh
#!/bin/bash
AGENT_ID=$1
tail -f .qaw/logs/agent-$AGENT_ID.log | tee -a .qaw/logs/combined.log
```

### 4. Post-Completion Hooks
**Triggered**: After agent successfully completes

**Use Cases**:
- Result validation
- Code formatting
- Test execution
- Documentation generation
- Git commit creation
- Notification sending

**Example**:
```bash
# hooks/post-completion/format-code.sh
#!/bin/bash
AGENT_ID=$1
RESULT_DIR=.qaw/results/agent-$AGENT_ID

# Format all modified files
find $RESULT_DIR -name "*.py" -exec black {} \;
find $RESULT_DIR -name "*.ts" -exec prettier --write {} \;
```

### 5. On-Error Hooks
**Triggered**: When agent encounters an error

**Use Cases**:
- Error logging
- Retry logic
- Escalation notifications
- Cleanup operations
- Rollback changes

**Example**:
```bash
# hooks/on-error/retry-or-escalate.sh
#!/bin/bash
AGENT_ID=$1
ERROR_MSG=$2
ATTEMPT=$3

if [ $ATTEMPT -lt 3 ]; then
  echo "Retry attempt $ATTEMPT for agent $AGENT_ID"
  # Re-queue the task
  qaw retry $AGENT_ID
else
  echo "❌ Agent $AGENT_ID failed after 3 attempts: $ERROR_MSG"
  # Notify for manual intervention
  qaw notify escalate $AGENT_ID "$ERROR_MSG"
fi
```

### 6. Pre-Cleanup Hooks
**Triggered**: Before agent resources are cleaned up

**Use Cases**:
- Artifact collection
- State preservation
- Final logging
- Resource release

**Example**:
```bash
# hooks/pre-cleanup/archive-logs.sh
#!/bin/bash
AGENT_ID=$1
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Archive logs before cleanup
tar -czf archives/agent-${AGENT_ID}-${TIMESTAMP}.tar.gz \
  .qaw/logs/agent-$AGENT_ID.log \
  .qaw/state/agents/agent-$AGENT_ID.json
```

## Hook Configuration

### Global Hooks
Defined in `.qaw/config/hooks.json`:

```json
{
  "hooks": {
    "pre-spawn": ["hooks/pre-spawn/validate-env.sh"],
    "post-spawn": ["hooks/post-spawn/notify.sh"],
    "on-progress": ["hooks/on-progress/stream-logs.sh"],
    "post-completion": [
      "hooks/post-completion/format-code.sh",
      "hooks/post-completion/run-tests.sh"
    ],
    "on-error": ["hooks/on-error/retry-or-escalate.sh"],
    "pre-cleanup": ["hooks/pre-cleanup/archive-logs.sh"]
  },
  "hookTimeout": 30,
  "continueOnHookFailure": false
}
```

### Agent-Specific Hooks
Override or extend global hooks per agent in agent config:

```json
{
  "name": "test-agent",
  "description": "Agent for running tests",
  "tools": ["@builtin"],
  "hooks": {
    "post-completion": [
      "hooks/test-agent/coverage-report.sh",
      "hooks/test-agent/upload-results.sh"
    ]
  }
}
```

## Hook Environment

All hooks receive these environment variables:

```bash
AGENT_ID          # Unique agent identifier
AGENT_NAME        # Agent configuration name
TASK_ID           # Task identifier
TASK_DESCRIPTION  # Task description
AGENT_PID         # Process ID of agent
LOG_FILE          # Path to agent log file
RESULT_DIR        # Directory for agent results
STATE_FILE        # Path to agent state JSON
START_TIME        # Agent start timestamp
```

## Hook Execution Model

### Synchronous Hooks
Block agent execution until complete:
- `pre-spawn` - Must succeed before agent starts
- `post-completion` - Run before marking task complete
- `on-error` - Handle error before cleanup

### Asynchronous Hooks
Run in background without blocking:
- `post-spawn` - Fire and forget notification
- `on-progress` - Continuous monitoring
- `pre-cleanup` - Can run while agent continues

## Hook Chain Example

```bash
# Complex workflow with multiple hooks

# 1. Pre-spawn: Validate and prepare
hooks/pre-spawn/validate-env.sh
hooks/pre-spawn/create-branch.sh

# 2. Spawn agent
qaw spawn --agent dev-agent "Add login feature"

# 3. Post-spawn: Start monitoring
hooks/post-spawn/notify.sh
hooks/post-spawn/start-monitor.sh &

# 4. On-progress: Continuous updates
hooks/on-progress/stream-logs.sh &
hooks/on-progress/update-dashboard.sh &

# 5. Post-completion: Validate and integrate
hooks/post-completion/format-code.sh
hooks/post-completion/run-tests.sh
hooks/post-completion/create-commit.sh
hooks/post-completion/notify-complete.sh

# 6. Pre-cleanup: Archive
hooks/pre-cleanup/archive-logs.sh
```

## Advanced Hook Patterns

### Conditional Execution
```bash
# hooks/post-completion/conditional-deploy.sh
#!/bin/bash
if [ "$AGENT_NAME" = "production-agent" ]; then
  # Only deploy for production agents
  ./deploy.sh
fi
```

### Hook Chaining
```bash
# hooks/post-completion/chain.sh
#!/bin/bash
AGENT_ID=$1

# Run multiple steps
./format.sh $AGENT_ID && \
./test.sh $AGENT_ID && \
./commit.sh $AGENT_ID && \
./notify.sh $AGENT_ID "Success!"
```

### Dynamic Hook Loading
```bash
# Load hooks based on task type
TASK_TYPE=$(jq -r .type .qaw/state/agents/agent-$AGENT_ID.json)
if [ -f "hooks/$TASK_TYPE/post-completion.sh" ]; then
  ./hooks/$TASK_TYPE/post-completion.sh $AGENT_ID
fi
```

## Integration with Q CLI

### Using Q CLI in Hooks
```bash
# hooks/post-completion/validate-with-q.sh
#!/bin/bash
AGENT_ID=$1

# Use Q CLI to review code
q chat --no-interactive \
  --agent code-reviewer \
  "Review the changes in $RESULT_DIR and suggest improvements" \
  > .qaw/reviews/agent-$AGENT_ID-review.txt
```

### Delegate to Sub-Agents
```bash
# hooks/post-completion/spawn-test-agent.sh
#!/bin/bash
AGENT_ID=$1

# Spawn a test agent after code generation
qaw spawn --agent test-agent \
  --parent $AGENT_ID \
  "Write tests for the code generated by agent $AGENT_ID"
```

## Best Practices

1. **Keep hooks simple**: Single responsibility per hook
2. **Handle failures gracefully**: Always include error handling
3. **Make hooks idempotent**: Safe to run multiple times
4. **Log extensively**: Debug issues after the fact
5. **Use timeouts**: Prevent hung hooks from blocking
6. **Test independently**: Hooks should work standalone
7. **Document dependencies**: List required tools/env vars

## Debugging Hooks

```bash
# Enable hook debugging
export QAW_DEBUG_HOOKS=1

# Run hook manually
AGENT_ID=test-123 \
TASK_ID=task-456 \
./hooks/post-completion/format-code.sh

# Check hook logs
tail -f .qaw/logs/hooks/post-completion.log
```
