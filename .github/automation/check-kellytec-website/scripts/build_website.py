"""Build and qualify the checked website artifact."""

import sys
from pathlib import Path

from kellytec_automation.common.artifacts.record_qualified_artifacts import (
    record_qualified,
)
from kellytec_automation.common.artifacts.restore_artifacts import restore_qualification
from kellytec_automation.common.io.library.local_files import read_json

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / ".github/automation/common/helpers"))
from brand_assets import (  # noqa: E402
    build_public_site,
)

if __name__ == "__main__":
    snapshot = read_json(ROOT / ".automation/kellytec-website/snapshot.json")
    if restore_qualification(ROOT, snapshot):
        raise SystemExit(0)
    destination = ROOT / "dist/site"
    build_public_site(destination)
    snapshot = read_json(ROOT / ".automation/kellytec-website/snapshot.json")
    record_qualified(
        ROOT,
        snapshot,
        [p for p in destination.rglob("*") if p.is_file()],
        {"check_website": "success", "build_website": "success"},
    )
