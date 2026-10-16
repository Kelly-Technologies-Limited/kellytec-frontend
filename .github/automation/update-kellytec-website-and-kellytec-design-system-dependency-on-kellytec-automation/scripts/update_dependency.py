"""Publish a prepared dependency PR without executing the upgrade branch."""

import os
from pathlib import Path

from kellytec_automation.common.adapter.github.context import event_payload, output
from kellytec_automation.common.dependencies.read_declarations import (
    dependency_declaration,
)
from kellytec_automation.common.dependencies.update_dependency_pull_request import (
    update_dependency_pull_request,
)
from kellytec_automation.common.io.library.local_files import read_json
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
    request = read_json(root / ".automation/dependency-request.json")
    os.environ["GH_TOKEN"] = os.environ["DEPENDENCY_WRITE_TOKEN"]
    result = update_dependency_pull_request(
        root,
        root / ".automation/dependency-update",
        repository=os.environ["GITHUB_REPOSITORY"],
        dependency=dependency,
        target=request["target"],
        config=dependency_declaration(root, dependency).get("update", {}),
    )
    output("status", result["status"])
    if result.get("url"):
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as stream:
            stream.write(result["url"] + "\n")
