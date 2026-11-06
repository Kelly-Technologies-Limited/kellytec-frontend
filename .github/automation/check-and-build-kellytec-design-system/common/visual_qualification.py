"""Bind independently compared Services presentation to one checked wheel."""

from pathlib import Path

from kellytec_automation.runtime.files.integrity import file_sha256
from kellytec_automation.runtime.files.local_files import read_json


CHECK = "services-ui-v1"
REPORT = ".automation/design-system-ui/acceptance.json"


def require_visual_qualification(root: Path, snapshot: dict, record: dict) -> None:
    """Reject missing, failed or unrelated Services visual qualification."""
    artifacts = record.get("artifacts", {})
    wheels = [name for name in artifacts if Path(name).name.startswith("kellytec_design_system-")
              and name.endswith(".whl")]
    if record.get("checks", {}).get(CHECK) != "success" or REPORT not in artifacts:
        raise ValueError("Services visual qualification is required")
    if len(wheels) != 1:
        raise ValueError("Services visual qualification requires one wheel")
    wheel = wheels[0]
    if file_sha256(root / wheel) != artifacts[wheel]:
        raise ValueError("Services visual qualification wheel changed")
    report = read_json(root / REPORT)
    expected = {"status": "passed", "policy": CHECK, "visual_comparison": "passed",
                "snapshot_id": snapshot["snapshot_id"], "wheel_sha256": artifacts[wheel]}
    if any(report.get(key) != value for key, value in expected.items()):
        raise ValueError("Services visual evidence differs from the qualified wheel or snapshot")
