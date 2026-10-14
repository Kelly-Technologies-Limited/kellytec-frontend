"""Generate shared brand assets and build the source-identified design-system wheel."""

import sys
from pathlib import Path

from kellytec_automation.common.adapter.github.context import output
from kellytec_automation.common.artifacts.restore_artifacts import restore_run_artifact
from kellytec_automation.common.io.library.integrity import file_sha256 as digest
from kellytec_automation.common.io.library.local_files import read_json, write_json
from kellytec_automation.common.process.run_command import command

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / ".github/automation/common/helpers"))
from brand_assets import (  # noqa: E402
    write_frontend_chrome,
)

if __name__ == "__main__":
    snapshot = read_json(ROOT / ".automation/kellytec-design-system/snapshot.json")
    directory = ROOT / "kellytec-design-system/dist"
    if restore_run_artifact("design-system-wheel", directory):
        manifest = read_json(directory / "manifest.json")
        if manifest["snapshot_id"] != snapshot["snapshot_id"] or not manifest["files"]:
            raise ValueError("Design System build belongs to another snapshot")
        for name, expected in manifest["files"].items():
            path = (directory / name).resolve()
            if not path.is_relative_to(directory.resolve()) or digest(path) != expected:
                raise ValueError("Restored Design System wheel changed")
        output("restored", "true")
        raise SystemExit(0)
    write_frontend_chrome(ROOT)
    command([sys.executable, "-m", "build", "--wheel", "kellytec-design-system"], cwd=ROOT)
    write_json(
        directory / "manifest.json",
        {
            "snapshot_id": snapshot["snapshot_id"],
            "files": {path.name: digest(path) for path in directory.glob("*.whl")},
        },
    )
