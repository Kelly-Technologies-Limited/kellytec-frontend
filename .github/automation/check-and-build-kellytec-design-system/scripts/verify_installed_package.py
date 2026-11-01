"""Test the installed wheel and record whole-product qualification."""

import runpy
import sys
from pathlib import Path

from kellytec_automation.common.artifacts.record_qualified_artifacts import (
    record_qualified,
)
from kellytec_automation.common.artifacts.restore_artifacts import restore_qualification
from kellytec_automation.common.io.library.integrity import file_sha256
from kellytec_automation.common.io.library.local_files import read_json, write_json
from kellytec_automation.common.process.run_command import command

VISUAL = runpy.run_path(str(Path(__file__).resolve().parents[1] / "common/visual_qualification.py"))


def main() -> None:
    root = Path.cwd()
    snapshot = read_json(root / ".automation/kellytec-design-system/snapshot.json")
    if restore_qualification(root, snapshot):
        VISUAL["require_visual_qualification"](
            root, snapshot, read_json(root / ".automation/kellytec-design-system/qualified.json"),
        )
        return
    wheels = list((root / "src/kellytec-design-system/dist").glob("*.whl"))
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
    directory = root / ".automation/design-system-ui"
    directory.mkdir(parents=True, exist_ok=True)
    browser = command([
        sys.executable, "-c",
        "from playwright.sync_api import sync_playwright; "
        "p=sync_playwright().start(); print(p.chromium.executable_path); p.stop()",
    ])
    command([
        sys.executable, "tests/kellytec-design-system/check_service_parity.py",
        "--browser-path", browser, "--output", str(directory),
    ], timeout=300)
    result = read_json(directory / "validation.json")
    cases = result.get("cases", [])
    if (len(cases) != 5 or {row.get("viewport_width") for row in cases} != {390, 520, 521, 900, 1440}
            or any(row.get("mode") != "component" or row.get("pixel_equal") is not True
                   or row.get("computed_styles_equal") is not True for row in cases)):
        raise ValueError("Independent Services visual comparisons did not all pass")
    write_json(directory / "acceptance.json", {
        "status": "passed", "policy": VISUAL["CHECK"], "visual_comparison": "passed",
        "snapshot_id": snapshot["snapshot_id"], "wheel_sha256": file_sha256(wheels[0]),
        "comparison": result,
    })
    record_qualified(
        root,
        snapshot,
        [*wheels, *sorted(path for path in directory.rglob("*") if path.is_file())],
        {
            "check_design_system": "success",
            "build_wheel": "success",
            "verify_installed_package": "success",
            VISUAL["CHECK"]: "success",
        },
    )


if __name__ == "__main__":
    main()
