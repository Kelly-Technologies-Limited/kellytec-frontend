"""Prepare dependency files with read-only credentials and retain their exact base."""

import importlib.util
import os
from pathlib import Path

from kellytec_automation.common.adapter.github.context import output
from kellytec_automation.common.dependencies.read_declarations import (
    dependency_declaration,
)
from kellytec_automation.common.dependencies.update_dependency_pull_request import (
    prepare_update,
)
from kellytec_automation.common.io.library.local_files import read_json

if __name__ == "__main__":
    root = Path.cwd()
    dependency = "automation"
    declaration = dependency_declaration(root, dependency)
    config = declaration.get("update", {})
    request = read_json(root / ".automation/dependency-request.json")
    module = None
    if config.get("generator"):
        specification = importlib.util.spec_from_file_location(
            "repository_dependency_generation", root / config["generator"]
        )
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)

    def generate() -> None:
        """Run the repository-owned generator loaded from the trusted checkout."""
        if module is not None:
            module.generate(root)

    result = prepare_update(
        root,
        repository=os.environ["GITHUB_REPOSITORY"],
        dependency=dependency,
        target=request["target"],
        config=config,
        generate=generate,
    )
    output("status", result["status"])
