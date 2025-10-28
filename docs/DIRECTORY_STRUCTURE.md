# Q Agentic Workstation - Directory Structure

## 📁 Project Organization

The Q Agentic Workstation project has been reorganized for better maintainability and clarity. Here's the current structure:

```
q-agentic-workstation/
│
├── 📦 qaw/                      # Core package source code
│   ├── __init__.py             # Package initialization
│   ├── cli.py                  # Command-line interface
│   ├── manager.py              # Manager agent orchestration
│   ├── dashboard.py            # Terminal UI dashboard
│   ├── dashboard_hybrid.py     # Hybrid dashboard implementation
│   ├── executor.py             # Agent execution engine
│   ├── state.py                # State management
│   ├── context.py              # Project context analysis
│   └── naming.py               # Semantic naming utilities
│
├── 🧪 tests/                    # Test suite
│   ├── test_agent_execution.py # Agent execution tests
│   ├── test_comprehensive_validation.py # Comprehensive validation
│   ├── test_dashboard.py       # Dashboard functionality tests
│   ├── test_manager_fixes.py   # Manager bug fix validation
│   ├── test_production_ready.py # Production readiness tests
│   └── TEST_RESULTS.md         # Test execution results
│
├── 📚 docs/                     # Documentation
│   ├── ARCHITECTURE.md         # System architecture
│   ├── CONTROL_CENTER.md       # Control center documentation
│   ├── DEMO_SCRIPT.md          # Demo walkthrough
│   ├── GETTING_STARTED.md      # Quick start guide
│   ├── HOOKS.md                # Hooks system documentation
│   ├── INTEGRATION.md          # Integration guide
│   ├── MANAGER_DASHBOARD.md    # Manager dashboard guide
│   ├── MANAGER_FIRST_SUMMARY.md # Manager overview
│   ├── ROADMAP.md              # Project roadmap
│   │
│   ├── 📂 archive/             # Historical documentation
│   │   ├── DASHBOARD_COMPLETE.md
│   │   ├── DASHBOARD.md
│   │   ├── FEATURES_COMPLETE.md
│   │   ├── MANAGER_AGENT_DESIGN.md
│   │   ├── MANAGER_MVP_COMPLETE.md
│   │   ├── MANAGER_QUICKSTART.md
│   │   ├── PHASE1_COMPLETE.md
│   │   ├── PHASE2_PLAN.md
│   │   └── SEMANTIC_NAMING_AND_AUTOPILOT.md
│   │
│   ├── 📂 design/              # Design documents
│   │   └── (Future design docs)
│   │
│   └── 📂 releases/            # Release notes
│       ├── AGENT_STALLING_FIX_SUMMARY.md
│       └── FIX_SUMMARY.md      # Latest UI/task breakdown fixes
│
├── 🤖 agents/                   # Agent configurations
│   ├── backend-agent.json      # Backend development agent
│   ├── doc-agent.json          # Documentation agent
│   ├── frontend-agent.json     # Frontend development agent
│   ├── orchestrator-agent.json # Orchestrator agent
│   └── test-agent.json         # Testing agent
│
├── 📋 examples/                 # Usage examples
│   └── full-stack-feature.md   # Full-stack feature example
│
├── 🔧 Configuration Files
│   ├── setup.py                # Package setup configuration
│   ├── requirements.txt        # Python dependencies
│   ├── install.sh              # Installation script
│   ├── .gitignore             # Git ignore rules
│   └── QUICKSTART.md          # Quick start guide
│
├── 📖 README.md                # Project overview
└── 📁 DIRECTORY_STRUCTURE.md   # This file

## Hidden Directories

- `.git/` - Git version control
- `.qaw/` - QAW runtime data and state
- `qaw.egg-info/` - Python package metadata
- `test-workspace/` - Test execution workspace
- `control-center/` - Control center components
- `hooks/` - Git hooks and automation

## Key Improvements in Organization

### 1. **Centralized Testing** (`tests/`)
All test files are now in a dedicated directory, making it easy to:
- Run the entire test suite
- Identify test coverage
- Maintain test code separately from production code

### 2. **Structured Documentation** (`docs/`)
Documentation is organized into categories:
- **Main docs**: Current, active documentation
- **Archive**: Historical documents for reference
- **Design**: Design specifications and proposals
- **Releases**: Release notes and fix summaries

### 3. **Clean Root Directory**
The root directory now contains only:
- Essential configuration files
- Main README and structure documentation
- Core directories

### 4. **Logical Grouping**
Related files are grouped together:
- All Python source in `qaw/`
- All tests in `tests/`
- All documentation in `docs/`
- All agent configs in `agents/`

## Quick Navigation

### For Developers
- Source code: `qaw/`
- Tests: `tests/`
- Agent configs: `agents/`

### For Users
- Getting started: `QUICKSTART.md`, `docs/GETTING_STARTED.md`
- Documentation: `docs/`
- Examples: `examples/`

### For Contributors
- Architecture: `docs/ARCHITECTURE.md`
- Roadmap: `docs/ROADMAP.md`
- Test suite: `tests/`

## Recent Changes

### Latest Fixes (October 2025)
- Fixed task breakdown for complex tasks (React/Amplify auth)
- Improved UI stability and error handling
- Enhanced manager response formatting
- See `docs/releases/FIX_SUMMARY.md` for details

### Directory Reorganization
- Moved all test files to `tests/`
- Organized documentation into subdirectories
- Cleaned up root directory
- Created clear separation between code, tests, and docs

## Maintenance Guidelines

1. **New Tests**: Add to `tests/` with descriptive names
2. **Documentation Updates**: Place in appropriate `docs/` subdirectory
3. **Release Notes**: Add to `docs/releases/` with date stamps
4. **Archive Old Docs**: Move outdated docs to `docs/archive/`
5. **Design Proposals**: Place in `docs/design/`

This structure promotes:
- ✅ Better code organization
- ✅ Easier navigation
- ✅ Clear separation of concerns
- ✅ Simplified maintenance
- ✅ Professional project structure
