# Manager-First Dashboard

## Overview

The Manager-First Dashboard is a production-quality Terminal User Interface (TUI) that puts natural language interaction at the center of your development workflow. Instead of manually managing agents, you describe what you want to build, and the Manager Agent orchestrates everything.

## Quick Start

### Launch the Dashboard

```bash
# Primary command
qaw app

# Alternative
qaw dashboard
```

### Your First Task

1. **Describe your task** in the chat input (bottom left):
   ```
   Add a user authentication system with login and signup
   ```

2. **Review the plan** - Manager breaks it into small increments shown in the Execution Plan panel

3. **Click "Execute"** or press Enter - Watch agents execute each increment in real-time

4. **Monitor progress** - See live updates as agents work through each step

## Interface Layout

```
┌─────────────────────────────────────────────────────────────┐
│                  Q Agentic Workstation                      │
│                  Manager-First Interface                     │
├──────────────────────────────┬──────────────────────────────┤
│                              │                              │
│   💬 Manager Chat            │   📋 Execution Plan          │
│   ━━━━━━━━━━━━━━━━━━━━━     │   ━━━━━━━━━━━━━━━━━━━━━     │
│                              │                              │
│   User: Add login feature    │   Task: Add login feature    │
│                              │   Increments: 3              │
│   Manager: I'll break this   │                              │
│   into 3 increments...       │   1. ⏳ Add auth model       │
│                              │   2. ⏳ Add API endpoints     │
│   [Chat history scrolls]     │   3. ⏳ Add tests            │
│                              │                              │
│                              ├──────────────────────────────┤
│                              │   📊 Agent Stats             │
│                              │   ━━━━━━━━━━━━━━━━━━━━━     │
│                              │   Total:      5              │
│                              │   Running:    2              │
│                              │   Done:       3              │
├──────────────────────────────┼──────────────────────────────┤
│ [Input: Describe task...]   │   🤖 Recent Agents           │
│ [🚀 Send] [▶️ Execute]      │   ✅ auth-model-builder      │
│                              │   🔄 api-endpoint-creator    │
└──────────────────────────────┴──────────────────────────────┘
```

### Panels

#### 💬 Manager Chat (Left, Top)
- **Purpose**: Primary interaction point with the Manager Agent
- **Features**:
  - Natural language task descriptions
  - Manager responses with execution plans
  - Conversation history
  - Real-time feedback during execution

#### 📋 Execution Plan (Right, Top)
- **Purpose**: Shows the breakdown of your current task
- **Features**:
  - Task description
  - List of increments with status indicators
  - Progress tracking (⏳ pending, 🔄 running, 🔍 verifying, ✅ done, ❌ failed)
  - Retry counts for failed increments
  - Estimated lines of code per increment

#### 📊 Agent Stats (Right, Middle)
- **Purpose**: Overview of all agents in the workspace
- **Shows**:
  - Total agents spawned
  - Currently running
  - Pending tasks
  - Completed tasks
  - Failed tasks

#### 🤖 Recent Agents (Right, Bottom)
- **Purpose**: Quick view of recently spawned agents
- **Shows**: Last 8 agents with their status and task preview

## Usage Patterns

### 1. Feature Development

**Input:**
```
Add a REST API endpoint for user profiles with GET, POST, PUT, DELETE
```

**Manager Response:**
```
I'll break this into 3 increments:

1. ⏳ Add data model for user profiles (~40 lines)
2. ⏳ Add API endpoints (GET, POST, PUT, DELETE) (~45 lines)
3. ⏳ Add tests for all endpoints (~35 lines)

Total estimated: ~120 lines

Ready to proceed?
```

**Action:** Click "▶️ Execute" to start

### 2. Bug Fixing

**Input:**
```
Fix the authentication bug where tokens expire too quickly
```

**Manager Response:**
```
I'll break this into 2 increments:

1. ⏳ Investigate and fix token expiration (~30 lines)
2. ⏳ Add regression test for token expiration (~25 lines)

Total estimated: ~55 lines
```

### 3. Refactoring

**Input:**
```
Refactor the database queries to use connection pooling
```

**Manager Response:**
```
I'll break this into 2 increments:

1. ⏳ Refactor database queries to use pooling (~40 lines)
2. ⏳ Verify refactoring with integration tests (~30 lines)

Total estimated: ~70 lines
```

### 4. Testing

**Input:**
```
Add comprehensive tests for the payment processing module
```

**Manager Response:**
```
I'll break this into 1 increment:

1. ⏳ Add payment processing tests (~45 lines)

Total estimated: ~45 lines
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Submit chat message |
| `Ctrl+R` | Refresh all data |
| `q` | Quit dashboard |
| `?` | Show help |

## Status Indicators

| Icon | Status | Meaning |
|------|--------|---------|
| ⏳ | Pending | Increment waiting to be executed |
| 🔄 | Running | Agent is currently working on increment |
| 🔍 | Verifying | Increment completed, running verification |
| ✅ | Completed | Increment finished successfully |
| ❌ | Failed | Increment failed (will retry) |
| 🔁 | Retry | Increment being retried after failure |

## Advanced Features

### Automatic Retry Logic

If an increment fails, the Manager automatically:
1. Captures the error
2. Adds verification feedback
3. Retries up to 3 times
4. Adjusts the approach based on feedback

### Live Progress Updates

Watch in real-time as:
- Increments transition through statuses
- Agents spawn and complete
- Verification runs
- Stats update

### Context-Aware Planning

The Manager uses project context to:
- Detect your tech stack
- Understand architecture patterns
- Follow naming conventions
- Use the right agent types

## Tips for Best Results

1. **Be Specific**: "Add user authentication with JWT tokens" is better than "Add auth"

2. **One Task at a Time**: Let the Manager break down complex tasks into increments

3. **Watch the Plan**: Review the execution plan before clicking Execute

4. **Check Logs**: If something fails, check recent agents for detailed logs

5. **Iterate**: After execution, describe follow-up tasks or adjustments

## Example Session

```
👤 You: Add a contact form to the homepage

🤖 Manager: I'll break this into 3 increments:

1. ⏳ Add contact form component (~50 lines)
2. ⏳ Add API endpoint for form submission (~45 lines)
3. ⏳ Add tests for form validation (~35 lines)

Total estimated: ~130 lines

Ready to proceed?

[User clicks "▶️ Execute"]

🤖 Manager: 🚀 Executing plan...

[Execution Plan Panel updates in real-time:]
1. 🔄 Add contact form component (~50 lines)
   Agent: frontend | ~50 lines
2. ⏳ Add API endpoint for form submission (~45 lines)
3. ⏳ Add tests for form validation (~35 lines)

[After completion:]
🤖 Manager: ✅ All increments completed successfully!

👤 You: Add email validation to the form

🤖 Manager: I'll break this into 2 increments:
...
```

## Troubleshooting

### "Manager not ready yet"
- Wait a few seconds for initialization
- Context analysis runs on first launch

### Plan execution stuck
- Check Agent Stats for running agents
- View Recent Agents for status
- Press `Ctrl+R` to refresh

### Dashboard won't launch
- Ensure textual is installed: `pip install textual`
- Check workspace is initialized: `qaw init`

## Comparison with CLI Chat

| Feature | Dashboard (`qaw app`) | CLI (`qaw chat`) |
|---------|----------------------|------------------|
| Interface | Rich TUI | Text-based |
| Progress | Live updates | Text output |
| Monitoring | Multi-panel | Status commands |
| Best For | Development sessions | Quick tasks, scripts |

## Next Steps

- Learn about [Manual Agent Control](./ADVANCED.md)
- Understand [Manager Agent Architecture](./MANAGER_AGENT.md)
- Explore [Phase 2 Features](./ROADMAP.md)

---

**Pro Tip**: Keep the dashboard open during development. Describe tasks as they come up, and let the Manager orchestrate your agent team!
