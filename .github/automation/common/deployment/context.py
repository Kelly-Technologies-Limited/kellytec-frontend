"""Resolve checked website deployment inputs and static Pages configuration."""

from pathlib import Path

from kellytec_automation.common.artifacts.verify_qualified_artifacts import (
    verify_qualified,
)
from kellytec_automation.common.io.library.local_files import read_json


def website_context(root: Path) -> tuple[dict, dict]:
    """Verify the restored product result before preparing Pages deployment."""
    value = read_json(root / ".automation/kellytec-website/qualified.json")
    snapshot = value["snapshot"]
    verify_qualified(
        root,
        value,
        repository=snapshot["repository"],
        product="kellytec-website",
        source_sha=snapshot["source_sha"],
    )
    config = read_json(
        root / ".github/automation/deploy-kellytec-website-to-github-pages/config/pages.json"
    )
    directory = (root / config["directory"]).resolve()
    if not directory.is_relative_to(root.resolve()) or not directory.is_dir():
        raise ValueError("Pages requires a checked artifact directory inside the workspace")
    return snapshot, config
