"""Upload only the original qualified package files."""

from pathlib import Path

from kellytec_automation.common.io.library.local_files import read_json
from kellytec_automation.publish.publish_packages import publish_files
from kellytec_automation.release.contract import read_manifest

if __name__ == "__main__":
    root = Path.cwd()
    config = read_json(
        root / ".github/automation/release-kellytec-design-system/config/package.json"
    )
    request = read_json(root / ".automation/package-release/request.json")
    manifest = read_manifest(request["manifest"])
    publish_files(
        config["registry"]["project"],
        manifest.version,
        {a.filename: a.sha256 for a in manifest.artifacts},
        root / ".automation/package-release",
        config["upload_url"],
        registry=config["registry"],
    )
