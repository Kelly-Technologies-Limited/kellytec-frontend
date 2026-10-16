"""Redeliver formal-release notifications independently of publication retries."""

import os
from pathlib import Path

from kellytec_automation.common.io.library.local_files import read_json
from kellytec_automation.release.notify_consumers import notify_consumers
from kellytec_automation.release.verify_release import verify_release

if __name__ == "__main__":
    root = Path.cwd()
    config = read_json(
        root / ".github/automation/release-kellytec-design-system/config/package.json"
    )
    manifest = verify_release(
        config["repository"], os.environ["RELEASE_TAG"], product=config["product"]
    )
    notify_consumers(
        manifest, os.environ["RELEASE_TAG"], read_json(root / config["consumers"])["consumers"]
    )
