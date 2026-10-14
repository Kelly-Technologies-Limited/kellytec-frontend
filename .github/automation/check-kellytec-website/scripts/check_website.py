"""Check public pages, local links and the output allowlist."""

import sys
from pathlib import Path

from kellytec_automation.common.process.run_command import command

if __name__ == "__main__":
    command([sys.executable, "-m", "pytest", "-q", "tests/kellytec-website"], cwd=Path.cwd())
