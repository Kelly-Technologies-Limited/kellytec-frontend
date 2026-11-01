"""Prevent a retained pre-visual qualification from skipping the browser gate."""

import runpy
from pathlib import Path

from kellytec_automation.common.io.library.local_files import read_json


if __name__ == "__main__":
    root = Path.cwd()
    helper = runpy.run_path(str(Path(__file__).resolve().parents[1] / "common/visual_qualification.py"))
    helper["require_visual_qualification"](
        root, read_json(root / ".automation/kellytec-design-system/snapshot.json"),
        read_json(root / ".automation/kellytec-design-system/qualified.json"),
    )
