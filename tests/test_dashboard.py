#!/usr/bin/env python
"""Test dashboard rendering."""

from pathlib import Path
from qaw.dashboard import DashboardApp

# Create test workspace
workspace = Path(".qaw")
workspace.mkdir(exist_ok=True)
(workspace / "state").mkdir(exist_ok=True)
(workspace / "logs").mkdir(exist_ok=True)
(workspace / "results").mkdir(exist_ok=True)
(workspace / "pids").mkdir(exist_ok=True)

# Launch dashboard
print("Launching dashboard...")
app = DashboardApp(workspace)
try:
    app.run()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
