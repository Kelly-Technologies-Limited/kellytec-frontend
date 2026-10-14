"""Expose this repository's declared product changes to GitHub jobs."""

import json
import os
from pathlib import Path

from kellytec_automation.common.adapter.github.context import event_payload, output
from kellytec_automation.common.changes.detect_changes import detect_changes
from kellytec_automation.common.io.library.local_files import read_json, write_json


def detect_product_changes() -> None:
    """Expose product impact as workflow outputs and retain its comparison evidence."""
    root = Path.cwd()
    rules = read_json(root / ".github/automation/common/changes/products.json")
    result = detect_changes(root, rules, os.environ["GITHUB_EVENT_NAME"], event_payload())
    write_json(root / ".automation/changes.json", result)
    output("products", json.dumps(result["products"]))
    output("source_sha", result["source_sha"])
    output(
        "repository_ready",
        str(os.environ["GITHUB_REPOSITORY"] == rules["repository"]).lower(),
    )


if __name__ == "__main__":
    detect_product_changes()
