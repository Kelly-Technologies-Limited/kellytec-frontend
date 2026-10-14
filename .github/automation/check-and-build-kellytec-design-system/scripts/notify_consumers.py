"""Notify direct design-system consumers after full product qualification."""

from pathlib import Path

from kellytec_automation.common.dependencies.notify_consumers import notify_consumers
from kellytec_automation.common.io.library.local_files import read_json

if __name__ == "__main__":
    root = Path.cwd()
    snapshot = read_json(root / ".automation/kellytec-design-system/snapshot.json")
    config = read_json(
        root / ".github/automation/check-and-build-kellytec-design-system/config/consumers.json"
    )
    notify_consumers(root, snapshot, config)
