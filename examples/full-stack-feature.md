# Example: Full-Stack Feature Development

This example demonstrates how to use the Q Agentic Workstation to build a complete feature with parallel agent execution.

## Scenario

Build a user authentication system with:
- Login UI component
- Authentication API
- JWT token management
- Unit and integration tests
- API documentation

## Step 1: Submit Task

```bash
# Start the control center (in a separate terminal)
qaw dashboard

# Submit the task
qaw submit "Build complete user authentication system with login UI, JWT API, tests, and docs"
```

## Step 2: Orchestrator Breaks Down Task

The orchestrator agent analyzes and creates this execution plan:

```
1. Frontend: Login form component (React + TypeScript)
2. Backend: Auth API endpoints (/login, /logout, /refresh)
3. Backend: JWT middleware and token management
4. Tests: Frontend component tests
5. Tests: Backend API integration tests
6. Docs: API documentation
```

## Step 3: Parallel Execution

The orchestrator spawns 3 agents in parallel:

### Agent A: Frontend Agent
**Task**: Create login UI component

**Output**:
```
src/components/LoginForm.tsx (new)
src/components/LoginButton.tsx (new)
src/hooks/useAuth.ts (new)
src/types/auth.ts (new)
```

**Hooks**:
- `post-completion/format-code.sh` → Runs Prettier
- `post-completion/lint.sh` → Runs ESLint

### Agent B: Backend Agent
**Task**: Implement auth API endpoints

**Output**:
```
src/routes/auth.ts (new)
src/controllers/authController.ts (new)
src/services/authService.ts (new)
src/middleware/authMiddleware.ts (new)
```

**Hooks**:
- `post-completion/format-code.sh` → Runs Prettier
- `post-completion/swagger.sh` → Updates Swagger docs

### Agent C: Backend Agent
**Task**: JWT token management

**Output**:
```
src/utils/jwt.ts (new)
src/config/jwt.config.ts (new)
```

## Step 4: Synchronization

After agents A, B, and C complete:

**Hook**: `hooks/orchestrator/sync-parallel-agents.sh`
- Validates all outputs
- Checks for conflicts
- Merges changes

## Step 5: Sequential Execution

Now that code is complete, run dependent tasks sequentially:

### Agent D: Test Agent (Frontend)
**Task**: Write tests for login components

**Output**:
```
src/components/__tests__/LoginForm.test.tsx (new)
src/hooks/__tests__/useAuth.test.ts (new)
```

**Hooks**:
- `post-completion/run-tests.sh` → Runs Jest

### Agent E: Test Agent (Backend)
**Task**: Write API integration tests

**Output**:
```
tests/integration/auth.test.ts (new)
```

**Hooks**:
- `post-completion/run-tests.sh` → Runs test suite
- `post-completion/coverage.sh` → Generates coverage report

### Agent F: Doc Agent
**Task**: Create API documentation

**Output**:
```
docs/api/authentication.md (new)
README.md (updated - added auth section)
```

**Hooks**:
- `post-completion/build-docs.sh` → Builds documentation site

## Step 6: Final Validation

**Hook**: `hooks/orchestrator/finalize.sh`

```bash
#!/bin/bash
# Run full test suite
npm test

# Check types
npm run typecheck

# Lint everything
npm run lint

# Generate summary
qaw summary > .qaw/results/summary.md
```

## Step 7: Review Results

```bash
# View status
qaw status

# Output:
# ✓ orchestrator-agent-abc123 (completed 8m ago)
#   ├─ ✓ frontend-agent-def456 (completed 6m ago)
#   ├─ ✓ backend-agent-ghi789 (completed 6m ago)  
#   ├─ ✓ backend-agent-jkl012 (completed 6m ago)
#   ├─ ✓ test-agent-mno345 (completed 4m ago)
#   ├─ ✓ test-agent-pqr678 (completed 3m ago)
#   └─ ✓ doc-agent-stu901 (completed 1m ago)

# Review changes
qaw diff

# View file tree
qaw files orchestrator-agent-abc123

# Read summary
cat .qaw/results/summary.md
```

## Step 8: Accept or Modify

### Option A: Accept Everything
```bash
qaw accept orchestrator-agent-abc123

# All changes merged to your working directory
# Git commit created (if configured)
```

### Option B: Selective Accept
```bash
# Accept frontend changes only
qaw accept frontend-agent-def456

# Reject backend approach, try different strategy
qaw reject backend-agent-ghi789

# Re-submit backend task with more guidance
qaw submit "Implement auth API using Express middleware pattern with bcrypt" \
  --agent backend-agent
```

### Option C: Request Modifications
```bash
# Ask for adjustments
qaw modify test-agent-mno345 \
  "Add tests for password reset flow and edge cases"
```

## Monitoring During Execution

### Terminal UI Dashboard
```
┌─ Q Agentic Workstation ────────────────────────────────────┐
│ Task: Build authentication system                           │
│ Status: 3 running | 2 pending | 1 completed                 │
│ Elapsed: 6m 23s                                             │
└────────────────────────────────────────────────────────────┘

Active Agents:
┌────────────────────────────────────────────────────────────┐
│ frontend-agent-def456  │ Creating LoginForm.tsx    │ 80%  │
│ backend-agent-ghi789   │ Writing authService.ts    │ 60%  │
│ backend-agent-jkl012   │ Implementing JWT utils    │ 40%  │
└────────────────────────────────────────────────────────────┘

Recent Activity:
17:30:15 ▶ frontend-agent spawned
17:30:16 ▶ backend-agent spawned (API)
17:30:17 ▶ backend-agent spawned (JWT)
17:32:45 ✓ Pre-spawn hooks completed
17:35:22 📝 frontend-agent created LoginForm.tsx
```

### Live Logs
```bash
# Follow specific agent
qaw logs -f frontend-agent-def456

# Follow all agents
qaw logs -f --all

# Filter by level
qaw logs --level error --all
```

## Expected Timeline

| Phase | Duration | Agents | Status |
|-------|----------|--------|--------|
| Analysis | 30s | Orchestrator | Planning |
| Frontend Dev | 4-6m | Frontend Agent | Running |
| Backend Dev | 5-7m | Backend Agent x2 | Running |
| Frontend Tests | 3-4m | Test Agent | Waiting |
| Backend Tests | 3-5m | Test Agent | Waiting |
| Documentation | 2-3m | Doc Agent | Waiting |
| **Total** | **8-12m** | | |

Compare to sequential development: **~30-45 minutes**

**Speedup**: 3-4x faster with parallel agents

## Cost Analysis

```bash
# View cost breakdown
qaw metrics orchestrator-agent-abc123

# Output:
# Agent                    | Tokens | Cost
# -------------------------|--------|-------
# orchestrator-agent       | 2.5K   | $0.01
# frontend-agent           | 8.2K   | $0.04
# backend-agent (API)      | 12.1K  | $0.06
# backend-agent (JWT)      | 6.8K   | $0.03
# test-agent (frontend)    | 5.4K   | $0.03
# test-agent (backend)     | 7.9K   | $0.04
# doc-agent               | 3.2K   | $0.02
# -------------------------|--------|-------
# Total                    | 46.1K  | $0.23
```

## Next Steps

1. Try modifying agent prompts for better results
2. Add custom hooks for your workflow
3. Create specialized agents for your stack
4. Integrate with CI/CD pipeline
5. Share successful patterns with team
