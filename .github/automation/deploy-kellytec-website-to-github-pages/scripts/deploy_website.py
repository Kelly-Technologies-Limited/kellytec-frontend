"""Verify Pages inputs or record the result of the official deployment step."""

import os
import sys
from pathlib import Path

from kellytec_automation.common.adapter.github.context import output

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / ".github/automation/common/deployment"))
from context import (  # noqa: E402
    website_context,
)
from state import (  # noqa: E402
    record_pages_result,
)

if __name__ == "__main__":
    snapshot, config = website_context(ROOT)
    if url := os.environ.get("PAGES_DEPLOYMENT_URL"):
        record_pages_result(ROOT, snapshot, url)
    else:
        output("directory", config["directory"])
        output("artifact_name", config["artifact_name"] + "-" + os.environ["GITHUB_RUN_ATTEMPT"])
