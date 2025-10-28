# Dashboard Demo Script

## Setup (1 minute)

```bash
# Clean slate
cd ~/demo-qaw
rm -rf .qaw
qaw init
```

## Demo Flow (5 minutes)

### 1. Launch Dashboard (10 seconds)
```bash
# Terminal 1
qaw dashboard
```

**Show**:
- Clean interface with 0 agents
- Grid layout with panels
- Keyboard shortcuts in footer

### 2. Submit Multiple Agents (30 seconds)
```bash
# Terminal 2 - Rapid fire submission
qaw submit "Create React login form with email and password fields" --agent frontend-agent

qaw submit "Create POST /api/auth/login endpoint with JWT" --agent backend-agent

qaw submit "Write integration tests for login flow" --agent test-agent

qaw submit "Document authentication API endpoints" --agent doc-agent
```

**Show in Dashboard**:
- Stats panel updates (4 total, 4 running)
- Table populates with emoji status
- Real-time duration updates

### 3. Select and View Agent (20 seconds)
**Action**: Click on frontend-agent row

**Show**:
- Details panel populates
- Full agent info displayed
- Action buttons enable
- Status color coding

### 4. Monitor Progress (60 seconds)
**Show**:
- Auto-refresh every 2 seconds
- Durations incrementing
- Agents completing (🔄 → ✓)
- Stats updating automatically

### 5. Interact with Agent (30 seconds)

**Select a running agent**, then:

```
Press 'l' key (or click View Logs button)
```

**Show**:
- Notification with last 30 lines
- See what agent is doing
- Real-time feedback

### 6. Stop an Agent (20 seconds)

**Select a running agent**, then:

```
Press 's' key (or click Stop Agent button)
```

**Show**:
- "Agent stopped" notification
- Status changes to cancelled
- Button state updates

### 7. Cleanup (10 seconds)

```
Press 'c' key (or click Cleanup button)
```

**Show**:
- "Cleanup complete" notification
- Stale agents removed
- Table refreshes

### 8. Help (10 seconds)

```
Press '?' key
```

**Show**:
- Full keyboard shortcuts
- Usage instructions
- Dismisses after 15s

### 9. View Completed Work (30 seconds)

```
Press 'q' to quit dashboard
ls -la  # Show created files
cat LoginForm.tsx  # Show agent output
```

**Show**:
- All files created
- Production-quality code
- Multiple agents worked in parallel

## Talking Points

### Opening
*"Let me show you the Q Agentic Workstation dashboard - a beautiful terminal UI for managing AI agents."*

### Features to Highlight

1. **Real-Time Monitoring**
   - "Notice how it updates automatically every 2 seconds"
   - "No need to manually refresh or rerun commands"

2. **Professional UI**
   - "Clean grid layout with dedicated panels"
   - "Color-coded status indicators"
   - "Emoji for quick visual scanning"

3. **Interactive Controls**
   - "Click any row to see full details"
   - "Buttons enable/disable based on context"
   - "Full keyboard navigation for power users"

4. **Production Quality**
   - "Built with Textual framework"
   - "Handles 20+ agents smoothly"
   - "Lightweight and responsive"

5. **Parallel Execution**
   - "All 4 agents run simultaneously"
   - "Independent processes"
   - "No blocking or waiting"

### Closing
*"This is just Phase 1. Coming soon: hooks for automation, dependency management, and advanced orchestration. The future of AI-assisted development."*

## Quick Wins to Demonstrate

1. **Speed**: 4 agents complete in ~2 minutes vs 8+ minutes sequential
2. **Visibility**: See everything at a glance vs multiple CLI commands
3. **Control**: Stop/start/view logs without leaving dashboard
4. **UX**: Professional UI vs plain text output
5. **Efficiency**: Auto-refresh vs manual polling

## Comparison Shot

### Before (CLI)
```bash
qaw status
# Wait...
qaw status
# Wait...
qaw status
# Manually check each agent:
qaw logs agent-123
qaw logs agent-456
qaw logs agent-789
```

### After (Dashboard)
```bash
qaw dashboard
# Everything live, all in one view
# Click, press keys, done
```

## Pro Tips for Demo

1. **Pre-load agents**: Have some running before showing dashboard
2. **Use full screen**: Maximize terminal for best effect
3. **Dark theme**: Looks better on video
4. **Slow down**: Let UI animations complete
5. **Highlight**: Point out auto-updates happening

## Common Questions

**Q**: "Does this require a GUI?"
**A**: "No! It's a TUI - works in any terminal, even over SSH."

**Q**: "What about CI/CD?"
**A**: "Use CLI for automation, dashboard for interactive development."

**Q**: "Can I customize it?"
**A**: "Keyboard shortcuts and themes coming in future updates."

**Q**: "Performance with many agents?"
**A**: "Tested with 20+, stays responsive. Updates only what changed."

## Technical Highlights (For Developers)

- Built with [Textual](https://textual.textualize.io/) framework
- Reactive programming model
- Efficient diff-based rendering
- Grid layout system
- Event-driven architecture
- Type-safe Python code
- 450 lines of production code

## Live Demo Checklist

- [ ] Terminal sized to at least 100x30
- [ ] Clean workspace (no old agents)
- [ ] Multiple terminals ready
- [ ] Good terminal theme
- [ ] Q CLI working
- [ ] All agents installed
- [ ] Textual installed
- [ ] Recording software ready (if recording)

## Backup Plan

If dashboard has issues:
1. Show CLI comparison first
2. Demo the qaw commands
3. Show TEST_RESULTS.md
4. Walk through dashboard.py code

## After Demo

Point to:
- **DASHBOARD.md** - Full documentation
- **QUICKSTART.md** - How to get started
- **PHASE2_PLAN.md** - What's coming next
- GitHub repo (if public)

---

**Remember**: The dashboard is the wow factor. Show it early, show it working, show it solving real problems.

🎬 Action!
