"""Bind the exact main Check package before publishing its bytes."""

from pathlib import Path

from kellytec_automation.common.io.library.local_files import read_json
from kellytec_automation.release.prepare_release import prepare_package

if __name__ == "__main__":
    root = Path.cwd()
    prepare_package(
        root,
        read_json(root / ".github/automation/release-kellytec-design-system/config/package.json"),
    )
