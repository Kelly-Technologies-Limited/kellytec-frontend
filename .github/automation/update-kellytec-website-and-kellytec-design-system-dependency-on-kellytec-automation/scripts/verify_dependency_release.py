"""Verify the declared release before preparing a dependency upgrade."""

from pathlib import Path

from kellytec_automation.common.adapter.github.context import event_payload
from kellytec_automation.release.verify_dependency_notification import (
    verify_dependency_notification,
)
from kellytec_automation.release.verify_engine_notification import verify_engine_release

if __name__ == "__main__":
    root = Path.cwd()
    dependency = "automation"
    if dependency == "engine":
        verify_engine_release(root)
    else:
        event = event_payload()
        verify_dependency_notification(
            root, dependency, event.get("client_payload") or event["inputs"]
        )
