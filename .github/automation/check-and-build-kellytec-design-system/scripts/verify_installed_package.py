"""Test the installed wheel and record whole-product qualification."""

import sys
from pathlib import Path

from kellytec_automation.common.artifacts.record_qualified_artifacts import (
    record_qualified,
)
from kellytec_automation.common.artifacts.restore_artifacts import restore_qualification
from kellytec_automation.common.io.library.local_files import read_json
from kellytec_automation.common.process.run_command import command

if __name__ == "__main__":
    root = Path.cwd()
    snapshot = read_json(root / ".automation/kellytec-design-system/snapshot.json")
    if restore_qualification(root, snapshot):
        raise SystemExit(0)
    wheels = list((root / "kellytec-design-system/dist").glob("*.whl"))
    if len(wheels) != 1:
        raise ValueError("Expected exactly one design-system wheel")
    command(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--force-reinstall",
            str(wheels[0]),
        ]
    )
    command(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/kellytec-design-system",
            "tests/workloads/build",
        ]
    )
    record_qualified(
        root,
        read_json(root / ".automation/kellytec-design-system/snapshot.json"),
        wheels,
        {
            "check_design_system": "success",
            "build_wheel": "success",
            "verify_installed_package": "success",
        },
    )
