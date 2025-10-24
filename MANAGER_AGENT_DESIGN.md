# Manager Agent Design - Autonomous Orchestration

## Problem Statement

**Current Issues**:
1. Agents go off-scope, introduce too much complexity
2. Manual task breakdown required
3. No automatic verification of correctness
4. No alignment check with original intent
5. Need to manually approve every tool use

**Goal**: Autonomous, self-verifying agent teams that work in small, safe increments.

## Architecture

### 1. Manager Agent (Orchestrator)

**Role**: Intelligent coordinator that plans, delegates, and verifies.

**Capabilities**:
- Natural language task interpretation
- Scope analysis and breakdown
- Context document generation
- Agent team assembly
- Progress monitoring
- Verification coordination
- Iterative refinement

### 2. Project Context System

**Steering Documents** (auto-generated):
```
.qaw/context/
├── project_rules.md       # Project-specific guidelines
├── architecture.md        # Current architecture understanding
├── coding_standards.md    # Code style, patterns to follow
├── constraints.md         # What NOT to do
└── verification_rules.md  # How to validate success
```

**Manager creates these on first run**:
1. Scans codebase
2. Infers patterns, style, architecture
3. Generates steering docs
4. Updates as project evolves

### 3. Task Decomposition Strategy

**Incremental Change Philosophy**:
```
Large Task: "Add user authentication"
    ↓ Manager breaks down:
    
Increment 1: "Add User model with email/password fields"
  - Minimal: Just the data model
  - Testable: Can verify schema
  - Safe: No business logic yet
  
Increment 2: "Add password hashing utility"
  - Minimal: Single function
  - Testable: Unit test with known inputs
  - Safe: No integration yet
  
Increment 3: "Add login endpoint"
  - Minimal: Single endpoint
  - Testable: Integration test
  - Safe: Builds on verified pieces
  
Increment 4: "Add JWT generation"
  - etc...
```

**Manager ensures**:
- Each increment is < 50 lines
- Each is independently testable
- Each is verifiable before next
- Rollback is always possible

### 4. Verification Pipeline

**3-Stage Verification**:

**Stage 1: Alignment Check**
```
Alignment Agent:
  - Reads original intent
  - Reviews code produced
  - Checks: "Does this match what was asked?"
  - Output: YES/NO + explanation
```

**Stage 2: Code Quality Check**
```
Reviewer Agent:
  - Reads project rules
  - Reviews code against standards
  - Checks: patterns, style, architecture fit
  - Output: PASS/FAIL + suggestions
```

**Stage 3: Test Verification**
```
Test Agent (conditional):
  - Only if code is testable
  - Writes/runs tests
  - Checks: Does it work?
  - Output: TESTS_PASS/FAIL + coverage
```

**Manager decision tree**:
```
All 3 pass → ACCEPT → Next increment
Any fail   → RETRY (with feedback) or ROLLBACK
```

### 5. Chat Interface in Dashboard

**New UI Component**: Manager Chat Panel

```
┌────────────────────────────────────────────────┐
│ 💬 Manager Chat                           [×]  │
├────────────────────────────────────────────────┤
│                                                │
│ You: Add user authentication                   │
│                                                │
│ Manager: I'll break this into 6 increments:   │
│  1. ✓ User model (completed)                  │
│  2. 🔄 Password hashing (in progress)         │
│  3. ⏳ Login endpoint (pending)               │
│  4. ⏳ JWT tokens (pending)                   │
│  5. ⏳ Protected routes (pending)             │
│  6. ⏳ Verification tests (pending)           │
│                                                │
│ Agent updates:                                 │
│  • frontend-agent: Created Login.tsx           │
│  • backend-agent: Added /auth/login            │
│  • test-agent: 12/12 tests passing            │
│  • alignment-agent: ✓ Matches intent          │
│                                                │
│ [Type message...]                              │
└────────────────────────────────────────────────┘
```

**Features**:
- Natural language input
- Manager responds with plan
- Live progress updates
- Agent activity feed
- Verification status
- Can ask questions mid-execution

## Implementation Plan

### Phase 2.5.1: Context System (Week 1)

**Files to create**:
```python
qaw/context.py (300 lines)
  - ProjectContext class
  - Auto-generate steering docs
  - Codebase analysis
  - Pattern inference
  
.qaw/context/
  - project_rules.md (template)
  - architecture.md (auto-generated)
  - coding_standards.md (inferred)
  - constraints.md (user-editable)
```

**Codebase Scanner**:
```python
class CodebaseAnalyzer:
    def analyze_project(self, root_dir: Path) -> ProjectContext:
        """Scan and understand the project."""
        
        # Detect tech stack
        tech_stack = self._detect_stack(root_dir)
        
        # Infer patterns
        patterns = self._analyze_patterns(root_dir)
        
        # Code style
        style = self._infer_style(root_dir)
        
        # Architecture
        architecture = self._map_architecture(root_dir)
        
        return ProjectContext(
            tech_stack=tech_stack,
            patterns=patterns,
            style=style,
            architecture=architecture,
        )
```

### Phase 2.5.2: Manager Agent (Week 2)

**Enhanced orchestrator-agent config**:
```json
{
  "name": "manager-agent",
  "description": "Intelligent orchestrator with verification",
  "tools": ["@builtin"],
  "allowedTools": [
    "delegate",
    "todo_list",
    "fs_read",
    "fs_write",
    "execute_bash"
  ],
  "systemPrompt": "You are a careful manager. Break tasks into <50 line increments. Always verify before proceeding. Use context docs in .qaw/context/",
  "autoApprove": true,
  "maxDelegations": 20,
  "verificationRequired": true
}
```

**Task Breakdown Algorithm**:
```python
class TaskBreakdown:
    def decompose(self, task: str, context: ProjectContext) -> List[Increment]:
        """Break task into minimal increments."""
        
        # Use manager-agent to analyze
        analysis = self._analyze_with_llm(task, context)
        
        # Extract increments
        increments = []
        for step in analysis.steps:
            increment = Increment(
                description=step.description,
                estimated_lines=step.lines,
                dependencies=[],
                testable=self._is_testable(step),
                verification_strategy=self._plan_verification(step),
            )
            increments.append(increment)
        
        return increments
```

### Phase 2.5.3: Verification Agents (Week 3)

**Three new agent configs**:

**alignment-agent.json**:
```json
{
  "name": "alignment-agent",
  "description": "Verifies code matches original intent",
  "systemPrompt": "Compare the original request with the code produced. Answer: Does this code do what was asked? Why or why not?",
  "allowedTools": ["fs_read"],
  "autoApprove": true
}
```

**reviewer-agent.json**:
```json
{
  "name": "reviewer-agent",
  "description": "Code quality and standards verification",
  "systemPrompt": "Review code against project rules in .qaw/context/. Check patterns, style, architecture fit. Provide specific feedback.",
  "allowedTools": ["fs_read", "grep"],
  "autoApprove": true
}
```

**test-agent-verifier.json**:
```json
{
  "name": "test-agent-verifier",
  "description": "Writes and runs verification tests",
  "systemPrompt": "Write minimal tests to verify the code works. Run them. Report pass/fail with details.",
  "allowedTools": ["fs_read", "fs_write", "execute_bash"],
  "autoApprove": true
}
```

**Verification Pipeline**:
```python
class VerificationPipeline:
    async def verify_increment(
        self,
        increment: Increment,
        code_produced: List[Path],
    ) -> VerificationResult:
        """Run 3-stage verification."""
        
        # Stage 1: Alignment
        alignment = await self._check_alignment(
            original_intent=increment.description,
            code_files=code_produced,
        )
        
        if not alignment.passes:
            return VerificationResult(
                stage="alignment",
                passed=False,
                feedback=alignment.reason,
                action="RETRY_WITH_FEEDBACK",
            )
        
        # Stage 2: Code Review
        review = await self._code_review(
            code_files=code_produced,
            project_rules=self.context.rules,
        )
        
        if not review.passes:
            return VerificationResult(
                stage="review",
                passed=False,
                feedback=review.suggestions,
                action="RETRY_WITH_FEEDBACK",
            )
        
        # Stage 3: Tests (if applicable)
        if increment.testable:
            tests = await self._run_tests(code_produced)
            
            if not tests.passes:
                return VerificationResult(
                    stage="tests",
                    passed=False,
                    feedback=tests.failures,
                    action="RETRY_WITH_FEEDBACK",
                )
        
        return VerificationResult(
            stage="complete",
            passed=True,
            feedback="All verifications passed",
            action="ACCEPT",
        )
```

### Phase 2.5.4: Chat Interface (Week 4)

**New dashboard widget**:
```python
class ManagerChatPanel(ScrollableContainer):
    """Interactive chat with manager agent."""
    
    def __init__(self):
        super().__init__()
        self.manager = ManagerAgent()
        self.conversation = []
    
    def compose(self) -> ComposeResult:
        yield Static(id="chat-history")
        yield Input(placeholder="Describe your task...", id="chat-input")
    
    async def on_input_submitted(self, event: Input.Submitted):
        """Handle user message."""
        user_message = event.value
        
        # Add to conversation
        self.add_message("user", user_message)
        
        # Manager processes
        plan = await self.manager.create_plan(user_message)
        self.add_message("manager", plan.summary)
        
        # Execute plan
        asyncio.create_task(self.execute_plan(plan))
    
    async def execute_plan(self, plan: ExecutionPlan):
        """Execute increments with verification."""
        for increment in plan.increments:
            # Update UI
            self.add_message("manager", f"Starting: {increment.description}")
            
            # Spawn agent
            agent = await self.spawn_coding_agent(increment)
            
            # Wait for completion
            await agent.wait()
            
            # Verify
            verification = await self.verify(increment, agent.outputs)
            
            if verification.passed:
                self.add_message("manager", f"✓ {increment.description} verified")
            else:
                self.add_message("manager", f"✗ Failed: {verification.feedback}")
                # Retry logic...
```

## Addressing Scope Creep

### 1. Hard Limits

**Enforce in manager-agent config**:
```python
class ScopeControl:
    MAX_LINES_PER_INCREMENT = 50
    MAX_FILES_PER_INCREMENT = 3
    MAX_ITERATIONS = 3
    
    def validate_increment(self, code_changes: CodeChanges) -> bool:
        """Ensure increment stays within bounds."""
        
        if code_changes.total_lines > self.MAX_LINES_PER_INCREMENT:
            return False, "Increment too large. Break into smaller pieces."
        
        if len(code_changes.files) > self.MAX_FILES_PER_INCREMENT:
            return False, "Too many files changed. Focus on one thing."
        
        return True, "OK"
```

### 2. Context Constraints

**In .qaw/context/constraints.md** (auto-generated):
```markdown
# Project Constraints

## Scope Control
- Maximum 50 lines per change
- One feature at a time
- No refactoring unless explicitly requested
- No "while we're at it" changes

## Forbidden Actions
- Don't change files outside task scope
- Don't add dependencies without approval
- Don't modify architecture without discussion
- Don't introduce new patterns

## Required Checks
- Every change must be testable
- Every change must be reversible
- Every change must align with intent
```

### 3. Manager Pre-Flight Check

**Before spawning any agent**:
```python
async def pre_flight_check(self, increment: Increment) -> bool:
    """Verify increment is focused and achievable."""
    
    # Check scope
    if not self._is_focused(increment):
        return False, "Too broad. Break down further."
    
    # Check dependencies
    if increment.dependencies and not all_complete(increment.dependencies):
        return False, "Dependencies not ready."
    
    # Check reversibility
    if not self._can_rollback(increment):
        return False, "Cannot safely rollback if needed."
    
    # Check testability
    if increment.testable and not self._has_test_strategy(increment):
        return False, "No clear way to verify this works."
    
    return True, "Ready to proceed"
```

### 4. Incremental Approval (Optional)

**For high-stakes changes**:
```python
class IncrementApproval:
    def __init__(self, require_human_approval: bool = False):
        self.require_human = require_human_approval
    
    async def approve_increment(self, increment: Increment) -> bool:
        """Get approval before executing."""
        
        if not self.require_human:
            return True  # Auto-approve
        
        # Show in dashboard chat
        response = await self.dashboard.ask_user(
            f"Proceed with: {increment.description}?\n"
            f"Estimated lines: {increment.estimated_lines}\n"
            f"Files affected: {increment.files_touched}\n"
            f"[Y/n]"
        )
        
        return response.lower() == 'y'
```

## Auto-Approval Implementation

**Make agents non-interactive by default**:

```python
# In executor.py
def spawn_agent(
    self,
    agent: AgentState,
    auto_approve: bool = True,  # NEW: default True
    trust_all_tools: bool = True,  # NEW: default True
):
    """Spawn agent with auto-approval."""
    
    cmd = ["q", "chat", "--agent", agent.agent_name]
    
    if no_interactive:
        cmd.append("--no-interactive")
    
    if auto_approve:
        cmd.append("--trust-all-tools")  # Q CLI auto-approves all tool use
    
    # ... rest of spawn logic
```

**Manager always uses**:
```python
# Manager spawns agents with full autonomy
agent = state.create_agent("frontend-agent", task)
executor.spawn_agent(agent, auto_approve=True, trust_all_tools=True)
```

## Configuration File

**`.qaw/config/manager.json`**:
```json
{
  "manager": {
    "enabled": true,
    "autoBreakdown": true,
    "autoApprove": true,
    "verificationRequired": true,
    "maxIncrementLines": 50,
    "maxIncrementFiles": 3,
    "requireTestsForLogic": true
  },
  "verification": {
    "alignmentCheck": true,
    "codeReview": true,
    "runTests": true,
    "maxRetries": 3
  },
  "context": {
    "autoGenerate": true,
    "updateOnCompletion": true,
    "includeExamples": true
  },
  "chat": {
    "enabled": true,
    "showAgentActivity": true,
    "showVerificationSteps": true,
    "notifyOnCompletion": true
  }
}
```

## Example Flow

### User Action
```
[In dashboard chat]: "Add user authentication with JWT"
```

### Manager Response (in chat)
```
Manager: Analyzing project...
- Detected: Express.js API, PostgreSQL
- Current auth: None
- Estimated: 6 increments, ~200 lines total

Plan:
1. Add User model (database schema)
2. Add password hashing util
3. Add user registration endpoint
4. Add login endpoint  
5. Add JWT generation/verification
6. Add auth middleware

Starting increment 1...
```

### Execution (auto)
```
Manager: Spawning backend-agent for User model...
→ backend-agent creates migration file
→ alignment-agent: ✓ Matches intent (user model with email/password)
→ reviewer-agent: ✓ Follows project patterns
→ test-agent: ✓ Schema validates
Manager: ✓ Increment 1 complete. Starting increment 2...
```

### If Something Fails
```
Manager: Spawning backend-agent for login endpoint...
→ backend-agent creates /api/auth/login
→ alignment-agent: ✓ Matches intent
→ reviewer-agent: ✗ Missing error handling
Manager: ✗ Code review failed. Retrying with feedback...

Manager: Spawning backend-agent (retry 1)...
→ backend-agent adds try/catch, status codes
→ reviewer-agent: ✓ Now passes
Manager: ✓ Increment 4 complete.
```

### Completion
```
Manager: All 6 increments complete!

Summary:
- Files created: 8
- Lines added: 187
- Tests added: 15 (all passing)
- Verification: All passed
- Duration: 8 minutes

Review changes?
[View Diff] [Accept All] [Reject]
```

## CLI Integration

```bash
# Chat mode (uses manager)
qaw chat "Add user auth"
# Manager takes over, breaks down, executes

# Dashboard includes chat
qaw dashboard
# Chat panel available, manager responds

# Or traditional
qaw submit "Add User model" --agent backend-agent
# Direct agent spawn (no manager)
```

## Benefits

1. **Scope Control**: Manager ensures small increments
2. **Auto-Verification**: 3-stage check catches issues early
3. **Context Aware**: Agents follow project patterns
4. **Self-Correcting**: Failed verifications trigger retries
5. **Fully Autonomous**: Auto-approve + verification = no babysitting
6. **Transparent**: Chat shows exactly what's happening
7. **Safe**: Rollback on any failure

## Technical Challenges

### Challenge 1: Manager Needs to be Smart
**Solution**: Use GPT-4 or Claude Opus for manager, cheaper models for specialist agents

### Challenge 2: Context Docs Need to be Good
**Solution**: Iterative improvement - manager updates docs as it learns

### Challenge 3: Verification Can Be Slow
**Solution**: Run stages in parallel where possible, cache verification results

### Challenge 4: Cost (Many LLM Calls)
**Solution**: 
- Use cheaper models for verification
- Cache alignment/review results
- Skip tests for trivial changes

## Implementation Priority

**Phase 2.5.1** (2 weeks):
1. Context system (codebase analysis)
2. Manager agent with breakdown logic
3. Auto-approve flag in executor
4. Basic chat interface in dashboard

**Phase 2.5.2** (2 weeks):
5. Verification agents (3 types)
6. Verification pipeline
7. Retry logic
8. Enhanced chat with status

**Phase 2.5.3** (1 week):
9. Scope control enforcement
10. Rollback on failure
11. User approval gates (optional)
12. Documentation

## Next Steps

1. Review design
2. Prioritize features
3. Start with context system
4. Build manager agent
5. Add chat interface
6. Implement verification

This creates a truly autonomous coding assistant that's safe, focused, and self-verifying. The chat interface makes it feel like a smart coworker who handles the details while keeping you informed.

Want me to start implementing this?
