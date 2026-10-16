"""Complete the GitHub Release after package publication succeeds."""

import json
import os
from pathlib import Path

from kellytec_automation.common.io.library.local_files import read_json
from kellytec_automation.release.contract import read_manifest
from kellytec_automation.release.finalize_release import finalize_package_release

if __name__ == "__main__":
    root = Path.cwd()
    config = read_json(
        root / ".github/automation/release-kellytec-design-system/config/package.json"
    )
    request = read_json(root / ".automation/package-release/request.json")
    results = {
        name: value["result"] for name, value in json.loads(os.environ["RELEASE_NEEDS"]).items()
    }
    finalize_package_release(
        read_manifest(request["manifest"]), request["tag"], results, registry=config["registry"]
    )
